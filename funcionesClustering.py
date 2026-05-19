import os
import numpy as np
import pandas as pd
import folium
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SALIDA = "amb"


def distanciaEuclidianaKm(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arcsin(np.sqrt(a))


def distanciaElectrolinearMasCercana(lat, lon, dfElectro):
    minDist = float("inf")
    for _, electro in dfElectro.iterrows():
        d = distanciaEuclidianaKm(lat, lon, electro["lat"], electro["lon"])
        if d < minDist:
            minDist = d
    return round(minDist, 4)


def sugerirElectrolineras(dfRegistros, dfElectro, nSugerencias=3):
    print(f"\n── Analizando {len(dfRegistros):,} eventos ────────────────────")
    print(f"   Buscando {nSugerencias} zonas óptimas para nuevas electrolineras...\n")

    dfRegistros = dfRegistros.copy()
    dfRegistros["dist_existente_km"] = dfRegistros.apply(
        lambda r: distanciaElectrolinearMasCercana(r["evento_lat"], r["evento_lon"], dfElectro),
        axis=1,
    )

    features = dfRegistros[[
        "evento_lat",
        "evento_lon",
        "dist_electro_km",
        "dist_existente_km",
        "autonomia_km",
    ]].copy()

    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=nSugerencias, random_state=42, n_init=10)
    dfRegistros["cluster"] = kmeans.fit_predict(X)

    sugerencias = []
    for i in range(nSugerencias):
        zona = dfRegistros[dfRegistros["cluster"] == i]
        nEventos = len(zona)
        pct = nEventos / len(dfRegistros) * 100

        latSug = zona["evento_lat"].mean()
        lonSug = zona["evento_lon"].mean()

        distPromExistente = zona["dist_existente_km"].mean()
        distCentroide = distanciaElectrolinearMasCercana(latSug, lonSug, dfElectro)

        modeloTop = zona["carro_modelo"].value_counts().idxmax()
        electroTop = zona["electro_nombre"].value_counts().idxmax()

        sugerencias.append({
            "zona": i + 1,
            "lat_sugerida": round(latSug, 6),
            "lon_sugerida": round(lonSug, 6),
            "eventos": nEventos,
            "porcentaje": round(pct, 1),
            "dist_electro_exist_km": round(distCentroide, 4),
            "dist_prom_varado_km": round(distPromExistente, 4),
            "vehiculo_frecuente": modeloTop,
            "electro_mas_visitada": electroTop,
        })

    dfSug = (
        pd.DataFrame(sugerencias)
        .sort_values("eventos", ascending=False)
        .reset_index(drop=True)
    )

    print(f"  {'Zona':<6} {'Eventos':>8} {'%':>6} {'Dist electro exist':>20} {'Lat':>10} {'Lon':>10}")
    print(f"  {'─'*6} {'─'*8} {'─'*6} {'─'*20} {'─'*10} {'─'*10}")
    for _, fila in dfSug.iterrows():
        print(
            f"  {int(fila['zona']):<6} "
            f"{fila['eventos']:>8,} "
            f"{fila['porcentaje']:>5.1f}% "
            f"{fila['dist_electro_exist_km']:>18.2f} km "
            f"{fila['lat_sugerida']:>10.6f} "
            f"{fila['lon_sugerida']:>10.6f}"
        )

    rutaCsv = os.path.join(SALIDA, "sugerencias_electrolineras.csv")
    dfSug.to_csv(rutaCsv, index=False, encoding="utf-8-sig")
    print(f"\n  [+] Sugerencias guardadas → {rutaCsv}")

    return dfSug, dfRegistros


def mapasSugerencias(dfSug, dfElectro, dfRegistros, ruta="amb/mapa_sugerencias.html"):
    print("\n── Generando mapa interactivo ───────────────────────")

    centroLat = dfRegistros["evento_lat"].mean()
    centroLon = dfRegistros["evento_lon"].mean()

    m = folium.Map(
        location=[centroLat, centroLon],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    grupoEventos = folium.FeatureGroup(name="🔋 Eventos de batería baja")
    for _, fila in dfRegistros.iterrows():
        folium.CircleMarker(
            location=[fila["evento_lat"], fila["evento_lon"]],
            radius=3,
            color="#ff6b6b",
            fill=True,
            fill_color="#ff6b6b",
            fill_opacity=0.4,
            tooltip=f"Batería: {fila['bateria_pct']}% | {fila['carro_modelo']}",
        ).add_to(grupoEventos)
    grupoEventos.add_to(m)

    grupoExistentes = folium.FeatureGroup(name="⚡ Electrolineras existentes")
    for _, fila in dfElectro.iterrows():
        popupHtml = f"""
        <div style='font-family:sans-serif; min-width:180px'>
            <b style='color:#00e5ff'>⚡ {fila['nombre']}</b><br><br>
            <b>Coordenadas:</b><br>
            Lat: {fila['lat']} | Lon: {fila['lon']}
        </div>
        """
        folium.Marker(
            location=[fila["lat"], fila["lon"]],
            popup=folium.Popup(popupHtml, max_width=250),
            tooltip=f"⚡ {fila['nombre']}",
            icon=folium.Icon(color="blue", icon="flash", prefix="fa"),
        ).add_to(grupoExistentes)
    grupoExistentes.add_to(m)

    coloresSug = ["red", "orange", "purple", "green", "darkred"]
    grupoSugeridas = folium.FeatureGroup(name="📍 Electrolineras sugeridas")

    for _, fila in dfSug.iterrows():
        zona = int(fila["zona"])
        color = coloresSug[(zona - 1) % len(coloresSug)]

        popupHtml = f"""
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

        folium.Marker(
            location=[fila["lat_sugerida"], fila["lon_sugerida"]],
            popup=folium.Popup(popupHtml, max_width=280),
            tooltip=f"📍 Zona sugerida #{zona} — {fila['eventos']:,} eventos",
            icon=folium.Icon(color=color, icon="star", prefix="fa"),
        ).add_to(grupoSugeridas)

        folium.Circle(
            location=[fila["lat_sugerida"], fila["lon_sugerida"]],
            radius=fila["dist_prom_varado_km"] * 1000,
            color=color,
            fill=True,
            fill_opacity=0.08,
            tooltip=f"Radio de influencia zona #{zona}",
        ).add_to(grupoSugeridas)

    grupoSugeridas.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    leyendaHtml = """
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
    m.get_root().html.add_child(folium.Element(leyendaHtml))

    m.save(ruta)
    print(f"  [+] Mapa guardado → {ruta}")
    print(f"      Ábrelo en tu navegador para explorar.")


def analisisCompleto(dfRegistros, dfElectro, nSugerencias=3):
    dfSug, dfReg = sugerirElectrolineras(dfRegistros, dfElectro, nSugerencias)
    mapasSugerencias(dfSug, dfElectro, dfReg)
    return dfSug
