import os
import glob
import pandas as pd

SALIDA = "amb"


def ultimoReg():
    buscar = os.path.join(SALIDA, "registros*.csv")
    archivo = glob.glob(buscar)
    archivo.sort(key=os.path.getmtime)
    ultimo = archivo[-1]
    print(f"[+] Usando archivo: {ultimo}")
    return ultimo


def cargaReg():
    ruta = ultimoReg()
    try:
        df = pd.read_csv(ruta, encoding="utf-8-sig")
        print(f"[+] {len(df):,} recargas cargados\n")
        return df
    except ValueError:
        print(f"[-] Error al leer {ruta}")
        return None


def electroEstadisticas():
    df = cargaReg()

    print("=" * 60)
    print("   ESTADÍSTICAS DE ELECTROLINERAS MÁS VISITADAS")
    print("=" * 60)

    tRecargas = len(df)

    rank = (
        df.groupby("electro_nombre").agg(
            visitas=("electro_id", "count"),
            distPromKm=("dist_electro_km", "mean"),
            bateriaProm=("bateria_pct", "mean"),
            kmRestProm=("km_restantes", "mean"),
        ).reset_index().sort_values("visitas", ascending=False).reset_index(drop=True)
    )

    rank["traficoEnE"] = (rank["visitas"] / tRecargas * 100).round(2)

    print(f"\n  Numero de veces que se recargó: {tRecargas:,}\n")
    print(rank)
    print("\n")
    return rank


def estadistiCarro():
    df = cargaReg()

    print("=" * 60)
    print("   ESTADÍSTICAS POR MODELO DE VEHÍCULO")
    print("=" * 60)

    for m, g in df.groupby("carro_modelo"):
        total = len(g)
        electroTop = g["electro_nombre"].value_counts().idxmax()
        visitasTop = g["electro_nombre"].value_counts().max()
        batProm = g["bateria_pct"].mean()
        distProm = g["dist_electro_km"].mean()

        print(f"\n  Modelo: {m}")
        print(f"  Recargas: {total:,}")
        print(f"  Bat. prom  : {batProm:.1f}% al solicitar recarga")
        print(f"  Dist. prom : {distProm:.2f} km a la electrolinera")
        print(f"  Electro top: {electroTop} ({visitasTop} visitas)")

    print("\n")


def topElectrolineras(n=3):
    df = cargaReg()

    total = len(df)
    top = df["electro_nombre"].value_counts().head(n)

    print("=" * 60)
    print(f"   TOP {n} ELECTROLINERAS MÁS VISITADAS")
    print("=" * 60)

    for i, (nombre, visitas) in enumerate(top.items()):
        pct = visitas / total * 100
        print(f"\n  {i+1}. {nombre}")
        print(f"      {visitas:,} visitas  ({pct:.1f}%)")

    print("\n")


def guardaEstadistic(ruta):
    df = cargaReg()

    resumen = df.groupby("electro_nombre").agg(
        visitas=("evento_id", "count"),
        distProm=("dist_electro_km", "mean"),
        latElectro=("electro_lat", "first"),
        lonElectro=("electro_lon", "first"),
    ).reset_index()

    resumen.to_csv(ruta, index=False)
    print(f"[+] Estadísticas guardadas en {ruta}")


def estadisticasElectricas():
    df = cargaReg()
    tRecargas = len(df)

    print("=" * 60)
    print("   DETALLE POR ELECTROLINERA")
    print("=" * 60)

    electrosOrdenadas = df["electro_nombre"].value_counts().index.tolist()

    for e in electrosOrdenadas:
        grupo = df[df["electro_nombre"] == e]
        visitas = len(grupo)
        pct = visitas / tRecargas * 100

        distProm = grupo["dist_electro_km"].mean()
        distMin = grupo["dist_electro_km"].min()
        distMax = grupo["dist_electro_km"].max()

        batProm = grupo["bateria_pct"].mean()
        batMin = grupo["bateria_pct"].min()
        batMax = grupo["bateria_pct"].max()

        kmProm = grupo["km_restantes"].mean()

        modeloTop = grupo["carro_modelo"].value_counts().idxmax()
        visitasMod = grupo["carro_modelo"].value_counts().max()

        grupo["ruta"] = grupo["origen_nombre"] + " → " + grupo["destino_nombre"]
        rutaTop = grupo["ruta"].value_counts().idxmax()
        rutaFrec = grupo["ruta"].value_counts().max()

        print(f"\n  {'─'*56}")
        print(f"  {e}")
        print(f"  {'─'*56}")
        print(f"  Visitas: {visitas:,}  ({pct:.1f}%) ")
        print(f"  Distancia: prom {distProm:.2f} km  |  min {distMin:.2f} km  |  max {distMax:.2f} km")
        print(f"  Batería: prom {batProm:.1f}%   |  min {batMin:.1f}%   |  max {batMax:.1f}%")
        print(f"  Km restantes: prom {kmProm:.2f} km al solicitar recarga")
        print(f"  Vehículo top: {modeloTop} ({visitasMod} visitas)")
        print(f"  Ruta frecuente: {rutaTop} ({rutaFrec}x)")

    print(f"\n  {'─'*56}\n")


def mostrarE():
    topElectrolineras(n=3)
    electroEstadisticas()
    estadisticasElectricas()
    estadistiCarro()
