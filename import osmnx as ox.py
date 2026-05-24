import osmnx as ox

G = ox.graph_from_place("Floridablanca, Santander, Colombia", network_type="drive")

# Coordenadas de los puntos
lat_origen, lon_origen = 7.070, -73.085
lat_destino, lon_destino = 7.078, -73.089

# 1. Encontrar el nodo más cercano a cada coordenada
nodo_origen = ox.nearest_nodes(G, X=lon_origen, Y=lat_origen)
nodo_destino = ox.nearest_nodes(G, X=lon_destino, Y=lat_destino)

# 2. Calcular la ruta y medir la distancia
ruta = ox.shortest_path(G, orig=nodo_origen, dest=nodo_destino, weight="length")
distancia_metros = sum(ox.utils_graph.get_route_edge_attributes(G, ruta, "length"))

print(f"Distancia entre las coordenadas: {distancia_metros} metros")

grafos = []
    for municipio in CIUDADES:
        try:
            print(f"\n[+] Descargando el mapa de: {municipio.split(",")[0]}")
            G = ox.graph_from_place(municipio, network_type="drive")
            grafos.append(G)
            print("[+] El mapa se descargó correctamente")
            
        except ValueError:
            print("\n[-] Hubo un error")
        
    if len(grafos) > 1:
        mapa = grafos[0]
        for g in grafos[1:]:
            mapa = nx.compose(mapa, g)
    else:
        print("\n[-] El grafo no se descargó correctamente")
        
        
km_recorridos = 0
            nodos_sin_salida = False #para comprobar si hay nodos sin salida
        
vecinos = list(G.neighbors(nodo_actual)) #lista de nodos cercanos a el nodo de el punto clave
                
                if len(vecinos) == 0: #si la lista de vecinos está vacia, rombpe el bucle y afirma que hay un nodo sin salida
                    nodos_sin_salida = True
                    break
                
                nodo_siguiente = random.choice(vecinos) # se escoge al nodo siguiente aleatoriamente entre la lista de vecinos
                
                distancia_metros = G[nodo_actual][nodo_siguiente][0]["length"] # encuentra la distancia entre el nodo actual y el siguiente
                distancia_km = distancia_metros/1000 #convierte la distancia en metros a kilometroj
                
                nodo_actual = nodo_siguiente #hace que el nodo siguiente sea el actual para inciar el bucle desde ese nodo
                
                bateria_actual -= (carro["consumo"]*distancia_km)/carro["cap_bat"] #le resta porcentaje a la bateria segun la distancia
                km_recorridos += distancia_km # acumula los kilometros recorridos

                nodos_reocrridos += 1 #cuenta cuantos nodos se han recorrido
            
            
            if nodos_sin_salida: #en caso de que hayan nodos sin salida elige un nuevo nodo al azar y lo toma como nodo inicial para volver a empezar
                punto = random.choice(PUNTOS_CLAVE)
                lat_inicio, lon_inicio = punto["lat"], punto["lon"]
                nodo_actual = ox.nearest_nodes(G, lon_inicio, lat_inicio)
                continue
            
lat_inicio, lon_inicio = punto["lat"],punto["lon"] #renombrar las coordenadas
        nodo_actual = ox.nearest_nodes(G, lon_inicio, lat_inicio) #convertir coordenadas en un nodo
        
        try:
                    ruta = nx.shortest_path(G, nodo_actual, nodo_destino, weight="length")
                except nx.NetworkXNoPath:
                    continue