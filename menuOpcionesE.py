import time
import os
import sys
import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
import matplotlib as plt

import funcionesPreparacion as fp
import funcionesEstadisticas as fe
import funcionesclustering as fc

G = None
df = None
dfPE = None
nodosFixed = None
dfPuntos = None
dfElectro = None
n = 0


def mostrarMenu(G):
    estadoGrafo = "[OK]" if G is not None else "[no cargado]"
    print("\n" + "="*60 + "\n")
    print("SISTEMA DE GESTIÓN DE ELECTROLINERAS")
    print("\n" + "="*60 + "\n")
    print(f"  Red vial: {estadoGrafo}")
    print("\n" + "="*60 + "\n")
    print("1 |Cargar datos de la red vial de la ciudad")
    print("2 |Configurar parametros para la simulación de recorridos")
    print("3 |Ejecutar simulación de recorridos")
    print("4 |Mostrar estadisticas y resultados")
    print("5 |Sugerir electrolineras")
    print("6 |Salir")
    print("\n" + "="*60)

def simularProceso(seg, mns):
    print(f"\n{mns}", end="")
    pts = 5
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end="")
        sys.stdout.flush()
    time.sleep(seg)
    print("\n\n[+] ¡Completado!")
    time.sleep(seg)


def errorSalida():
    seg = 1
    mns = "Regresando al menú principal"
    print(f"\n{mns}", end="")
    pts = 3
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end="")
        sys.stdout.flush()

def enteroPosi(me):
    while True:
        ent = input(me)
        try:
            num = int(ent)
            if num > 0:
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
            if num > 0 and num <= 100:
                return num
            else:
                print("\n[-] Error: el numero debe estar entre 0 y 1.")
        except ValueError:
            print(f"\n[-] Error: {ent} no es un numero valido.")

def salida(seg, mns):
    print(f"\n{mns}", end="")
    pts = 5
    timePts = seg / pts
    for i in range(pts):
        time.sleep(timePts)
        print(".", end="")
        sys.stdout.flush()
    time.sleep(seg)


def opcion1():
    global G, listdf, dfPE, nodosFixed, dfPuntos, dfElectro, carros

    variables = fp.cargaDescarga()
    G = variables[0]
    listdf = variables[1]
    dfPE = variables[2]

    carros = listdf[2]

    nodosFixed = fp.nodosCerca(G, dfPE)
    nodosFixed["id"] = range(1, len(nodosFixed) + 1)

    dfPuntos = nodosFixed.iloc[:10].reset_index(drop=True)
    dfElectro = nodosFixed.iloc[10:].reset_index(drop=True)
    dfElectro["id"] = range(1, len(dfElectro) + 1)


def opcion2():
    global listdf, n

    n = enteroPosi("\nIngrese el numero de recorridos a simular: ")

    time.sleep(0.5)
    print(f"\nSe ejecutaran {n} recorridos ")
    time.sleep(1)

    print("\nPuntos a recorrer:\n")
    puntos = listdf[0]
    print(puntos[["id", "nombre"]].to_string(index=False))
    print("\nElectrolineras:\n")
    electros = listdf[1]
    print(electros[["id", "nombre"]].to_string(index=False))

    time.sleep(0.5)
    print(f"\nSe ejecutaran {n} recorridos ")
    time.sleep(1)
    return n

def opcion3():
    global n, dfPuntos, dfElectro, carros, G

    dfReg = fp.simulacion(n, dfPuntos, dfElectro, carros, G)
    name = fp.filename("registros", "csv")
    fp.guardar(dfReg, name)
    print(f"registros guardados como: {name}")

def opcion4():
    fe.mostrarE()
    name = fp.filename("estadistica", "csv")
    fe.guardaEstadistic(name)

def opcion5():
    dfReg = fe.cargaReg()
    dfElectro = listdf[1]

    n = enteroPosi("\n¿Cuántas nuevas electrolineras sugerir? ")
    fc.analisisCompleto(dfReg, dfElectro, nSugerencias=n)


def menuPrincipal():
    global G, listdf, dfPE, nodosFixed, dfPuntos, dfElectro, carros

    key = 0
    while True:
        mostrarMenu(G)
        op = enteroPosi("\nElija una opcion (1-6): ")

        match op:
            case 1:
                opcion1()
                key = 1

            case 2:
                if key >= 1:
                    n = opcion2()
                    key = 2
                else:
                    print("\n[-] Error: No se han cargado datos")
                    errorSalida()

            case 3:
                if key >= 2:
                    opcion3()
                    key = 3
                else:
                    print("\n[-] Error: No se han cargado datos o no se an configurado parametros")
                    errorSalida()

            case 4:
                if key >= 3:
                    opcion4()
                    key = 4
                else:
                    print("\n[-] Error: No se han simulado recorridos")
                    errorSalida()

            case 5:
                if key >= 4:
                    opcion5()
                else:
                    print("\n[-] Error: No se han simulado recorridos")
                    errorSalida()

            case 6:
                salida(0.2, "\nSaliendo")
                break

            case _:
                print("\n[-] Error: Opcion invalida")
                errorSalida()


menuPrincipal()
