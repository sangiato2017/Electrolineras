import numpy as np
import pandas as pd


carros = []
def info_carro(modelo, Cbatery, autonomia, potencia):
    carros.append({
        "id": len(carros),
        "modelo": modelo,
        "cbateria": Cbatery,
        "autonomia": autonomia,
        "potencia": potencia
    })
    return pd.DataFrame(carros)

def guardar(df, ruta="info_carros.csv"):
    df.to_csv(ruta, index=False, encoding="utf-8-sig")


carro1 = info_carro("BYD SEAL 82.5 kWh RWD Design", 84.0, 455, 172)
carro2 = info_carro("BYD DOLPHIN SURF 30 kWh Active", 32.0, 190, 158)

guardar(pd.DataFrame(carros))

carros = pd.read_csv("info_carros.csv")

carros