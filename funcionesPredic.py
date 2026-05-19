import os
import numpy as np
import pandas as pd
import folium
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

SALIDA = "amb"


def distanciaHaversineKm(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arcsin(np.sqrt(a))


def distanciaAElectrolinerasMasCercana(lat, lon, dfElectro):
    minDist = float("inf")
    for _, e in dfElectro.iterrows():
        d = distanciaHaversineKm(lat, lon, e["lat"], e["lon"])
        if d < minDist:
            minDist = d
    return round(minDist, 4)


def generarCandidatas(G, dfRegistros, cadaNNodos=5):
    """
    Genera candidatos a partir de nodos reales de la red vial.
    Asi los puntos sugeridos siempre caen sobre calles existentes,
    nunca en montanas, rios ni zonas sin infraestructura.

    Para no usar todos los nodos del grafo (que pueden ser cientos de miles),
    se toma uno de cada cadaNNodos, lo que da una muestra representativa
    sin disparar el tiempo de computo.
    """
    latMin = dfRegistros["evento_lat"].min() - 0.02
    latMax = dfRegistros["evento_lat"].max() + 0.02
    lonMin = dfRegistros["evento_lon"].min() - 0.02
    lonMax = dfRegistros["evento_lon"].max() + 0.02

    candidatas = []
    for nodoId, datos in G.nodes(data=True):
        lat = datos["y"]
        lon = datos["x"]
        if latMin <= lat <= latMax and lonMin <= lon <= lonMax:
            candidatas.append({"nodoId": nodoId, "lat": lat, "lon": lon})

    dfTodos = pd.DataFrame(candidatas)
    dfCand = dfTodos.iloc[::cadaNNodos].reset_index(drop=True)

    print(f"  [+] Nodos en la red vial del area: {len(dfTodos):,}")
    print(f"  [+] Candidatos seleccionados (1 de cada {cadaNNodos}): {len(dfCand):,}")
    return dfCand


def calcularFeaturesCandidatas(dfCand, dfRegistros, dfElectro, radioInfluenciaKm=2.0):
    """
    Para cada punto candidato calcula features que describen su utilidad
    como ubicacion de una nueva electrolinera:

    - densidadEventos: cuantos eventos de bateria baja ocurrieron cerca
    - distMediaEventos: distancia promedio a esos eventos (que tan centrico es)
    - distElectroExistente: distancia a la electrolinera existente mas cercana
    - autonomiaPromCercana: autonomia promedio de vehiculos varados cerca
    - bateriaPromCercana: bateria promedio al varar (que tan urgente era)
    - kmRestantesPromCercanos: km restantes promedio al varar
    """
    densidades = []
    distMedias = []
    distElectros = []
    autonomiasProm = []
    bateriasProm = []
    kmRestantesProm = []

    eventosLat = dfRegistros["evento_lat"].values
    eventosLon = dfRegistros["evento_lon"].values
    autonomias = dfRegistros["autonomia_km"].values
    baterias = dfRegistros["bateria_pct"].values
    kmRestantes = dfRegistros["km_restantes"].values

    for _, cand in dfCand.iterrows():
        distancias = np.array([
            distanciaHaversineKm(cand["lat"], cand["lon"], eLat, eLon)
            for eLat, eLon in zip(eventosLat, eventosLon)
        ])

        mascaraCercanos = distancias <= radioInfluenciaKm
        nCercanos = mascaraCercanos.sum()

        if nCercanos > 0:
            densidades.append(nCercanos)
            distMedias.append(distancias[mascaraCercanos].mean())
            autonomiasProm.append(autonomias[mascaraCercanos].mean())
            bateriasProm.append(baterias[mascaraCercanos].mean())
            kmRestantesProm.append(kmRestantes[mascaraCercanos].mean())
        else:
            densidades.append(0)
            distMedias.append(radioInfluenciaKm)
            autonomiasProm.append(0)
            bateriasProm.append(100)
            kmRestantesProm.append(0)

        distElectros.append(distanciaAElectrolinerasMasCercana(cand["lat"], cand["lon"], dfElectro))

    dfCand = dfCand.copy()
    dfCand["densidadEventos"] = densidades
    dfCand["distMediaEventos"] = distMedias
    dfCand["distElectroExistente"] = distElectros
    dfCand["autonomiaPromCercana"] = autonomiasProm
    dfCand["bateriaPromCercana"] = bateriasProm
    dfCand["kmRestantesPromCercanos"] = kmRestantesProm

    return dfCand


def etiquetarCandidatas(dfCand, umbralDensidad=None, umbralDistMin=0.5):
    """
    Etiqueta cada candidata como buena (1) o mala (0) ubicacion.

    Una candidata es buena si:
    - Tiene alta densidad de eventos cercanos (hay necesidad real)
    - Esta suficientemente lejos de electrolineras existentes (no duplica cobertura)

    El umbral de densidad se calcula automaticamente si no se especifica.
    """
    if umbralDensidad is None:
        umbralDensidad = dfCand["densidadEventos"].quantile(0.6)

    hayNecesidad = dfCand["densidadEventos"] >= umbralDensidad
    noDuplicaCobertura = dfCand["distElectroExistente"] >= umbralDistMin

    dfCand = dfCand.copy()
    dfCand["esUbicacionBuena"] = (hayNecesidad & noDuplicaCobertura).astype(int)

    nBuenas = dfCand["esUbicacionBuena"].sum()
    nTotales = len(dfCand)
    print(f"  [+] Etiquetado: {nBuenas:,} candidatas buenas de {nTotales:,} ({nBuenas/nTotales*100:.1f}%)")

    return dfCand


def entrenarRandomForest(dfCand):
    """
    Entrena un Random Forest para aprender que combinacion de features
    hace que una ubicacion sea optima para una nueva electrolinera.
    Retorna el modelo, el scaler y el score de probabilidad para cada candidata.
    """
    columnaFeatures = [
        "densidadEventos",
        "distMediaEventos",
        "distElectroExistente",
        "autonomiaPromCercana",
        "bateriaPromCercana",
        "kmRestantesPromCercanos",
    ]

    X = dfCand[columnaFeatures].values
    y = dfCand["esUbicacionBuena"].values

    scaler = StandardScaler()
    XScaled = scaler.fit_transform(X)

    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    modelo.fit(XScaled, y)

    probBuena = modelo.predict_proba(XScaled)[:, 1]

    importancias = dict(zip(columnaFeatures, modelo.feature_importances_))
    print("\n  Importancia de features (Random Forest):")
    for feat, imp in sorted(importancias.items(), key=lambda x: -x[1]):
        barra = "█" * int(imp * 40)
        print(f"    {feat:<30} {barra} {imp:.3f}")

    return modelo, scaler, probBuena


def seleccionarMejoresCandidatas(dfCand, probBuena, nSugerencias, separacionMinimaKm=1.5):
    """
    Selecciona las N mejores candidatas asegurando que no esten demasiado cerca
    entre si (no queremos sugerir dos electrolineras a 200 metros de distancia).

    Usa un algoritmo greedy: toma la mejor, descarta las que estan muy cerca,
    repite hasta tener N sugerencias.
    """
    dfCand = dfCand.copy()
    dfCand["scoreRf"] = probBuena

    dfOrdenado = dfCand[dfCand["densidadEventos"] > 0].sort_values("scoreRf", ascending=False).reset_index(drop=True)

    seleccionadas = []
    for _, candidata in dfOrdenado.iterrows():
        if len(seleccionadas) >= nSugerencias:
            break

        demasiadoCerca = False
        for selec in seleccionadas:
            dist = distanciaHaversineKm(candidata["lat"], candidata["lon"], selec["lat"], selec["lon"])
            if dist < separacionMinimaKm:
                demasiadoCerca = True
                break

        if not demasiadoCerca:
            seleccionadas.append(candidata)

    return pd.DataFrame(seleccionadas).reset_index(drop=True)


def construirResumenSugerencias(dfSeleccionadas, dfRegistros, dfElectro, radioInfluenciaKm=2.0):
    """
    Construye el dataframe final de sugerencias con toda la informacion
    relevante para cada ubicacion propuesta.
    """
    sugerencias = []

    for zona, fila in enumerate(dfSeleccionadas.itertuples(), start=1):
        distancias = dfRegistros.apply(
            lambda r: distanciaHaversineKm(fila.lat, fila.lon, r["evento_lat"], r["evento_lon"]),
            axis=1,
        )
        eventosCercanos = dfRegistros[distancias <= radioInfluenciaKm]
        nEventos = len(eventosCercanos)
        pct = nEventos / len(dfRegistros) * 100

        if nEventos > 0:
            modeloTop = eventosCercanos["carro_modelo"].value_counts().idxmax()
            electroTop = eventosCercanos["electro_nombre"].value_counts().idxmax()
            distPromVarado = distancias[distancias <= radioInfluenciaKm].mean()
        else:
            modeloTop = "N/A"
            electroTop = "N/A"
            distPromVarado = 0

        distElectroExist = distanciaAElectrolinerasMasCercana(fila.lat, fila.lon, dfElectro)

        sugerencias.append({
            "zona": zona,
            "lat_sugerida": round(fila.lat, 6),
            "lon_sugerida": round(fila.lon, 6),
            "score_rf": round(fila.scoreRf, 4),
            "eventos": nEventos,
            "porcentaje": round(pct, 1),
            "dist_electro_exist_km": round(distElectroExist, 4),
            "dist_prom_varado_km": round(distPromVarado, 4),
            "vehiculo_frecuente": modeloTop,
            "electro_mas_visitada": electroTop,
        })

    dfSug = pd.DataFrame(sugerencias).sort_values("score_rf", ascending=False).reset_index(drop=True)
    dfSug["zona"] = range(1, len(dfSug) + 1)
    return dfSug


def sugerirElectrolineras(G, dfRegistros, dfElectro, nSugerencias=3):
    print(f"\n── Analizando {len(dfRegistros):,} eventos ────────────────────")
    print(f"   Buscando {nSugerencias} zonas optimas con Random Forest...\n")

    print("  [1/5] Extrayendo candidatos de la red vial...")
    dfCand = generarCandidatas(G, dfRegistros)

    print("  [2/5] Calculando features por candidato...")
    dfCand = calcularFeaturesCandidatas(dfCand, dfRegistros, dfElectro)

    print("  [3/5] Etiquetando candidatos...")
    dfCand = etiquetarCandidatas(dfCand)

    print("  [4/5] Entrenando Random Forest...")
    _, _, probBuena = entrenarRandomForest(dfCand)

    print("\n  [5/5] Seleccionando mejores ubicaciones...")
    dfSeleccionadas = seleccionarMejoresCandidatas(dfCand, probBuena, nSugerencias)

    dfSug = construirResumenSugerencias(dfSeleccionadas, dfRegistros, dfElectro)

    print(f"\n  {'Zona':<6} {'Score RF':>9} {'Eventos':>8} {'%':>6} {'Dist exist':>12} {'Lat':>10} {'Lon':>10}")
    print(f"  {'─'*6} {'─'*9} {'─'*8} {'─'*6} {'─'*12} {'─'*10} {'─'*10}")
    for _, f in dfSug.iterrows():
        print(
            f"  {int(f['zona']):<6}"
            f" {f['score_rf']:>9.4f}"
            f" {f['eventos']:>8,}"
            f" {f['porcentaje']:>5.1f}%"
            f" {f['dist_electro_exist_km']:>10.2f} km"
            f" {f['lat_sugerida']:>10.6f}"
            f" {f['lon_sugerida']:>10.6f}"
        )

    rutaCsv = os.path.join(SALIDA, "sugerencias_electrolineras.csv")
    dfSug.to_csv(rutaCsv, index=False, encoding="utf-8-sig")
    print(f"\n  [+] Sugerencias guardadas → {rutaCsv}")

    return dfSug, dfCand


def mapasSugerencias(dfSug, dfElectro, dfRegistros, ruta="amb/mapa_sugerencias.html"):
    print("\n── Generando mapa interactivo ───────────────────────")

    centroLat = dfRegistros["evento_lat"].mean()
    centroLon = dfRegistros["evento_lon"].mean()

    m = folium.Map(
        location=[centroLat, centroLon],
        zoom_start=12,
        tiles="CartoDB dark_matter",
    )

    grupoEventos = folium.FeatureGroup(name="🔋 Eventos de bateria baja")
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
            <b>Score Random Forest:</b> {fila['score_rf']}<br>
            <b>Eventos en la zona:</b> {fila['eventos']:,} ({fila['porcentaje']}%)<br>
            <b>Dist. a electro existente:</b> {fila['dist_electro_exist_km']} km<br>
            <b>Dist. prom. varado:</b> {fila['dist_prom_varado_km']} km<br>
            <b>Vehiculo frecuente:</b> {fila['vehiculo_frecuente']}<br>
            <b>Electro mas visitada:</b> {fila['electro_mas_visitada']}<br><br>
            <b>Coordenadas sugeridas:</b><br>
            Lat: {fila['lat_sugerida']} | Lon: {fila['lon_sugerida']}
        </div>
        """

        folium.Marker(
            location=[fila["lat_sugerida"], fila["lon_sugerida"]],
            popup=folium.Popup(popupHtml, max_width=280),
            tooltip=f"📍 Zona #{zona} — Score RF: {fila['score_rf']} — {fila['eventos']:,} eventos",
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
        <span style='color:#ff6b6b'>●</span> Evento bateria baja<br>
        <span style='color:#00e5ff'>i</span> Electrolinera existente<br>
        <span style='color:#ffd700'>★</span> Ubicacion sugerida (RF)<br>
        <span style='opacity:0.5'>○</span> Radio de influencia
    </div>
    """
    m.get_root().html.add_child(folium.Element(leyendaHtml))

    m.save(ruta)
    print(f"  [+] Mapa guardado → {ruta}")
    print(f"      Abrelo en tu navegador para explorar.")


def analisisCompleto(G, dfRegistros, dfElectro, nSugerencias=3):
    dfSug, dfCand = sugerirElectrolineras(G, dfRegistros, dfElectro, nSugerencias)
    mapasSugerencias(dfSug, dfElectro, dfRegistros)
    return dfSug