# PROYECTO DE AULA ELECTROLINERAS

Teoría de Grafos, IA, Programación en Python:

“Sistema para la infraestructura y modelo predictivo de puntos de carga (Electrolineras) para vehículos eléctricos en el
área metropolitana de Bucaramanga”

### OBJETIVO

El proyecto de aula tiene como propósito evaluar las capacidades y competencias desarrolladas por el estudiante al finalizar
el semestre, con especial énfasis en los temas de lógica, programación, estructuras de datos y resolución de problemas. Para
ello, se propone un ejercicio práctico que integra la teoría de grafos, la inteligencia artificial (IA) y la programación en Python,
aplicando los conocimientos adquiridos en las asignaturas de “Algoritmos y Programación” y “Matemáticas Discretas”.

### OBJETIVOS ESPECIFICOS

- Analizar el contexto de las ubicaciones de los puntos de carga (Electrolineras) y puntos de referencia para recorridos
de vehículos eléctricos, como caso de aplicación real de la teoría de grafos y la optimización de las electrolineras.

- Optimizar la ubicación de los puntos de carga, minimizando la distancia promedio que deben recorrer los usuarios y
maximizando la cobertura del servicio dentro de la ciudad.

- Desarrollar habilidades en la implementación de estructuras de datos y técnicas vistas durante el semestre
(secuencias, estructuras selectivas, ciclos repetitivos, arreglos unidimensionales y bidimensionales, manejo de
archivos, teoría de grafos, así como el uso de herramientas y bibliotecas de IA).

- Practicar el manejo de archivos en distintos formatos (.txt, .xlsx, .csv, .json), tanto en lectura como en escritura.

- Ejercitar la implementación de algoritmos clásicos de ordenamiento, recorrido de grafos, búsqueda y modificación
de archivos.

- Fomentar la capacidad de descomposición de problemas en subproblemas más simples y su resolución mediante la
técnica de “Dividir y Conquistar”, a través de la construcción de funciones modulares en Python.

- Comprender la importancia de la aplicación de estructuras de datos, algoritmos y bibliotecas en el desarrollo de
soluciones prácticas, modelos de predicción, dentro del lenguaje de programación Python.

---

## Descargar y ejecutar el programa

Estas lineas de comandos lo que hacen es:

- Clonar el repositorio (descargar el programa)
- Crear un entorno virtual de python y activarlo dentro del repositorio clonado
- Actualizar pip
- Instalar las librerias necesarias para que el programa funcione desde requirments.txt
- Ejecutar el programa


**macOS / Linux**
```bash
git clone https://github.com/sangiato2017/Electrolineras.git && cd Electrolineras && python -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && python menuOpcionesE.py
```

**Windows (PowerShell)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser; git clone https://github.com/sangiato2017/Electrolineras.git; cd Electrolineras; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install -r requirements.txt; python menuOpcionesE.py
```

Al terminar de trabajar, el entorno se desactiva ejecutando:

```bash
deactivate
```

---

