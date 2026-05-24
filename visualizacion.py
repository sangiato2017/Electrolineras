import pandas as pd
import os
import folium
from config import SALIDA, ARCHIVO_ESTADISTICAS, ELECTROLINERAS, MAPA_INTERACTIVO


def mostrar_estadisticas():
    global estadistica
    
    ruta = os.path.join(SALIDA, ARCHIVO_ESTADISTICAS)
    stats = pd.read_csv(ruta)
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE USO DE ELECTROLINERAS")
    print("="*60 )
    
    for modelo in stats["vehiculo"].unique():
        sub = stats[stats["vehiculo"] == modelo]
        gama = sub["gama"].iloc[0]
        total = len(sub)
        
        print(f"\n{modelo} ({gama} gama) — {total} recargas totales")
        print("-"*60)
        
        cuantos = sub["electrolinera"].value_counts()
        
        for electrolinera, cantidad in cuantos.items():
            porcentaje = round((cantidad / total) * 100, 1)

            print(f"  {electrolinera:<45} {cantidad:>4} ({porcentaje}%)")
            

def ver(sugerencias):
    
    mapa = folium.Map(location=[7.1193, -73.1227], zoom_start=12)
    
    for e in ELECTROLINERAS:
        folium.Marker(
            location=[e["lat"], e["lon"]],
            popup=e["nombre"],
            tooltip=e["nombre"],
            icon=folium.Icon(color="blue", icon="bolt", prefix="fa")
        ).add_to(mapa)
        
    for i, s in enumerate(sugerencias):
        folium.Marker(
            location=[s["lat"], s["lon"]],
            popup=f"Sugerencia {i+1} - Demanda: Alta",
            tooltip=f"Nueva electrolinera sugerida {i+1}",
            icon=folium.Icon(color="red", icon="star", prefix="fa")
        ).add_to(mapa)
    
    ruta = os.path.join(SALIDA, MAPA_INTERACTIVO)
    mapa.save(ruta)
    print(f"\n[+] Mapa guardado en: {ruta}")
    print("[i] Abre el archivo .html en tu navegador para verlo")

