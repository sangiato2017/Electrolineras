import time
import os
import sys
import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
import matplotlib as plt


import funcionesPreparacion as fp

G          = None
df         = None
df_P_E     = None
nodosfixed = None
df_puntos  = None
df_electro = None
n          = 0
#============Menú============#

def mostrar_menu(G):
    
    estado_grafo = "[OK]" if G is not None else "[no cargado]"
    print("\n" + "="*40 + "\n")
    print("SISTEMA DE GESTIÓN DE ELECTROLINERAS")
    print("\n" + "="*40 + "\n" )
    print(f"  Red vial: {estado_grafo}")
    print("\n" + "="*40 + "\n" )
    print("1 |Cargar datos de la red vial de la ciudad")
    print("2 |Configurar parametros para la simulación de recorridos")
    print("3 |Ejecutar simulación de recorridos")
    print("4 |Mostrar estadisticas y resultados")
    print("5 |Salir")
    print("\n" + "="*40)

def simularProceso(seg, mns):
    print(f"\n{mns}", end = "")
    pts = 5
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end = "")
        sys.stdout.flush()
    time.sleep(seg)
    print("\n\n[+] ¡Completado!")
    time.sleep(seg)

#============Validaciones============#

def errorSalida():
    seg = 1
    mns = "Regresando al menú principal"
    print(f"\n{mns}", end = "")
    pts = 3
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end = "")
        sys.stdout.flush()

def enteroPosi(me):
    while True:
        ent = input(me)
        try:
            num = int(ent)
            if(num > 0):
                return num
            else:
                print("\n[-] Error: el numero debe ser mayor a 0.")
        except ValueError:
            print(f"\n[-] Error: {ent} no es un numero valido.")

def floatPosi(me):
    while True:
        ent = input(me)
        try:
            num = float(ent)
            if(num > 0 and num <= 100):
                return num
            else:
                print("\n[-] Error: el numero debe estar entre 0 y 1.")
        except ValueError:
            print(f"\n[-] Error: {ent} no es un numero valido.")

def salida(seg, mns):
    print(f"\n{mns}", end = "")
    pts = 5
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end = "")
        sys.stdout.flush()
    time.sleep(seg)


#============opciones del menú============#

def opcion_1():
    
    global G, listdf, df_P_E, nodosfixed, df_puntos, df_electro, carros
    
    variables = fp.carga_descarga()
    G = variables[0]
    listdf = variables[1]
    df_P_E = variables[2]
    
    carros = listdf[2]
    
    nodosfixed = fp.nodos_cerca(G, df_P_E)
    nodosfixed["id"] = range(1, len(nodosfixed) + 1)
    
    
    df_puntos  = nodosfixed.iloc[:10].reset_index(drop=True)
    df_electro = nodosfixed.iloc[10:].reset_index(drop=True)
    df_electro["id"] = range(1, len(df_electro) + 1)
    
    
def opcion_2():
    global listdf, n
    
    n = enteroPosi("\nIngrese el numero de recorridos a simular: ")
    
    time.sleep(0.5)
    print(f"\nSe ejecutaran {n} recorridos ")
    time.sleep(1)
    
    print("\nPuntos a recorrer:\n")
    puntos = listdf[0]
    print(puntos[["id","nombre"]].to_string(index=False))
    print("\nElectrolineras:\n")
    electros = listdf[1]
    print(electros[["id","nombre"]].to_string(index=False))
    
    time.sleep(0.5)
    print(f"\nSe ejecutaran {n} recorridos ")
    time.sleep(1)
    return n
    
def opcion_3():
    global n, df_puntos, df_electro, carros, G
    
    dfreg = fp.simulacion(n, df_puntos, df_electro, carros, G)
    name = fp.get_filename("registros","csv")
    fp.guardar(dfreg, name)
    

#============Principal============#
def menu_principal():
    global G, listdf, df_P_E, nodosfixed, df_puntos, df_electro, carros
    
    key = 0
    while True:
        
        mostrar_menu(G)
        op = enteroPosi("\nElija una opcion (1-5): ")
        
        match op:
            case 1:
                opcion_1()
                key = 1
                
            case 2:
                if(key >= 1):
                    
                    n = opcion_2()
                    key = 2
                else:
                    print("\n[-] Error: No se han cargado datos" )
                    errorSalida()
                    
            case 3:
                if (key >= 2):
                    
                    opcion_3()
                    key = 3
                else:
                    print("\n[-] Error: No se han cargado datos o no se an configurado parametros" )
                    errorSalida()
            case 4:
                if(key >= 3):
                    simularProceso(2, "\nGenerando estadisticas y resultados")
                else:
                    print("\n[-] Error: No se han simulado recorridos" )
                    errorSalida()
            case 5:
                salida(0.2, "\nSaliendo")
                break
            case _:
                print("\n[-] Error: Opcion invalida")
                errorSalida()
        


menu_principal()
