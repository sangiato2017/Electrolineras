"""
Ubicar Puntos de Interés en la Red Vial del AMB
================================================
Carga el grafo GraphML y encuentra el nodo más cercano
de la red vial para cada punto de interés.

Requisitos:
    pip install osmnx networkx geopandas matplotlib folium
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import folium
from shapely.geometry import Point


# ──────────────────────────────────────────────
# PUNTOS DE INTERÉS
# Coordenadas obtenidas de OpenStreetMap / Google Maps
# Formato: (latitud, longitud)
# ──────────────────────────────────────────────

PUNTOS_INTERES = {
    1:  {
        "nombre": "UIS Campus Central",
        "lat": 7.138910870846234,
        "lon": -73.12032665780893,
    },
    2:  {
        "nombre": "UIS Campus Florida",
        "lat": 7.061655811364763,
        "lon": -73.08857057324246,
    },
    3:  {
        "nombre": "UIS Parque Tecnológico Guatiguará",
        "lat": 6.994784145580453,
        "lon": -73.06667862587386,
    },
    4:  {
        "nombre": "UIS Campus Bucarica (Centro)",
        "lat": 7.12103758498896,
        "lon": -73.12316849078937,
    },
    5:  {
        "nombre": "CENFER",
        "lat": 7.0825389469325275,
        "lon": -73.15430831704738,
    },
    6:  {
        "nombre": "UNAB",
        "lat": 7.117167340341574,
        "lon": -73.10527508962832,
    },
    7:  {
        "nombre": "UTS (Unidades Tecnológicas de Santander)",
        "lat": 7.105157239184978,
        "lon": -73.12385424317661,
    },
    8:  {
        "nombre": "Universidad Pontificia Bolivariana UPB",
        "lat": 7.03935832884894,
        "lon": -73.07256052223526,
    },
    9:  {
        "nombre": "PTAR Río Frío",
        "lat": 7.065755983770025,
        "lon": -73.12805114126374,
    },
    10: {
        "nombre": "Sede Recreacional Catay",
        "lat": 6.976343071508123,
        "lon": -73.04130608532574,
    },
}


# ──────────────────────────────────────────────
# 1. CARGAR GRAFO
# ──────────────────────────────────────────────

def cargar_grafo(ruta: str):
    print("→ Cargando grafo desde GraphML...")
    G = ox.load_graphml(ruta)
    print(f"  ✓ {G.number_of_nodes():,} nodos  |  {G.number_of_edges():,} aristas\n")
    return G


# ──────────────────────────────────────────────
# 2. ENCONTRAR NODO MÁS CERCANO EN LA RED
# ──────────────────────────────────────────────

def encontrar_nodos_cercanos(G, puntos: dict) -> pd.DataFrame:
    """
    Para cada punto de interés encuentra el nodo más cercano
    en la red vial y calcula la distancia en metros.
    """
    print("── Buscando nodos más cercanos en la red ───────────")

    registros = []
    for idx, info in puntos.items():
        nodo_id, dist = ox.nearest_nodes(
            G,
            X=info["lon"],   # longitud → X
            Y=info["lat"],   # latitud  → Y
            return_dist=True,
        )
        datos_nodo = G.nodes[nodo_id]
        registros.append({
            "id"             : idx,
            "nombre"         : info["nombre"],
            "lat_original"   : info["lat"],
            "lon_original"   : info["lon"],
            "nodo_red"       : nodo_id,
            "lat_nodo"       : datos_nodo["y"],
            "lon_nodo"       : datos_nodo["x"],
            "dist_al_nodo_m" : round(dist, 2),
        })

        print(f"  [{idx:>2}] {info['nombre']}")
        print(f"        Nodo ID : {nodo_id}")
        print(f"        Distancia al nodo más cercano: {round(dist, 2)} m\n")

    return pd.DataFrame(registros)


# ──────────────────────────────────────────────
# 3. GUARDAR TABLA CSV
# ──────────────────────────────────────────────

def guardar_csv(df: pd.DataFrame, ruta="puntos_en_red.csv"):
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"  ✓ Tabla guardada → {ruta}")


# ──────────────────────────────────────────────
# 4. MAPA ESTÁTICO (PNG)
# ──────────────────────────────────────────────

def mapa_estatico(G, df: pd.DataFrame, ruta="mapa_puntos.png"):
    print("\n── Generando mapa estático PNG ─────────────────────")

    fig, ax = ox.plot_graph(
        G,
        figsize=(20, 20),
        node_size=0,
        edge_color="#4a90d9",
        edge_linewidth=0.35,
        edge_alpha=0.6,
        bgcolor="#0d1117",
        show=False,
        close=False,
    )

    colores = plt.cm.tab10.colors

    for _, fila in df.iterrows():
        c = colores[(fila["id"] - 1) % 10]

        # Punto original
        ax.scatter(
            fila["lon_original"], fila["lat_original"],
            c=[c], s=180, zorder=5, edgecolors="white", linewidths=0.8,
        )
        # Nodo en la red
        ax.scatter(
            fila["lon_nodo"], fila["lat_nodo"],
            c=[c], s=60, marker="x", zorder=6, linewidths=1.2,
        )
        # Etiqueta
        ax.annotate(
            f"{fila['id']}. {fila['nombre']}",
            xy=(fila["lon_original"], fila["lat_original"]),
            xytext=(6, 6), textcoords="offset points",
            fontsize=6.5, color="white",
            bbox=dict(boxstyle="round,pad=0.2", fc=c, alpha=0.75, ec="none"),
        )

    ax.set_title(
        "Puntos de Interés — Red Vial AMB",
        fontsize=15, color="white", pad=12,
    )

    fig.savefig(ruta, dpi=200, bbox_inches="tight", facecolor="#0d1117")
    plt.close()
    print(f"  ✓ Imagen guardada → {ruta}")


# ──────────────────────────────────────────────
# 5. MAPA INTERACTIVO (HTML con Folium)
# ──────────────────────────────────────────────

def mapa_interactivo(df: pd.DataFrame, ruta="mapa_puntos_interactivo.html"):
    print("\n── Generando mapa interactivo HTML ─────────────────")

    centro_lat = df["lat_original"].mean()
    centro_lon = df["lon_original"].mean()

    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    colores_folium = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "cadetblue", "darkgreen", "pink", "lightblue",
    ]

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

        # Marcador del punto de interés
        folium.Marker(
            location=[fila["lat_original"], fila["lon_original"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{fila['id']}. {fila['nombre']}",
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

        # Marcador del nodo en la red
        folium.CircleMarker(
            location=[fila["lat_nodo"], fila["lon_nodo"]],
            radius=5,
            color="white",
            fill=True,
            fill_color="white",
            fill_opacity=0.8,
            tooltip=f"Nodo de red #{fila['nodo_red']}",
        ).add_to(m)

        # Línea conectando punto original → nodo de red
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
    print(f"  ✓ Mapa HTML guardado → {ruta}")
    print("    Ábrelo en tu navegador para explorar de forma interactiva.")


# ──────────────────────────────────────────────
# 6. EJEMPLO: RUTA ENTRE DOS PUNTOS
# ──────────────────────────────────────────────

def ejemplo_ruta(G, df: pd.DataFrame, origen_id=1, destino_id=6):
    """Calcula la ruta más corta entre dos puntos de interés."""

    print(f"\n── Ruta de ejemplo: [{origen_id}] → [{destino_id}] ──────────────────")

    nodo_origen  = df.loc[df["id"] == origen_id,  "nodo_red"].values[0]
    nodo_destino = df.loc[df["id"] == destino_id, "nodo_red"].values[0]

    nombre_o = df.loc[df["id"] == origen_id,  "nombre"].values[0]
    nombre_d = df.loc[df["id"] == destino_id, "nombre"].values[0]

    try:
        ruta = nx.shortest_path(G, nodo_origen, nodo_destino, weight="length")
        distancia = nx.shortest_path_length(G, nodo_origen, nodo_destino, weight="length")

        print(f"  Origen  : {nombre_o}")
        print(f"  Destino : {nombre_d}")
        print(f"  Nodos en la ruta : {len(ruta)}")
        print(f"  Distancia total  : {round(distancia / 1000, 3)} km")

        # Graficar la ruta
        fig, ax = ox.plot_graph_route(
            G, ruta,
            figsize=(12, 12),
            node_size=0,
            edge_color="#4a90d9",
            edge_linewidth=0.3,
            edge_alpha=0.5,
            route_color="#ff6b6b",
            route_linewidth=3,
            bgcolor="#0d1117",
            show=False,
            close=False,
        )

        ax.set_title(
            f"Ruta: {nombre_o}\n→ {nombre_d}  ({round(distancia/1000, 2)} km)",
            fontsize=11, color="white", pad=10,
        )

        fig.savefig("ruta_ejemplo.png", dpi=180, bbox_inches="tight", facecolor="#0d1117")
        plt.close()
        print("  ✓ Imagen de ruta → ruta_ejemplo.png")

        return ruta

    except nx.NetworkXNoPath:
        print("  ✗ No existe ruta entre estos nodos (red desconectada).")
        return None


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":

    # Ajusta esta ruta si tu archivo está en otro lugar
    RUTA_GRAPHML = "red_vial_ambucaramanga/red_vial_amb.graphml"

    # 1. Cargar grafo
    G = cargar_grafo(RUTA_GRAPHML)

    # 2. Encontrar nodos más cercanos
    df_puntos = encontrar_nodos_cercanos(G, PUNTOS_INTERES)

    # 3. Guardar tabla
    print("\n── Guardando resultados ────────────────────────────")
    guardar_csv(df_puntos, "puntos_en_red.csv")
    print(df_puntos[["id", "nombre", "nodo_red", "dist_al_nodo_m"]].to_string(index=False))

    # 4. Mapa estático
    mapa_estatico(G, df_puntos, "mapa_puntos.png")

    # 5. Mapa interactivo
    mapa_interactivo(df_puntos, "mapa_puntos_interactivo.html")

    # 6. Ejemplo de ruta (UIS Central → UNAB)
    #ejemplo_ruta(G, df_puntos, origen_id=1, destino_id=6)

    print("\n✅ ¡Todo listo!")