import numpy as np
import pandas as pd
import os
import networkx as nx
import osmnx as ox
from math import sqrt
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from config import LAT_MAX, LAT_MIN, LON_MAX, LON_MIN, PASO, ELECTROLINERAS, ARCHIVO_ESTADISTICAS, SALIDA
import grafo as gf

def celdas():
    celdas = []
        
    lat = LAT_MIN
    while (lat < LAT_MAX):
        lon = LON_MIN
        while (lon < LON_MAX):
            celdas.append({"lat": lat, "lon": lon})
            lon += PASO
        lat += PASO
        
    return celdas

def distanciaeuclidiana(lat1, lon1, lat2, lon2):
    return sqrt((lat1-lat2)**2 + (lon1-lon2)**2)
    

def construir_dataset(G):
    
    ruta = os.path.join(SALIDA, ARCHIVO_ESTADISTICAS)
    
    lista_celdas = celdas()
    
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    
    df = shuffle(df, random_state=42)
    
    coord_recargas = df[["lat_actual", "lon_actual"]].values
    
    coord_nodos = np.array([[d["y"], d["x"]] for _, d in G.nodes(data=True)])
    
    coords_electros = np.array([[e["lat"], e["lon"]] for e in ELECTROLINERAS])
    
    for celda in lista_celdas:
        
        dists = np.sqrt((coord_nodos[:,0] - celda["lat"])**2 + (coord_nodos[:,1] - celda["lon"])**2)
        celda["densidad_urbana"] = np.sum(dists < PASO)
        
        dists = np.sqrt((coord_recargas[:,0] - celda["lat"])**2 + (coord_recargas[:,1] - celda["lon"])**2)
        celda["demanda"] = np.sum(dists < PASO)
    
        dists_electros = np.sqrt((coords_electros[:,0] - celda["lat"])**2 + (coords_electros[:,1] - celda["lon"])**2)
        celda["dist_electrolinera"] = np.min(dists_electros)
        
    
    return pd.DataFrame(lista_celdas)

#G = gf.obtener_mapa()
#construir_dataset(G)
def clasificar(d):
    if d == 0:
        return 0  
    elif d <= 5:
        return 1  
    elif d <= 15:
        return 2   
    else:
        return 3  

def entrenar_modelo(G):
    
    df = construir_dataset(G)
    
    df = df[df["densidad_urbana"] >= 5]   
    print(f"Celdas urbanas para entrenar: {len(df)}")
    
    df["categoria"] = df["demanda"].apply(clasificar)
    
    X = df[["lat", "lon", "densidad_urbana", "dist_electrolinera"]]
    y = df["categoria"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(X_train, y_train)
    
    score = modelo.score(X_test, y_test)
    print(f"Precisión del modelo: {round(score*100, 2)}%")
    
    print(df["densidad_urbana"].describe())
    print(df["densidad_urbana"].value_counts().head(20))
    
    return modelo, df

def predecir_electrolineras(G,modelo, df, n_electros=4, dist_min=0.02):
    
    X = df[["lat", "lon", "densidad_urbana", "dist_electrolinera"]]
    df["prediccion"] = modelo.predict(X) # crea una nueva columna llamada predicción, y predice en base a los features de X
    
    df_candi = df[df["dist_electrolinera"] > dist_min].copy() # crea una copia del df y lo filtra por electrolineras que estan separadas a mas de 20 metros
    
    df_candi = df_candi.sort_values("prediccion", ascending=False) #organiza de mayor a menor demanda
    
    sugerencias = []
    for _, fila in df_candi.iterrows():
        demaciado_cerca = False
        lat_ajustada, lon_ajustada = ajustar_a_via(G, fila["lat"], fila["lon"])
        fila = fila.copy()
        fila["lat"] = lat_ajustada
        fila["lon"] = lon_ajustada
        
        for s in sugerencias:
            dist = distanciaeuclidiana(fila["lat"], fila["lon"], s["lat"], s["lon"])
            
            if dist < dist_min:
                demaciado_cerca = True
                break
    
        if not demaciado_cerca:
            
            sugerencias.append(fila)
            
        if (len(sugerencias) == n_electros):
            break
    
    print("\n" + "="*60)
    print("UBICACIONES SUGERIDAS PARA NUEVAS ELECTROLINERAS")
    print("="*60)
    for i, s in enumerate(sugerencias):
        print(f"\n  Sugerencia {i+1}:")
        print(f"  Lat: {round(s['lat'], 6)}, Lon: {round(s['lon'], 6)}")
        print(f"  Densidad urbana: {int(s['densidad_urbana'])}")
        print(f"  Demanda estimada: {'Alta' if s['prediccion']==3 else 'Media' if s['prediccion']==2 else 'Baja'}")
        print(f"  Distancia a electrolinera más cercana: {round(s['dist_electrolinera']*111, 2)} km")
    
    
    return sugerencias

def ajustar_a_via(G, lat, lon):
    nodo = ox.nearest_nodes(G, lon, lat)
    datos = G.nodes[nodo]
    return datos["y"], datos["x"]