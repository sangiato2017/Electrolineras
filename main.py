import os
import grafo as gf
import simulacion as sm
import visualizacion as vs
import modelo as md
from config import SALIDA, G, ARCHIVO_ESTADISTICAS, estadistica


os.makedirs(SALIDA, exist_ok=True)

def menu_principal():
    global G, estadistica
    
    if(os.path.exists(os.path.join(SALIDA, ARCHIVO_ESTADISTICAS))):
        estadistica = True
    anterior = "no hay estidistica aún" if estadistica is None else "ver estadistica anterior"
    estado = "no cargado" if G is None else "cargado"
    print(f'''
{"="*60}
SISTEMA DE RECOMENDACIÓN DE NUEVAS ELECTROLINERAS
{"="*60}
1. Cargar datos de la red vial ---[{estado}]---
2. Simular recorridos
3. Ver estadísticas ---[{anterior}]---
4. Entrenar modelo Random Forest
5. Predecir ubicaciones óptimas nuevas
6. Visualizar 
7. Salir
{"="*60}''')

def opciones():
    global G, modelo, df, sugerencias
    key = 0
    while True:
        menu_principal()
        op = entero_positivo("\nopcion (1-7): ")
        
        match op:
            case 1:
                G = gf.obtener_mapa()
                key = 1
            case 2:
                if(key >= 1):
                    sm.simulacion(G)
                    key = 2
                else:
                    print("\n[-] no se ha cargado la red vial")
            case 3:
                if(os.path.exists(os.path.join(SALIDA, ARCHIVO_ESTADISTICAS))):
                    vs.mostrar_estadisticas()
                    key = 3
                else:
                    print("\n[-] Porfavor ejecute las opciones en orden")
            case 4:
                if (key >= 3 and G is not None):
                    modelo, df = md.entrenar_modelo(G)
                    key = 4
                else:
                    print("\n[-] Porfavor ejecute las opciones en orden")
            case 5:
                if(key >= 4):
                    
                    sugerencias = md.predecir_electrolineras(G,modelo, df)
                    key = 5
                else:
                    print("\n[-] Porfavor ejecute las opciones en orden")
            case 6:
                if(key >= 5):
                    vs.ver(sugerencias)
                    key = 6
                else:
                    print("\n[-] Porfavor ejecute las opciones en orden")
            case 7:
                print("\nSaliendo...")
                break
            case _ :
                print("\n[-] Opcion invalida")

def entero_positivo(mensaje):
    "Valida que el numero ingresado sea entero y positivo"
    while True:
        entrada = input(mensaje)
        try:
            num = int(entrada)
            if num > 0:
                return num
            else:
                print("\n[-] Error: el numero debe ser mayor a 0.")
        except ValueError:
            print(f"\n[-] Error: {entrada} no es un numero valido.\n")

opciones()