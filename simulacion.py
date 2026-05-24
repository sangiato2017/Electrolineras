import osmnx as ox
import networkx as nx
import random
import os
import pandas as pd

from config import BATERIA, PUNTOS_CLAVE, ELECTROLINERAS, CARROS, SALIDA, MAPA_CIUDAD, ARCHIVO_ESTADISTICAS

def simulacion(G):
    n = entero_positivo("Ingrese el numero de recorridos que desea simular: ")
    estadisticas = {}
    registros = []
    
    nodos_puntos_clae = [ox.nearest_nodes(G,p["lon"],p["lat"]) for p in PUNTOS_CLAVE]
    nodos_electrolinerah = [(ox.nearest_nodes(G, e["lon"], e["lat"]), e) for e in ELECTROLINERAS]
    
    rutas_calculadas = {}
    for origen  in nodos_puntos_clae:
        for destino in nodos_puntos_clae:
            if origen != destino:
                try:
                    ruta = nx.shortest_path(G, origen, destino, weight="length")
                    rutas_calculadas[(origen, destino)] = ruta
                except nx.NetworkXNoPath:
                    pass
    
    for i in range(len(CARROS)):
        
        carro = CARROS[i] #selecciona los carros
        modelo = carro["modelo"]
        #un punto clave aleatorio
        
        autonomia = carro["autonomia"]
        bateria_actual = 1.0
        nodos_reocrridos = 0 #contador
        recargas = 0 #contador
        
        print(f"\n[i] Usando el carro: {carro["modelo"]}\n") #aviso para saber cual carro se está usando
        
        nodo_punto_actual = random.choice(nodos_puntos_clae)
        nodo_actual = nodo_punto_actual
        
        
        estadisticas[modelo] = {}
        while (recargas < n): #mientras la s recargas sean menores a n seguirá el bucle
            while (bateria_actual > 0.2):
                
                nodo_destino = random.choice(nodos_puntos_clae)
                ruta = rutas_calculadas.get((nodo_punto_actual, nodo_destino))
                if ruta is None:
                    continue
                
                for idx, nodo_siguiente  in enumerate(ruta[1:]):
                    if bateria_actual < 0.2:
                        break
                    
                    nodo_anterior = ruta[idx]
                    distancia_metros = G[nodo_anterior][nodo_siguiente][0]["length"] # encuentra la distancia entre el nodo actual y el siguiente
                    distancia_km = distancia_metros/1000 #convierte la distancia en metros a kilometroj

                    nodo_actual = nodo_siguiente #hace que el nodo siguiente sea el actual para inciar el bucle desde ese nodo
                    
                    bateria_actual -= (carro["consumo"]*distancia_km)/carro["cap_bat"] #le resta porcentaje a la bateria segun la distancia
                    nodos_reocrridos += 1 #cuenta cuantos nodos se han recorrido
                
                nodo_punto_actual = nodo_destino
            
            print(f"quedan: {round(bateria_actual*100, 2)}% de bateria se recorrieron {nodos_reocrridos} nodos") # imprime el porcentaje final de la bateria
                
            
            
            print("[i] necesita recargar")
            print("Buscando electrolinera mas cercana...")
            
            menor_dist = float("inf")
            electro_masercana = None
            
            for nodo_e, e in nodos_electrolinerah:
                try:
                    dist = nx.shortest_path_length(G, nodo_actual, nodo_e, weight="length")
                    if dist < menor_dist:
                        menor_dist = dist
                        electro_masercana = e
                except nx.NetworkXNoPath:
                    continue  
            
            if electro_masercana is None:
                punto = random.choice(PUNTOS_CLAVE)
                lat_inicio, lon_inicio = punto["lat"], punto["lon"]
                nodo_actual = ox.nearest_nodes(G, lon_inicio, lat_inicio)
                continue
                
                    
            print(f"[i]Recarga en {electro_masercana["nombre"]}\n")
            if bateria_actual < 0:
                bateria_actual = 0.0
                
            datos_nodo = G.nodes[nodo_actual]
            lat_actual = datos_nodo["y"]
            lon_actual = datos_nodo["x"]
            
            registros.append({
                "vehiculo": carro["modelo"],
                "gama": carro["gama"],
                "lat_actual": lat_actual,
                "lon_actual": lon_actual,
                "electrolinera": electro_masercana["nombre"],
                "lat_electrolinera": electro_masercana["lat"],
                "lon_electrolinera": electro_masercana["lon"],
                "distancia_metros": round(menor_dist, 2),
                "bateria_al_recargar": round(bateria_actual, 4),
                "nodos_recorridos": nodos_reocrridos
            })
            
            nombre = electro_masercana["nombre"]
            if nombre in estadisticas[modelo]:
                estadisticas[modelo][nombre] += 1
            else:
                estadisticas[modelo][nombre] = 1
            
            
            bateria_actual = 1.0
            recargas += 1
            
        print(f"Se recargaron {recargas} veces")
        
    for modelo, conteos in estadisticas.items():
        print("="*60)
        print(modelo)
        print("="*60)
        
        for electro, veces in conteos.items():
            print(f"{electro}: {veces} recargas")
                
    
    ruta = os.path.join(SALIDA,ARCHIVO_ESTADISTICAS)
    
    reg = pd.DataFrame(registros)
    reg.to_csv(ruta,index=False ,encoding="utf-8-sig")

def entero_positivo(mensaje):
    "Valida que el numero ingresado sea entero y positivo"
    while True:
        entrada = input(mensaje)
        try:
            num = int(entrada)
            if num > 0:
                return num
            else:
                print("\n[-] Error: el numero debe ser mayor a 0.")
        except ValueError:
            print(f"\n[-] Error: {entrada} no es un numero valido.\n")

#ruta = os.path.join(SALIDA, MAPA_CIUDAD)
#G = ox.load_graphml(ruta)
#simulacion(G)