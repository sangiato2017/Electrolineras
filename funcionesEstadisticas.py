import os
import glob
import pandas as pd

SALIDA = "amb"


def ulimoReg():

    buscar = os.path.join(SALIDA, "registros*.csv")
    archivo = glob.glob(buscar)

    archivo.sort(key=os.path.getmtime)
    ultimo = archivo[-1]
    print(f"[+] Usando archivo: {ultimo}")
    return ultimo


def cargaReg():
    
    ruta = ulimoReg()
    
    try:
        df = pd.read_csv(ruta, encoding="utf-8-sig")
        
        print(f"[+] {len(df):,} eventos cargados\n")
        
        return df
    except ValueError:
        
        print(f"[-] Error al leer {ruta}")
        return None


def electroEstadisticas():
    
    df = cargaReg()
    
    print("=" * 40)
    print("   ESTADÍSTICAS DE ELECTROLINERAS MÁS VISITADAS")
    print("=" * 40)

    tEventos = len(df)

    rank = (
        df.groupby("electro_nombre").agg(
            
            visitas = ("evento_id", "count"),
            dist_prom_km = ("dist_electro_km", "mean"),
            bateria_prom = ("bateria_pct", "mean"),
            km_rest_prom = ("km_restantes", "mean"),
            
        ).reset_index().sort_values("visitas", ascending=False).reset_index(drop=True)
    )

    rank["porcentaje"] = (rank["visitas"] / tEventos * 100).round(2)

    print(f"\n  Total de eventos de recarga simulados: {tEventos:,}\n")
    print(f"  {'#':<4} {'Electrolinera':<42} {'Visitas':>8} {'%':>7} {'Dist prom':>10} {'Bat. prom':>10} {'Km rest':>8}")
    print(f"  {'-'*4} {'-'*42} {'-'*8} {'-'*7} {'-'*10} {'-'*10} {'-'*8}")

    for i, fila in rank.iterrows():
        print(
            f"  {i+1:<4} "
            f"{fila['electro_nombre']:<42} "
            f"{fila['visitas']:>8,} "
            f"{fila['porcentaje']:>6.1f}% "
            f"{fila['dist_prom_km']:>9.2f}km "
            f"{fila['bateria_prom']:>9.1f}% "
            f"{fila['km_rest_prom']:>7.2f}km"
        )

    print("\n")
    return rank


def estadisticas_por_modelo():
    """
    Muestra cuántos eventos de recarga tuvo cada modelo de vehículo
    y la electrolinera más frecuentada por cada uno.
    """
    df = cargaReg()
    if df is None:
        return

    print("=" * 60)
    print("   ESTADÍSTICAS POR MODELO DE VEHÍCULO")
    print("=" * 60)

    for modelo, grupo in df.groupby("carro_modelo"):
        total = len(grupo)
        electro_top = grupo["electro_nombre"].value_counts().idxmax()
        visitas_top = grupo["electro_nombre"].value_counts().max()
        bat_prom    = grupo["bateria_pct"].mean()
        dist_prom   = grupo["dist_electro_km"].mean()

        print(f"\n  Modelo     : {modelo}")
        print(f"  Recargas   : {total:,}")
        print(f"  Bat. prom  : {bat_prom:.1f}% al solicitar recarga")
        print(f"  Dist. prom : {dist_prom:.2f} km a la electrolinera")
        print(f"  Electro top: {electro_top} ({visitas_top} visitas)")

    print("\n")


def top_n_electrolineras(n=3):
    """
    Imprime un resumen del podio de las N electrolineras más visitadas.
    Parámetros:
        n (int): cuántas electrolineras mostrar (por defecto 3)
    """
    df = cargaReg()
    if df is None:
        return

    total = len(df)
    top = df["electro_nombre"].value_counts().head(n)

    print("=" * 60)
    print(f"   TOP {n} ELECTROLINERAS MÁS VISITADAS")
    print("=" * 60)

    medallas = ["🥇", "🥈", "🥉"] + ["  "] * (n - 3)

    for i, (nombre, visitas) in enumerate(top.items()):
        pct = visitas / total * 100
        barra = "█" * int(pct / 2)
        print(f"\n  {medallas[i]} {i+1}. {nombre}")
        print(f"      {visitas:,} visitas  ({pct:.1f}%)  {barra}")

    print("\n")


def guardar_estadisticas(ruta):
    df = cargaReg()
    
    resumen = df.groupby("electro_nombre").agg(
        visitas        = ("evento_id",       "count"),
        dist_prom      = ("dist_electro_km", "mean"),
        lat_electro    = ("electro_lat",     "first"),
        lon_electro    = ("electro_lon",     "first"),
    ).reset_index()
    
    resumen.to_csv(ruta, index=False)
    print(f"[+] Estadísticas guardadas → {ruta}")

# ─────────────────────────────────────────────
#  Función principal que agrupa todo
# ─────────────────────────────────────────────

def estadisticas_detalle_electrolineras():
    """
    Muestra una ficha detallada por cada electrolinera con:
      - Total de visitas y porcentaje
      - Distancia promedio, mínima y máxima desde la que fue solicitada
      - Batería promedio, mínima y máxima al llegar
      - Km restantes promedio al llegar
      - Modelo de vehículo que más la visitó
      - Ruta más frecuente que terminó en ella (origen → destino)
    """
    df = cargaReg()
    if df is None:
        return

    tEventos = len(df)

    print("=" * 60)
    print("   DETALLE POR ELECTROLINERA")
    print("=" * 60)

    electros = df["electro_nombre"].unique()
    electros_ordenadas = (
        df["electro_nombre"]
        .value_counts()
        .index
        .tolist()
    )

    for electro in electros_ordenadas:

        grupo = df[df["electro_nombre"] == electro]
        visitas = len(grupo)
        pct     = visitas / tEventos * 100

        dist_prom = grupo["dist_electro_km"].mean()
        dist_min  = grupo["dist_electro_km"].min()
        dist_max  = grupo["dist_electro_km"].max()

        bat_prom  = grupo["bateria_pct"].mean()
        bat_min   = grupo["bateria_pct"].min()
        bat_max   = grupo["bateria_pct"].max()

        km_prom   = grupo["km_restantes"].mean()

        modelo_top   = grupo["carro_modelo"].value_counts().idxmax()
        visitas_mod  = grupo["carro_modelo"].value_counts().max()

        grupo["ruta"] = grupo["origen_nombre"] + " → " + grupo["destino_nombre"]
        ruta_top      = grupo["ruta"].value_counts().idxmax()
        ruta_frec     = grupo["ruta"].value_counts().max()

        barra = "█" * int(pct / 2)

        print(f"\n  {'─'*56}")
        print(f"  📍 {electro}")
        print(f"  {'─'*56}")
        print(f"  Visitas       : {visitas:,}  ({pct:.1f}%)  {barra}")
        print(f"  Distancia     : prom {dist_prom:.2f} km  |  min {dist_min:.2f} km  |  max {dist_max:.2f} km")
        print(f"  Batería       : prom {bat_prom:.1f}%   |  min {bat_min:.1f}%   |  max {bat_max:.1f}%")
        print(f"  Km restantes  : prom {km_prom:.2f} km al solicitar recarga")
        print(f"  Vehículo top  : {modelo_top} ({visitas_mod} visitas)")
        print(f"  Ruta frecuente: {ruta_top} ({ruta_frec}x)")

    print(f"\n  {'─'*56}\n")


def mostrar_estadisticas():
    """
    Ejecuta y muestra todas las estadísticas disponibles:
      1. Top 3 electrolineras (podio visual)
      2. rank completo de electrolineras
      3. Detalle individual por cada electrolinera
      4. Estadísticas por modelo de vehículo
    """
    top_n_electrolineras(n=3)
    electroEstadisticas()
    estadisticas_detalle_electrolineras()
    estadisticas_por_modelo()
    