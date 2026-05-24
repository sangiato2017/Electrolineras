# PROYECTO DE AULA ELECTROLINERAS
---

## Descargar y ejecutar el programa

Estas lineas de comandos lo que hacen es:

- Clonar el repositorio (descargar el programa)
- Crear un entorno virtual de python y activarlo dentro del repositorio clonado
- Actualizar pip
- Instalar las librerias necesarias para que el programa funcione desde requirments.txt
- Ejecutar el programa

---
### Recomendaciones al ejecutar

El proyecto ya incluye un dataset con 8000 recorridos por tanto se recomienda ejecutar la opcion 1 y saltar directo a la opcion 3.

```preview
============================================================
SISTEMA DE RECOMENDACIÓN DE NUEVAS ELECTROLINERAS
============================================================
1. Cargar datos de la red vial ---[no cargado]---     <---obligatorio
2. Simular recorridos
3. Ver estadísticas ---[ver estadistica anterior]---  <---Directo aqui
4. Entrenar modelo Random Forest
5. Predecir ubicaciones óptimas nuevas
6. Visualizar 
7. Salir
============================================================

opcion (1-7): 
``` 


**macOS / Linux**
```bash
git clone https://github.com/sangiato2017/Electrolineras.git && cd Electrolineras && python -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && python main.py
```

**Windows (PowerShell)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser; git clone https://github.com/sangiato2017/Electrolineras.git; cd Electrolineras; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install -r requirements.txt; python main.py
```

Al terminar de trabajar, el entorno se desactiva ejecutando:

```bash
deactivate
```

---

