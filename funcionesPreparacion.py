import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import folium
import random


CIUDADES = [
    "Bucaramanga, Santander, Colombia",
    "Floridablanca, Santander, Colombia",
    "Girón, Santander, Colombia",
    "Piedecuesta, Santander, Colombia"
]

TIPO = "drive"
SALIDA = "amb"
PUNTOS_CLAVE = []
ELECTROLINERAS = []
CARROS = []

os.makedirs(SALIDA, exist_ok=True)


def puntosClave(nombre, lat, lon):
    PUNTOS_CLAVE.append({
        "id": len(PUNTOS_CLAVE) + 1,
        "nombre": nombre,
        "lat": lat,
        "lon": lon
    })

def electrolineras(nombre, lat, lon):
    ELECTROLINERAS.append({
        "id": len(ELECTROLINERAS) + 1,
        "nombre": nombre,
        "lat": lat,
        "lon": lon
    })

def infoCarro(modelo, cBateria, autonomia, potencia):
    CARROS.append({
        "id": len(CARROS) + 1,
        "modelo": modelo,
        "cbateria": cBateria,
        "autonomia": autonomia,
        "potencia": potencia
    })

def guardar(df, ruta):
    df.to_csv(ruta, index=False, encoding="utf-8-sig")


puntosClave("UIS Campus Central",                       7.138910870846234,  -73.12032665780893)
puntosClave("UIS Campus Florida",                       7.061655811364763,  -73.08857057324246)
puntosClave("UIS Parque Tecnológico Guatiguará",        6.994784145580453,  -73.06667862587386)
puntosClave("UIS Campus Bucarica (Centro)",             7.12103758498896,   -73.12316849078937)
puntosClave("CENFER",                                   7.0825389469325275, -73.15430831704738)
puntosClave("UNAB",                                     7.117167340341574,  -73.10527508962832)
puntosClave("UTS (Unidades Tecnológicas de Santander)", 7.105157239184978,  -73.12385424317661)
puntosClave("Universidad Pontificia Bolivariana UPB",   7.03935832884894,   -73.07256052223526)
puntosClave("PTAR Río Frío",                            7.065755983770025,  -73.12805114126374)
puntosClave("Sede Recreacional Catay",                  6.976343071508123,  -73.04130608532574)

electrolineras("Homecenter",                                7.115794947043329, -73.12049190407198)
electrolineras("Centro Comercial Quinta Etapa",             7.115473864260488, -73.10771498564486)
electrolineras("Centro Comercial Cacique",                  7.099383171372943, -73.10738728564714)
electrolineras("Centro Comercial Canaveral",                7.070722605372017, -73.10545322620052)
electrolineras("Estacion de Servicio Terpel de Piedecuesta",6.998348410998912, -73.05270638323637)
electrolineras("Éxito de la Rosita",                        7.113534997127967, -73.12309979445544)
electrolineras("Centro Comercial la Florida",               7.070730036568059, -73.10553799907328)
electrolineras("Promotores del Oriente (vía a Girón)",      7.085743648912543, -73.16471385719439)

infoCarro("BYD SEAL 82.5 kWh RWD Design",   84.0, 455, 172)
infoCarro("BYD DOLPHIN SURF 30 kWh Active", 32.0, 190, 158)

dfp = pd.DataFrame(PUNTOS_CLAVE)
dfe = pd.DataFrame(ELECTROLINERAS)
dfc = pd.DataFrame(CARROS)


def descargarMapa():
    print("\nDescargando mapa... \n")
    grafos = []
    for ciudad in CIUDADES:
        try:
            G = ox.graph_from_place(ciudad, network_type=TIPO)
            grafos.append(G)
            print(f"[+] Grafo de {ciudad.split(',')[0]} descargado con exito")
        except ValueError:
            print("[-] Hubo un error al descargar el grafo ")

    if len(grafos) > 1:
        grafoCombinado = grafos[0]
        for g in grafos[1:]:
            grafoCombinado = nx.compose(grafoCombinado, g)
    else:
        print("Solo se descargó un grafo correctamente... ")
        grafoCombinado = grafos[0]

    return grafoCombinado

def guardarMapa(G):
    print("\n[+] Guardando mapa...")
    ruta = os.path.join(SALIDA, "mapa.graphml")
    ox.save_graphml(G, filepath=ruta)
    print(f"[+] Mapa guardado con exito como {ruta}")

def cargarMapa(ruta):
    print("[+] Cargando mapa...")
    G = ox.load_graphml(ruta)
    print("[+] Mapa cargado")
    return G

def cargarDf(ruta):
    print(f"[+] Cargando {ruta.split('/')[1]}")
    df = pd.read_csv(ruta)
    print(f"[+] {ruta.split('/')[1]} Cargado con exito")
    return df

def nodosCerca(G, puntos):
    reg = []
    for i, punto in puntos.iterrows():
        nodoId, dist = ox.nearest_nodes(
            G,
            X=punto["lon"],
            Y=punto["lat"],
            return_dist=True
        )
        datosNodo = G.nodes[nodoId]
        reg.append({
            "id": i,
            "nombre": punto["nombre"],
            "lat_original": punto["lat"],
            "lon_original": punto["lon"],
            "nodo_red": nodoId,
            "lat_nodo": datosNodo["y"],
            "lon_nodo": datosNodo["x"],
            "dist_al_nodo_m": round(dist, 2)
        })
    return pd.DataFrame(reg)

def cargaDescarga():
    archivosSalida = [
        ["puntosclave.csv",    dfp],
        ["electrolineras.csv", dfe],
        ["carros.csv",         dfc]
    ]

    print("\nArchivos de ubicaciones .csv:\n")
    dfCargados = []
    for nombre, dfLocal in archivosSalida:
        ruta = os.path.join(SALIDA, nombre)
        if os.path.exists(ruta):
            print(f"\nYa existe el archivo {nombre}")
            carga = cargarDf(ruta)
            dfCargados.append(carga)
        else:
            guardar(dfLocal, ruta)
            print(f"[+]{nombre} Guardado con exito")
            dfCargados.append(dfLocal)

    rutaMapa = os.path.join(SALIDA, "mapa.graphml")
    if os.path.exists(rutaMapa):
        print(f"\nYa existe el archivo {rutaMapa.split('/')[1]}")
        G = cargarMapa(rutaMapa)
    else:
        G = descargarMapa()
        guardarMapa(G)

    dfCombinado = pd.concat(dfCargados[:-1], ignore_index=True)
    dfCombinado["id"] = range(1, len(dfCombinado) + 1)

    return [G, dfCargados, dfCombinado]


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
    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    print("\n[+] mapa guardado con exito ")

def verMejor(df, ruta):
    centroLat = df["lat_original"].mean()
    centroLon = df["lon_original"].mean()

    m = folium.Map(
        location=[centroLat, centroLon],
        zoom_start=12,
        tiles="CartoDB dark_matter"
    )

    coloresFolium = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "cadetblue", "darkgreen", "pink", "lightblue",
    ]

    print("\nGenerando mapa interactivo")
    for _, fila in df.iterrows():
        color = coloresFolium[(fila["id"] - 1) % len(coloresFolium)]
        popupHtml = f"""
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
            popup=folium.Popup(popupHtml, max_width=280),
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
                [fila["lat_nodo"], fila["lon_nodo"]],
            ],
            color="white",
            weight=1.5,
            dash_array="5",
            opacity=0.6,
        ).add_to(m)

    m.save(ruta)
    print(f"Mapa interactivo guardado como {ruta.split('/')[1]}")

def cargarMapaInteractivo(df, ruta):
    if os.path.exists(ruta):
        print("\n[+] Ya existe el mapa interactivo")
    else:
        ruta = os.path.join(SALIDA, "mapaInteractivo.html")
        verMejor(df, ruta)


def distancia(G, a, b):
    try:
        d = nx.shortest_path_length(G, a, b, weight="length")
        return d / 1000.0
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def electroCercana(G, nActual, dfElectro):
    mejor = None
    mejorDist = float("inf")

    for i, electro in dfElectro.iterrows():
        nodoE = electro["nodo_red"]
        dist = distancia(G, nActual, nodoE)
        if dist is not None and dist < mejorDist:
            mejorDist = dist
            mejor = electro

    if mejor is None:
        return None

    return {
        "electro_id": mejor.name,
        "electro_nombre": mejor["nombre"],
        "electro_nodo": mejor["nodo_red"],
        "electro_lat": mejor["lat_original"],
        "electro_lon": mejor["lon_original"],
        "dist_electro_km": round(mejorDist, 4),
    }

def simulacion(n, dfPuntos, dfElectro, dfCarros, G, umbralPct=20.0):
    registros = []
    descartados = 0
    idsPuntos = list(range(len(dfPuntos)))

    vehiculos = []
    for _, carro in dfCarros.iterrows():
        vehiculos.append({
            "modelo": carro["modelo"],
            "autonomia_km": float(carro["autonomia"]),
            "bateria_actual": 100.0,
            "origen_id": random.choice(idsPuntos),
        })

    eventosPorVehiculo = {v["modelo"]: 0 for v in vehiculos}
    totalObjetivo = n * len(vehiculos)

    print(f"\n── Simulando {n:,} eventos con {len(vehiculos)} vehículos ──")
    for v in vehiculos:
        print(f"   {v['modelo']} — {v['autonomia_km']} km")

    viajeId = 0
    eventoId = 0

    while sum(eventosPorVehiculo.values()) < totalObjetivo:
        for v in vehiculos:
            if eventosPorVehiculo[v["modelo"]] >= n:
                continue

            origenId = v["origen_id"]
            destinoId = random.choice([i for i in idsPuntos if i != origenId])

            nodoOrigen = dfPuntos.iloc[origenId]["nodo_red"]
            nodoDestino = dfPuntos.iloc[destinoId]["nodo_red"]

            try:
                ruta = nx.shortest_path(G, nodoOrigen, nodoDestino, weight="length")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                descartados += 1
                v["origen_id"] = random.choice(idsPuntos)
                continue

            viajeId += 1
            eventoEnViaje = False

            for i in range(len(ruta) - 1):
                nodoA = ruta[i]
                nodoB = ruta[i + 1]

                datosArista = G.get_edge_data(nodoA, nodoB)
                if datosArista is None:
                    continue

                if isinstance(datosArista, dict) and 0 in datosArista:
                    segM = datosArista[0].get("length", 0)
                else:
                    segM = list(datosArista.values())[0].get("length", 0)

                segKm = segM / 1000.0
                consumo = (segKm / v["autonomia_km"]) * 100.0
                v["bateria_actual"] -= consumo

                if v["bateria_actual"] <= umbralPct and not eventoEnViaje:
                    eventoEnViaje = True

                    datosNodo = G.nodes[nodoB]
                    resultado = electroCercana(G, nodoB, dfElectro)

                    if resultado is None:
                        descartados += 1
                        v["bateria_actual"] = 100.0
                        break

                    kmRestantes = (v["bateria_actual"] / 100.0) * v["autonomia_km"]

                    if resultado["dist_electro_km"] > kmRestantes:
                        descartados += 1
                        v["bateria_actual"] = 100.0
                        break

                    eventoId += 1
                    eventosPorVehiculo[v["modelo"]] += 1
                    registros.append({
                        "evento_id": eventoId,
                        "viaje_id": viajeId,
                        "carro_modelo": v["modelo"],
                        "autonomia_km": v["autonomia_km"],
                        "origen_nombre": dfPuntos.iloc[origenId]["nombre"],
                        "destino_nombre": dfPuntos.iloc[destinoId]["nombre"],
                        "evento_nodo": nodoB,
                        "evento_lat": round(datosNodo["y"], 6),
                        "evento_lon": round(datosNodo["x"], 6),
                        "bateria_pct": round(v["bateria_actual"], 2),
                        "km_restantes": float(f"{kmRestantes:.4f}"),
                        **resultado,
                    })

                    print(
                        f"  [{sum(eventosPorVehiculo.values())}/{totalObjetivo}] "
                        f"{v['modelo'][:15]}: {eventosPorVehiculo[v['modelo']]}/{n}",
                        flush=True
                    )

                    v["bateria_actual"] = 100.0
                    v["origen_id"] = destinoId

                    if eventoId % 100 == 0:
                        print(f"  [{eventoId:>{len(str(n))}}] eventos | viajes: {viajeId:,}")

                    break

            else:
                v["origen_id"] = destinoId

    print(f"\n  ✅ Simulación completa")
    print(f"     Eventos registrados : {len(registros):,}")
    print(f"     Viajes totales      : {viajeId:,}")
    print(f"     Descartados         : {descartados:,}")

    return pd.DataFrame(registros)

def filename(name, ext):
    nombreArchivo = f"{name}.{ext}"
    salida = os.path.join(SALIDA, nombreArchivo)
    if not os.path.exists(salida):
        return salida

    n = 1
    while True:
        nombreArchivo = f"{name}({n}).{ext}"
        salida = os.path.join(SALIDA, nombreArchivo)
        if not os.path.exists(salida):
            return salida
        n += 1
