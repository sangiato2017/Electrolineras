"""
Red Vial - Área Metropolitana de Bucaramanga
=============================================
Descarga la red vial desde OpenStreetMap usando OSMnx
y la guarda en múltiples formatos para análisis de grafos.

Requisitos:
    pip install osmnx networkx geopandas matplotlib
"""

import os
import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt


# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────

# Municipios del Área Metropolitana de Bucaramanga
MUNICIPIOS = [
    "Bucaramanga, Santander, Colombia",
    "Floridablanca, Santander, Colombia",
    "Girón, Santander, Colombia",
    "Piedecuesta, Santander, Colombia",
]

# Tipo de red vial:
#   "drive"    → carreteras para vehículos (recomendado para rutas)
#   "walk"     → rutas peatonales
#   "bike"     → ciclovías y rutas para bicicleta
#   "all"      → todas las vías
NETWORK_TYPE = "drive"

# Carpeta de salida
OUTPUT_DIR = "red_vial_ambucaramanga"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# 1. DESCARGA DE LA RED VIAL
# ──────────────────────────────────────────────

def descargar_red_vial():
    """Descarga y combina la red vial de todos los municipios del AMB."""

    print("=" * 55)
    print("  Descargando Red Vial - Área Metropolitana de Bucaramanga")
    print("=" * 55)

    grafos = []
    for municipio in MUNICIPIOS:
        print(f"\n→ Descargando: {municipio.split(',')[0]}...")
        try:
            G = ox.graph_from_place(municipio, network_type=NETWORK_TYPE)
            grafos.append(G)
            nodos, aristas = G.number_of_nodes(), G.number_of_edges()
            print(f"  ✓ {nodos:,} nodos  |  {aristas:,} aristas")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if not grafos:
        raise RuntimeError("No se pudo descargar ningún municipio.")

    print("\n→ Combinando grafos del área metropolitana...")
    if len(grafos) > 1:
        G_metro = grafos[0]
        for g in grafos[1:]:
            G_metro = nx.compose(G_metro, g)
    else:
        G_metro = grafos[0]

    # Convertir a grafo no dirigido para simplificar análisis si se desea
    # G_metro = ox.get_undirected(G_metro)

    print(f"\n✅ Red Metropolitana lista:")
    print(f"   Nodos   : {G_metro.number_of_nodes():,}")
    print(f"   Aristas : {G_metro.number_of_edges():,}")

    return G_metro


# ──────────────────────────────────────────────
# 2. GUARDAR EN MÚLTIPLES FORMATOS
# ──────────────────────────────────────────────

def guardar_grafo(G):
    """Exporta el grafo en diferentes formatos."""

    print("\n── Guardando archivos ──────────────────────────────")

    # 2a. GraphML → formato estándar para grafos (Gephi, NetworkX, etc.)
    ruta_graphml = os.path.join(OUTPUT_DIR, "red_vial_amb.graphml")
    ox.save_graphml(G, filepath=ruta_graphml)
    print(f"  ✓ GraphML     → {ruta_graphml}")

    # 2b. Shapefiles → nodos y aristas por separado (QGIS, ArcGIS)
    #ruta_shp = os.path.join(OUTPUT_DIR, "shapefiles")
    #ox.save_graph_shapefile(G, filepath=ruta_shp)
    #print(f"  ✓ Shapefiles  → {ruta_shp}/")

    # 2c. GeoPackage → formato geoespacial moderno (QGIS)
    #ruta_gpkg = os.path.join(OUTPUT_DIR, "red_vial_amb.gpkg")
    #ox.save_graph_geopackage(G, filepath=ruta_gpkg)
    #print(f"  ✓ GeoPackage  → {ruta_gpkg}")

    # 2d. GeoJSON de nodos y aristas (web, Leaflet, Mapbox)
    #nodos_gdf, aristas_gdf = ox.graph_to_gdfs(G)

    #ruta_nodos_json = os.path.join(OUTPUT_DIR, "nodos.geojson")
    #ruta_aristas_json = os.path.join(OUTPUT_DIR, "aristas.geojson")
    #nodos_gdf.to_file(ruta_nodos_json, driver="GeoJSON")
    #aristas_gdf.to_file(ruta_aristas_json, driver="GeoJSON")
    #print(f"  ✓ GeoJSON     → {ruta_nodos_json}")
    #print(f"  ✓ GeoJSON     → {ruta_aristas_json}")

    #return nodos_gdf, aristas_gdf


# ──────────────────────────────────────────────
# 3. ESTADÍSTICAS BÁSICAS DEL GRAFO
# ──────────────────────────────────────────────

def estadisticas(G):
    """Calcula y muestra estadísticas básicas de la red."""

    print("\n── Estadísticas de la red ──────────────────────────")
    stats = ox.basic_stats(G)

    metricas = {
        "Nodos (intersecciones)"    : G.number_of_nodes(),
        "Aristas (segmentos viales)": G.number_of_edges(),
        "Longitud total (km)"       : round(stats.get("edge_length_total", 0) / 1000, 2),
        "Longitud promedio arista (m)": round(stats.get("edge_length_avg", 0), 2),
        "Grado promedio (nodo)"     : round(stats.get("k_avg", 0), 3),
        "Densidad de intersecciones": round(stats.get("intersection_density_km", 0), 4),
    }

    for nombre, valor in metricas.items():
        print(f"  {nombre:<38}: {valor:,}")

    return stats


# ──────────────────────────────────────────────
# 4. VISUALIZACIÓN
# ──────────────────────────────────────────────

def visualizar(G):
    """Genera y guarda un mapa de la red vial."""

    print("\n── Generando visualización ─────────────────────────")
    fig, ax = ox.plot_graph(
        G,
        figsize=(14, 14),
        node_size=0,
        edge_color="#E8C547",
        edge_linewidth=0.4,
        edge_alpha=0.7,
        bgcolor="#1a1a2e",
        show=False,
        close=False,
    )

    ax.set_title(
        "Red Vial — Área Metropolitana de Bucaramanga",
        fontsize=16,
        color="white",
        pad=15,
    )

    ruta_img = os.path.join(OUTPUT_DIR, "mapa_red_vial.png")
    fig.savefig(ruta_img, dpi=200, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close()
    print(f"  ✓ Mapa PNG    → {ruta_img}")


# ──────────────────────────────────────────────
# 5. EJEMPLO DE USO CON NETWORKX
# ──────────────────────────────────────────────

def ejemplo_networkx(G):
    """
    Muestra cómo usar el grafo con NetworkX directamente.
    El grafo descargado ES un objeto NetworkX MultiDiGraph.
    """
    print("\n── Ejemplo de uso con NetworkX ─────────────────────")

    # Obtener nodos y aristas como listas
    nodos = list(G.nodes(data=True))
    aristas = list(G.edges(data=True))

    print(f"  Primer nodo  → ID: {nodos[0][0]}")
    print(f"  Atributos    → {list(nodos[0][1].keys())}")
    print(f"  Primera arista → {aristas[0][2].get('name', 'sin nombre')} "
          f"| {round(aristas[0][2].get('length', 0), 1)} m")

    # Ruta más corta entre dos nodos al azar
    import random
    nodo_origen  = random.choice(list(G.nodes()))
    nodo_destino = random.choice(list(G.nodes()))

    try:
        ruta = nx.shortest_path(G, nodo_origen, nodo_destino, weight="length")
        longitud = nx.shortest_path_length(G, nodo_origen, nodo_destino, weight="length")
        print(f"\n  Ruta más corta de ejemplo:")
        print(f"  Origen  → {nodo_origen}")
        print(f"  Destino → {nodo_destino}")
        print(f"  Nodos en ruta → {len(ruta)}")
        print(f"  Distancia     → {round(longitud, 1)} m")
    except nx.NetworkXNoPath:
        print("  (Los nodos de ejemplo no están conectados)")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Descargar
    #G = descargar_red_vial()

    # 2. Guardar
    #nodos_gdf, aristas_gdf = guardar_grafo(G)

    # 3. Estadísticas
    #estadisticas(G)
    G = ox.load_graphml("red_vial_ambucaramanga/red_vial_amb.graphml")
    # 4. Mapa
    visualizar(G)

    # 5. Ejemplo NetworkX
    ejemplo_networkx(G)

    print("\n" + "=" * 55)
    print(f"  ¡Listo! Archivos guardados en: ./{OUTPUT_DIR}/")
    print("=" * 55)