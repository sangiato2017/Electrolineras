

import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import folium
import random


CIUDADES = [
    "Bucaramanga, Santander, Colombia"  ,
    "Floridablanca, Santander, Colombia",
    "Girón, Santander, Colombia"        ,
    "Piedecuesta, Santander, Colombia"    
]

TIPO = "drive"

SALIDA = "amb"

PUNTOS_CLAVE = []

ELECTROLINERAS = []

CARROS = []

os.makedirs(SALIDA, exist_ok=True)




def puntos_clave(nombre, lat, lon):
    PUNTOS_CLAVE.append({
        "id"    : len   (PUNTOS_CLAVE) + 1,
        "nombre": nombre,
        "lat"   : lat   ,
        "lon"   : lon
    })
    
def electrolineras(nombre, lat, lon):
    ELECTROLINERAS.append({
        "id"    : len   (ELECTROLINERAS) + 1,
        "nombre": nombre,
        "lat"   : lat   ,
        "lon"   : lon
    })
    
def info_carro(modelo, Cbatery, autonomia, potencia):
    CARROS.append({
        "id"       : len      (CARROS) + 1,
        "modelo"   : modelo   ,
        "cbateria" : Cbatery  ,
        "autonomia": autonomia,
        "potencia" : potencia
    })

def guardar(df, ruta):
    
    df.to_csv(ruta, index=False, encoding="utf-8-sig")

punto1  = puntos_clave("UIS Campus Central"                      , 7.138910870846234 , -73.12032665780893)
punto2  = puntos_clave("UIS Campus Florida"                      , 7.061655811364763 , -73.08857057324246)
punto3  = puntos_clave("UIS Parque Tecnológico Guatiguará"       , 6.994784145580453 , -73.06667862587386)
punto4  = puntos_clave("UIS Campus Bucarica (Centro)"            , 7.12103758498896  , -73.12316849078937)
punto5  = puntos_clave("CENFER"                                  , 7.0825389469325275, -73.15430831704738)
punto6  = puntos_clave("UNAB"                                    , 7.117167340341574 , -73.10527508962832)
punto7  = puntos_clave("UTS (Unidades Tecnológicas de Santander)", 7.105157239184978 , -73.12385424317661)
punto8  = puntos_clave("Universidad Pontificia Bolivariana UPB"  , 7.03935832884894  , -73.07256052223526)
punto9  = puntos_clave("PTAR Río Frío"                           , 7.065755983770025 , -73.12805114126374)
punto10 = puntos_clave("Sede Recreacional Catay"                 , 6.976343071508123 , -73.04130608532574)

electro1 = electrolineras("Homecenter"                                , 7.115794947043329, -73.12049190407198)
electro2 = electrolineras("Centro Comercial Quinta Etapa"             , 7.115473864260488, -73.10771498564486)
electro3 = electrolineras("Centro Comercial Cacique"                  , 7.099383171372943, -73.10738728564714)
electro4 = electrolineras("Centro Comercial Canaveral"                , 7.070722605372017, -73.10545322620052)
electro5 = electrolineras("Estacion de Servicio Terpel de Piedecuesta", 6.998348410998912, -73.05270638323637)
electro6 = electrolineras("Éxito de la Rosita"                        , 7.113534997127967, -73.12309979445544)
electro7 = electrolineras("Centro Comercial la Florida"               , 7.070730036568059, -73.10553799907328)
electro8 = electrolineras("Promotores del Oriente (vía a Girón)"      , 7.085743648912543, -73.16471385719439)

carro1 = info_carro("BYD SEAL 82.5 kWh RWD Design"  , 84.0, 455, 172)
carro2 = info_carro("BYD DOLPHIN SURF 30 kWh Active", 32.0, 190, 158)

dfp = pd.DataFrame(PUNTOS_CLAVE)

dfe = pd.DataFrame(ELECTROLINERAS)

dfc = pd.DataFrame(CARROS)







def desc_mapa():
    
    print("\nDescargando mapa... \n")
    
    grafos = []
    for i in CIUDADES:
        
        try:
            G = ox.graph_from_place(i, network_type=TIPO)
            grafos.append(G)
            print(f"[+] Grafo de {i.split(",")[0]} descargado con exito")
            
        except ValueError:
            print("[-] Hubo un error al descargar el grafo ")
            
    if (len(grafos) > 1):
        
        Gmix = grafos[0]
        for i in grafos[1:]:
            Gmix = nx.compose(Gmix, i)
            
    else:
        
        print("Solo se descargó un grafo correctamente... ")
        Gmix = grafos[0]
    
    return Gmix

def guar_mapa(G):
    
    print("\n[+] Guardando mapa...")
    
    ruta = os.path.join(SALIDA, "mapa.graphml")
    ox.save_graphml(G, filepath=ruta)
    
    print(f"[+] Mapa guardado con exito como {ruta}")

def cargar_mapa(ruta):
    
    print("[+] Cargando mapa...")
    G = ox.load_graphml(ruta)
    print("[+] Mapa cargado")
    
    return G

def cargadf (ruta):
    
    print(f"[+] Cargando {ruta.split("/")[1]}")
    df = pd.read_csv(ruta)
    print(f"[+] {ruta.split("/")[1]} Cargado con exito")
    
    return df
    
def nodos_cerca(G, puntos):
    
    reg = []
    for i, j in puntos.iterrows():
        
        nodid, dist = ox.nearest_nodes(
            G,
            X = j["lon"],
            Y = j["lat"],
            return_dist=True
            
        )
        
        dnodo = G.nodes[nodid]
        reg.append({
            "id"             : i,
            "nombre"         : j["nombre"],
            "lat_original"   : j["lat"],
            "lon_original"   : j["lon"],
            "nodo_red"       : nodid,
            "lat_nodo"       : dnodo["y"],
            "lon_nodo"       : dnodo["x"],
            "dist_al_nodo_m" : round(dist, 2)
        })
    
    dfreg = pd.DataFrame(reg)
    return dfreg

def carga_descarga():
    
    ARCHIVOS_SALIDA = [
    ["puntosclave.csv"   , dfp],
    ["electrolineras.csv", dfe],
    ["carros.csv"        , dfc]
    ]

    print("\nArchivos de ubicacioes .csv:\n")
    dfCargados =[]
    for i, j in ARCHIVOS_SALIDA:
        
        ruta = os.path.join(SALIDA, i)
        
        if os.path.exists(ruta):
            
            print(f"\nYa existe el archivo {i}")
            ruta = os.path.join(SALIDA, i)
            carga = cargadf(ruta)
            dfCargados.append(carga)
            
        else:
            
            guardar(j, ruta)
            print(f"[+]{i} Guardado con exito")
            dfCargados.append(j)

    ruta = os.path.join(SALIDA, "mapa.graphml")
    if os.path.exists(ruta):
        
        print(f"\nYa existe el archivo {ruta.split("/")[1]}")
        G = cargar_mapa(ruta)
        
    else:
        
        G = desc_mapa()
        guar_mapa(G)
        


    dfCombinado = pd.concat(dfCargados[:-1], ignore_index=True)

    dfCombinado["id"] = range(1, len(dfCombinado) + 1)


    listasalida = [G, dfCargados, dfCombinado]
    
    return listasalida


def ver(G):
    
    print("\nCargando visualización...")
    
    fig, ax = ox.plot_graph(
        G,
        figsize=(14, 14),
        node_size=0,
        edge_color="#E8C547",
        edge_linewidth=0.4,
        edge_alpha=1,
        bgcolor="#1a1a2e",
        show=False,
        close=False
        
    )
    
    ax.set_title(
        "Red Vial del Area Metropolitana de Bucaramanga",
        fontsize=16,
        color="white",
        pad=15
    )
    
    
    ruta = os.path.join(SALIDA, "mapa.png")
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="#1a1a2e" )
    plt.close()
    
    print("\n[+] mapa guardado con exito ")
    
    
def ver_mejor(df, ruta):
    
    centro_lat = df["lat_original"].mean()
    centro_lon = df["lon_original"].mean()
    
    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter"
    )
    
    colores_folium = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "cadetblue", "darkgreen", "pink", "lightblue",
    ]
    
    print("\nGenerando mapa interactivo")
    for _, fila in df.iterrows():
        
        color = colores_folium[(fila["id"] - 1) % len(colores_folium)]

        popup_html = f"""
        <div style='font-family:sans-serif; min-width:200px'>
            <b style='font-size:14px'>{fila['id']}. {fila['nombre']}</b><br><br>
            <b>Coordenadas originales:</b><br>
            Lat: {fila['lat_original']} | Lon: {fila['lon_original']}<br><br>
            <b>Nodo más cercano en la red:</b><br>
            ID: {fila['nodo_red']}<br>
            Lat: {round(fila['lat_nodo'], 6)} | Lon: {round(fila['lon_nodo'], 6)}<br><br>
            <b>Distancia al nodo:</b> {fila['dist_al_nodo_m']} m
        </div>
        """
        
        folium.Marker(
            location=[fila["lat_original"], fila["lon_original"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{fila['id']}. {fila['nombre']}",
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)
        
        folium.CircleMarker(
            location=[fila["lat_nodo"], fila["lon_nodo"]],
            radius=5,
            color="white",
            fill=True,
            fill_color="white",
            fill_opacity=0.8,
            tooltip=f"Nodo de red #{fila['nodo_red']}",
        ).add_to(m)
        
        folium.PolyLine(
            locations=[
                [fila["lat_original"], fila["lon_original"]],
                [fila["lat_nodo"],     fila["lon_nodo"]],
            ],
            color="white",
            weight=1.5,
            dash_array="5",
            opacity=0.6,
        ).add_to(m)
        
    m.save(ruta)
    
    print(f"Mapa interactivo guardado como {ruta.split("/")[1]}")

def carga_mapaI(df, ruta):
    
    
    if (os.path.exists(ruta)):
        
        print("\n[+] Ya existe el mapa interactivo")
        
    else:
        ruta = os.path.join(SALIDA, "mapaInteractivo.html")
        ver_mejor(df, ruta)
        

#listaS = carga_descarga()
#en la listaS[]: 0 = grafo, 1 = lista de dataframes ubicaciones y carros, 2 = dataframes combinados sin los carros

#df_puntos_engeneral = nodos_cerca(listaS[0], listaS[2])
#df_puntos_engeneral["id"] = range(1, len(df_puntos_engeneral) + 1)

#ruta = os.path.join(SALIDA, "mapaInteractivo.html")
#carga_mapaI(df_puntos_engeneral, ruta)

#df_puntos_engeneral.style.hide(axis="index")

def distancia(G, a, b):
    try:
        d = nx.shortest_path_length(G, a, b, weight="length")
        return d / 1000.0
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def electrocercana(G, nActual, df_electro):
    
    mejor = None
    mejor_dist = float("inf")
    
    for i, j in df_electro.iterrows():
        
        
        nodo_e = j["nodo_red"]
        dist = distancia(G, nActual, nodo_e)
        
        if dist is not None and dist < mejor_dist:
            
            mejor_dist = dist
            mejor = j
            
    if mejor is None:
        return None
    
    diccio = {
        "electro_id"     : mejor.name,          
        "electro_nombre" : mejor["nombre"],
        "electro_nodo"   : mejor["nodo_red"],
        "electro_lat"    : mejor["lat_original"],
        "electro_lon"    : mejor["lon_original"],
        "dist_electro_km": round(mejor_dist, 4),
    }
    
    return diccio

def simulacion(n, df_puntos, df_electro, df_carros, G, umbral_pct=20.0):


    registros   = []
    descartados = 0
    ids_puntos  = list(range(len(df_puntos)))

    # ── Inicializar todos los vehículos ───────────────────
    vehiculos = []

    for _, carro in df_carros.iterrows():
        vehiculos.append({
            "modelo"        : carro["modelo"],
            "autonomia_km"  : float(carro["autonomia"]),
            "bateria_actual": 100.0,
            "origen_id"     : random.choice(ids_puntos),
        })

    eventos_por_vehiculo = {v["modelo"]: 0 for v in vehiculos}
    total_objetivo = n * len(vehiculos) 

    print(f"\n── Simulando {n:,} eventos con {len(vehiculos)} vehículos ──")
    for v in vehiculos:
        print(f"   {v['modelo']} — {v['autonomia_km']} km")
        

    viaje_id  = 0
    evento_id = 0

    while sum(eventos_por_vehiculo.values()) < total_objetivo:

        
        # ── Cada vehículo hace un viaje ───────────────────
        for v in vehiculos:

            if eventos_por_vehiculo[v["modelo"]] >= n:
                continue

            origen_id  = v["origen_id"]
            destino_id = random.choice([i for i in ids_puntos if i != origen_id])

            nodo_origen  = df_puntos.iloc[origen_id]["nodo_red"]
            nodo_destino = df_puntos.iloc[destino_id]["nodo_red"]

            try:
                ruta = nx.shortest_path(G, nodo_origen, nodo_destino, weight="length")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                descartados += 1
                v["origen_id"] = random.choice(ids_puntos)
                continue

            viaje_id += 1
            evento_en_viaje = False

            for i in range(len(ruta) - 1):
                nodo_a = ruta[i]
                nodo_b = ruta[i + 1]

                datos_arista = G.get_edge_data(nodo_a, nodo_b)
                if datos_arista is None:
                    continue

                if isinstance(datos_arista, dict) and 0 in datos_arista:
                    seg_m = datos_arista[0].get("length", 0)
                else:
                    seg_m = list(datos_arista.values())[0].get("length", 0)

                seg_km            = seg_m / 1000.0
                consumo           = (seg_km / v["autonomia_km"]) * 100.0
                v["bateria_actual"] -= consumo

                if v["bateria_actual"] <= umbral_pct and not evento_en_viaje:
                    evento_en_viaje = True

                    datos_nodo = G.nodes[nodo_b]
                    resultado  = electrocercana(G, nodo_b, df_electro)
                    

                    if resultado is None:
                        descartados += 1
                        v["bateria_actual"] = 100.0
                        break

                    km_restantes = (v["bateria_actual"] / 100.0) * v["autonomia_km"]
                    if resultado["dist_electro_km"] > km_restantes:
                        descartados += 1
                        v["bateria_actual"] = 100.0
                        break
                    
                    evento_id += 1
                    eventos_por_vehiculo[v["modelo"]] += 1 
                    registros.append({
                        "evento_id"     : evento_id,
                        "viaje_id"      : viaje_id,
                        "carro_modelo"  : v["modelo"],
                        "autonomia_km"  : v["autonomia_km"],
                        "origen_nombre" : df_puntos.iloc[origen_id]["nombre"],
                        "destino_nombre": df_puntos.iloc[destino_id]["nombre"],
                        "evento_nodo"   : nodo_b,
                        "evento_lat"    : round(datos_nodo["y"], 6),
                        "evento_lon"    : round(datos_nodo["x"], 6),
                        "bateria_pct"   : round(v["bateria_actual"], 2),
                        "km_restantes"  : round(km_restantes, 4),
                        **resultado,
                    })
                    
                    print(f"  [{sum(eventos_por_vehiculo.values())}/{total_objetivo}] "f"{v['modelo'][:15]}: {eventos_por_vehiculo[v['modelo']]}/{n}", flush=True)

                    v["bateria_actual"] = 100.0
                    v["origen_id"]      = destino_id

                    if evento_id % 100 == 0:
                        print(f"  [{evento_id:>{len(str(n))}}] eventos | viajes: {viaje_id:,}")

                    break

            else:
                v["origen_id"] = destino_id

    print(f"\n  ✅ Simulación completa")
    print(f"     Eventos registrados : {len(registros):,}")
    print(f"     Viajes totales      : {viaje_id:,}")
    print(f"     Descartados         : {descartados:,}")

    return pd.DataFrame(registros)

def get_filename(name, ext):
    filename = f"{name}.{ext}"
    sal = os.path.join(SALIDA, filename)
    if not os.path.exists(sal):
        return sal
    
    n = 1
    while True:
        filename = f"{name}({n}).{ext}"          
        sal = os.path.join(SALIDA, filename)     
        if not os.path.exists(sal):              
            return sal
        n += 1