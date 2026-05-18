import os
import glob
import pandas as pd

SALIDA = "amb"


def ulimoReg():

    buscar = os.path.join(SALIDA, "registros*.csv") # busca un archivo con ese nombre... el "*" indica que cualquier caracter es valido
    archivo = glob.glob(buscar) # usca todos los archivos que empiezan con registros y que tiene extencion .csv
    archivo.sort(key=os.path.getmtime) # ordena los archivos por fecha de modificación
    ultimo = archivo[-1] # -1 indica el ultimp arcihvo de la lista
    
    print(f"[+] Usando archivo: {ultimo}")
    return ultimo


def cargaReg():
    
    ruta = ulimoReg() # recive la ruta de donde esta el registro ya filtrado con fecha mas reciente
    
    try:
        df = pd.read_csv(ruta, encoding="utf-8-sig") # intenta cargar el archivo de registros
        
        print(f"[+] {len(df):,} ecargas cargados\n") # imprime el tamaño del archivo (cuantas filas tine)
        
        return df
    
    except ValueError:
        
        print(f"[-] Error al leer {ruta}") # si algo falla devuelve el valor none y no se carga nada
        
        return None


def electroEstadisticas():
    
    df = cargaReg()
    
    print("=" * 60)
    print("   ESTADÍSTICAS DE ELECTROLINERAS MÁS VISITADAS")
    print("=" * 60)

    tRecargas = len(df) # cantidad de recargas que se hicieron

    rank = (
        df.groupby("electro_nombre").agg( # agrupa los elementos por nombre
            
            visitas = ("electro_id", "count"), # cuenta cuanas recargas se hicieron en esta electrolinera
            dist_prom_km = ("dist_electro_km", "mean"), # calcula el promedioi de la columna
            bateria_prom = ("bateria_pct", "mean"), # calcula el promedioi de la columna
            km_rest_prom = ("km_restantes", "mean"), # calcula el promedioi de la columna
            
        ).reset_index().sort_values("visitas", ascending=False).reset_index(drop=True) # resetaea el indice
    )                                                                                   # organiza las filas de forma decendente
                                                                                        # vuelve a resetear el indice y borra el anterior indice desordenado
                                                                                        
    rank["traficoen_E"] = (rank["visitas"] / tRecargas * 100).round(2) # saca el porcentaje de participacion de la electrolinera en las cargas de todos los carros

    print(f"\n  Numero de veces que se recargó: {tRecargas:,}\n")
    
    print(rank)
    
    print("\n")
    return rank


def estadistiCarro():
    
    df = cargaReg() # carga el ultimo registro

    print("=" * 60)
    print("   ESTADÍSTICAS POR MODELO DE VEHÍCULO")
    print("=" * 60)

    for m, g in df.groupby("carro_modelo"):
        
        total = len(g)
        electro_top = g["electro_nombre"].value_counts().idxmax()
        visitas_top = g["electro_nombre"].value_counts().max()
        bat_prom = g["bateria_pct"].mean()
        dist_prom = g["dist_electro_km"].mean()

        print(f"\n  Modelo     : {m}")
        print(f"  Recargas   : {total:,}")
        print(f"  Bat. prom  : {bat_prom:.1f}% al solicitar recarga")
        print(f"  Dist. prom : {dist_prom:.2f} km a la electrolinera")
        print(f"  Electro top: {electro_top} ({visitas_top} visitas)")

    print("\n")


def topElectrolineras(n=3):
    
    df = cargaReg()
    

    total = len(df)
    top = df["electro_nombre"].value_counts().head(n)

    print("=" * 60)
    print(f"   TOP {n} ELECTROLINERAS MÁS VISITADAS")
    print("=" * 60)

    for i, (n, v) in enumerate(top.items()):
        
        pct = v / total * 100
        print(f"\n  {i+1}. {n}")
        print(f"      {v:,} visitas  ({pct:.1f}%)")

    print("\n")


def guardaEstadistic(ruta):
    df = cargaReg()
    
    resumen = df.groupby("electro_nombre").agg(
        visitas        = ("evento_id",       "count"),
        dist_prom      = ("dist_electro_km", "mean"),
        lat_electro    = ("electro_lat",     "first"),
        lon_electro    = ("electro_lon",     "first"),
    ).reset_index()
    
    resumen.to_csv(ruta, index=False)
    print(f"[+] Estadísticas guardadas en {ruta}")



def estadisticaselectricas():
    
    df = cargaReg()
    tRecargas = len(df)

    print("=" * 60)
    print("   DETALLE POR ELECTROLINERA")
    print("=" * 60)

    electros = df["electro_nombre"].unique()
    
    electros_ordenadas = (
        df["electro_nombre"].value_counts().index.tolist()
    )

    for e in electros_ordenadas:

        grupo = df[df["electro_nombre"] == e]
        visitas = len(grupo)
        pct = visitas / tRecargas * 100

        dist_prom = grupo["dist_electro_km"].mean()
        dist_min  = grupo["dist_electro_km"].min()
        dist_max  = grupo["dist_electro_km"].max()

        bat_prom  = grupo["bateria_porcent"].mean()
        bat_min   = grupo["bateria_pct"].min()
        bat_max   = grupo["bateria_pct"].max()

        km_prom   = grupo["km_restantes"].mean()

        modelo_top   = grupo["carro_modelo"].value_counts().idxmax()
        visitas_mod  = grupo["carro_modelo"].value_counts().max()

        grupo["ruta"] = grupo["origen_nombre"] + " → " + grupo["destino_nombre"]
        ruta_top      = grupo["ruta"].value_counts().idxmax()
        ruta_frec     = grupo["ruta"].value_counts().max()

        

        print(f"\n  {'─'*56}")
        print(f"  {e}")
        print(f"  {'─'*56}")
        print(f"  Visitas       : {visitas:,}  ({pct:.1f}%) ")
        print(f"  Distancia     : prom {dist_prom:.2f} km  |  min {dist_min:.2f} km  |  max {dist_max:.2f} km")
        print(f"  Batería       : prom {bat_prom:.1f}%   |  min {bat_min:.1f}%   |  max {bat_max:.1f}%")
        print(f"  Km restantes  : prom {km_prom:.2f} km al solicitar recarga")
        print(f"  Vehículo top  : {modelo_top} ({visitas_mod} visitas)")
        print(f"  Ruta frecuente: {ruta_top} ({ruta_frec}x)")

    print(f"\n  {'─'*56}\n")


def mostrarE():
    
    topElectrolineras(n=3)
    electroEstadisticas()
    estadisticaselectricas()
    estadistiCarro()
    