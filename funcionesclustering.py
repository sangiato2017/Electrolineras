"""
Sugerencias de Electrolineras — KMeans + Mapa Interactivo
==========================================================
Agrupa los eventos de batería baja para sugerir ubicaciones
óptimas para nuevas electrolineras y las visualiza en folium.
"""

import os
import numpy as np
import pandas as pd
import folium
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SALIDA = "amb"


# ══════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════

def distancia_euclidiana_km(lat1, lon1, lat2, lon2):
    """
    Distancia aproximada en km entre dos puntos (fórmula de Haversine simplificada).
    Suficientemente precisa para distancias cortas en el AMB.
    """
    R = 6371  # radio de la Tierra en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arcsin(np.sqrt(a))


def distancia_a_electrolinera_mas_cercana(lat, lon, df_electro):
    """Distancia en km desde un punto a la electrolinera existente más cercana."""
    min_dist = float("inf")
    for _, e in df_electro.iterrows():
        d = distancia_euclidiana_km(lat, lon, e["lat"], e["lon"])
        if d < min_dist:
            min_dist = d
    return round(min_dist, 4)


# ══════════════════════════════════════════════════════════════
# CLUSTERING
# ══════════════════════════════════════════════════════════════

def sugerir_electrolineras(df_registros, df_electro, n_sugerencias=3):
    """
    Aplica KMeans sobre los eventos de batería baja para sugerir
    ubicaciones óptimas para nuevas electrolineras.

    Features usados:
      - evento_lat, evento_lon     : ubicación del evento
      - dist_electro_km            : distancia a electrolinera más cercana
      - autonomia_km (normalizada) : tipo de vehículo

    Parámetros:
        df_registros   : DataFrame con eventos de simulación
        df_electro     : DataFrame con electrolineras existentes (lat, lon)
        n_sugerencias  : número de nuevas electrolineras a sugerir

    Retorna:
        df_sugerencias : DataFrame con ubicaciones sugeridas y métricas
    """

    print(f"\n── Analizando {len(df_registros):,} eventos ────────────────────")
    print(f"   Buscando {n_sugerencias} zonas óptimas para nuevas electrolineras...\n")

    # ── Calcular distancia a electrolinera existente más cercana ──
    df_registros = df_registros.copy()
    df_registros["dist_existente_km"] = df_registros.apply(
        lambda r: distancia_a_electrolinera_mas_cercana(
            r["evento_lat"], r["evento_lon"], df_electro
        ),
        axis=1,
    )

    # ── Features para el clustering ───────────────────────────────
    features = df_registros[[
        "evento_lat",
        "evento_lon",
        "dist_electro_km",     # distancia a la que fue a recargar
        "dist_existente_km",   # distancia a la electrolinera más cercana
        "autonomia_km",        # tipo de vehículo
    ]].copy()

    # Normalizar para que todas las features tengan el mismo peso
    scaler  = StandardScaler()
    X       = scaler.fit_transform(features)

    # ── KMeans ────────────────────────────────────────────────────
    kmeans = KMeans(n_clusters=n_sugerencias, random_state=42, n_init=10)
    df_registros["cluster"] = kmeans.fit_predict(X)

    # ── Construir tabla de sugerencias ────────────────────────────
    sugerencias = []
    for i in range(n_sugerencias):
        zona = df_registros[df_registros["cluster"] == i]
        n_eventos = len(zona)
        pct       = n_eventos / len(df_registros) * 100

        # Centroide geográfico real (promedio de lat/lon del cluster)
        lat_sug = zona["evento_lat"].mean()
        lon_sug = zona["evento_lon"].mean()

        # Distancia promedio a la electrolinera existente más cercana
        dist_prom_existente = zona["dist_existente_km"].mean()

        # Distancia desde el centroide sugerido a la electrolinera existente más cercana
        dist_centroide = distancia_a_electrolinera_mas_cercana(
            lat_sug, lon_sug, df_electro
        )

        # Modelo de vehículo más frecuente en esta zona
        modelo_top = zona["carro_modelo"].value_counts().idxmax()

        # Electrolinera existente más visitada desde esta zona
        electro_top = zona["electro_nombre"].value_counts().idxmax()

        sugerencias.append({
            "zona"                  : i + 1,
            "lat_sugerida"          : round(lat_sug, 6),
            "lon_sugerida"          : round(lon_sug, 6),
            "eventos"               : n_eventos,
            "porcentaje"            : round(pct, 1),
            "dist_electro_exist_km" : round(dist_centroide, 4),
            "dist_prom_varado_km"   : round(dist_prom_existente, 4),
            "vehiculo_frecuente"    : modelo_top,
            "electro_mas_visitada"  : electro_top,
        })

    df_sug = (
        pd.DataFrame(sugerencias)
        .sort_values("eventos", ascending=False)
        .reset_index(drop=True)
    )

    # ── Mostrar resumen ───────────────────────────────────────────
    print(f"  {'Zona':<6} {'Eventos':>8} {'%':>6} {'Dist electro exist':>20} {'Lat':>10} {'Lon':>10}")
    print(f"  {'─'*6} {'─'*8} {'─'*6} {'─'*20} {'─'*10} {'─'*10}")
    for _, f in df_sug.iterrows():
        print(
            f"  {int(f['zona']):<6} "
            f"{f['eventos']:>8,} "
            f"{f['porcentaje']:>5.1f}% "
            f"{f['dist_electro_exist_km']:>18.2f} km "
            f"{f['lat_sugerida']:>10.6f} "
            f"{f['lon_sugerida']:>10.6f}"
        )

    # Guardar CSV
    ruta_csv = os.path.join(SALIDA, "sugerencias_electrolineras.csv")
    df_sug.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    print(f"\n  [+] Sugerencias guardadas → {ruta_csv}")

    return df_sug, df_registros


# ══════════════════════════════════════════════════════════════
# MAPA INTERACTIVO
# ══════════════════════════════════════════════════════════════

def mapa_sugerencias(df_sug, df_electro, df_registros,
                     ruta="amb/mapa_sugerencias.html"):
    """
    Genera un mapa interactivo Folium con:
      - Puntos de eventos (mapa de calor de varados)
      - Electrolineras existentes
      - Electrolineras sugeridas por el modelo
    """

    print("\n── Generando mapa interactivo ───────────────────────")

    centro_lat = df_registros["evento_lat"].mean()
    centro_lon = df_registros["evento_lon"].mean()

    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    # ── Capa 1: Eventos de batería baja (puntos pequeños) ─────────
    grupo_eventos = folium.FeatureGroup(name="🔋 Eventos de batería baja")
    for _, fila in df_registros.iterrows():
        folium.CircleMarker(
            location=[fila["evento_lat"], fila["evento_lon"]],
            radius=3,
            color="#ff6b6b",
            fill=True,
            fill_color="#ff6b6b",
            fill_opacity=0.4,
            tooltip=f"Batería: {fila['bateria_pct']}% | {fila['carro_modelo']}",
        ).add_to(grupo_eventos)
    grupo_eventos.add_to(m)

    # ── Capa 2: Electrolineras existentes ─────────────────────────
    grupo_existentes = folium.FeatureGroup(name="⚡ Electrolineras existentes")
    for _, fila in df_electro.iterrows():
        popup_html = f"""
        <div style='font-family:sans-serif; min-width:180px'>
            <b style='color:#00e5ff'>⚡ {fila['nombre']}</b><br><br>
            <b>Coordenadas:</b><br>
            Lat: {fila['lat']} | Lon: {fila['lon']}
        </div>
        """
        folium.Marker(
            location=[fila["lat"], fila["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"⚡ {fila['nombre']}",
            icon=folium.Icon(color="blue", icon="flash", prefix="fa"),
        ).add_to(grupo_existentes)
    grupo_existentes.add_to(m)

    # ── Capa 3: Electrolineras sugeridas ──────────────────────────
    colores_sug = ["red", "orange", "purple", "green", "darkred"]
    grupo_sugeridas = folium.FeatureGroup(name="📍 Electrolineras sugeridas")

    for _, fila in df_sug.iterrows():
        zona = int(fila["zona"])
        color = colores_sug[(zona - 1) % len(colores_sug)]

        popup_html = f"""
        <div style='font-family:sans-serif; min-width:220px'>
            <b style='font-size:14px; color:#ffd700'>
                📍 Zona sugerida #{zona}
            </b><br><br>
            <b>Eventos en la zona:</b> {fila['eventos']:,} ({fila['porcentaje']}%)<br>
            <b>Dist. a electro existente:</b> {fila['dist_electro_exist_km']} km<br>
            <b>Dist. prom. varado:</b> {fila['dist_prom_varado_km']} km<br>
            <b>Vehículo frecuente:</b> {fila['vehiculo_frecuente']}<br>
            <b>Electro más visitada:</b> {fila['electro_mas_visitada']}<br><br>
            <b>Coordenadas sugeridas:</b><br>
            Lat: {fila['lat_sugerida']} | Lon: {fila['lon_sugerida']}
        </div>
        """

        # Marcador principal
        folium.Marker(
            location=[fila["lat_sugerida"], fila["lon_sugerida"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"📍 Zona sugerida #{zona} — {fila['eventos']:,} eventos",
            icon=folium.Icon(color=color, icon="star", prefix="fa"),
        ).add_to(grupo_sugeridas)

        # Círculo de influencia
        folium.Circle(
            location=[fila["lat_sugerida"], fila["lon_sugerida"]],
            radius=fila["dist_prom_varado_km"] * 1000,  # metros
            color=color,
            fill=True,
            fill_opacity=0.08,
            tooltip=f"Radio de influencia zona #{zona}",
        ).add_to(grupo_sugeridas)

    grupo_sugeridas.add_to(m)

    # ── Control de capas ──────────────────────────────────────────
    folium.LayerControl(collapsed=False).add_to(m)

    # ── Leyenda ───────────────────────────────────────────────────
    leyenda_html = """
    <div style='
        position: fixed; bottom: 30px; left: 30px; z-index: 1000;
        background: rgba(0,0,0,0.8); padding: 12px 16px; border-radius: 8px;
        font-family: sans-serif; color: white; font-size: 13px;
        border: 1px solid #444;
    '>
        <b style='font-size:14px'>Leyenda</b><br><br>
        <span style='color:#ff6b6b'>●</span> Evento batería baja<br>
        <span style='color:#00e5ff'>i</span> Electrolinera existente<br>
        <span style='color:#ffd700'>★</span> Ubicación sugerida<br>
        <span style='opacity:0.5'>○</span> Radio de influencia
    </div>
    """
    m.get_root().html.add_child(folium.Element(leyenda_html))

    m.save(ruta)
    print(f"  [+] Mapa guardado → {ruta}")
    print(f"      Ábrelo en tu navegador para explorar.")


# ══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════

def analisis_completo(df_registros, df_electro, n_sugerencias=3):
    """
    Ejecuta el análisis completo:
      1. KMeans para sugerir ubicaciones
      2. Mapa interactivo con todo
    """
    df_sug, df_reg = sugerir_electrolineras(df_registros, df_electro, n_sugerencias)
    mapa_sugerencias(df_sug, df_electro, df_reg)
    return df_sug