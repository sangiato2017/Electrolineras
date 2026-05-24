import osmnx as ox
import networkx as nx
import os


from config import CIUDADES, SALIDA, MAPA_CIUDAD


def descargaelgrafo():
    "Descarga el mapa del area metropolitana"
    
    print("\nDescargando mapa... \n")
    
    G = ox.graph_from_place(CIUDADES, network_type="drive")
    
    
    return G

def guardaelgrafo():
    "Guarda el mapa"
    
    G = descargaelgrafo()
    print("\n[+] Guardando el mapa de la ciudad... \n")
    ruta = os.path.join(SALIDA, MAPA_CIUDAD)
    ox.save_graphml(G, filepath=ruta)
    print(f"[+] Mapa guardado como {ruta}")
    
    return G

def obtener_mapa():
    ruta = os.path.join(SALIDA, MAPA_CIUDAD)
    if (os.path.exists(ruta)):
        print(f"\n[i] Ya existe el mapa en: {ruta} cargandolo...")
        G = ox.load_graphml(ruta)
        print("[+] Mapa cargado con exito")
    else:
        G = guardaelgrafo()
    
    return G