# Sistema de Gestión de Electrolineras — AMB

Simulación de recorridos de vehículos eléctricos sobre la red vial del **Área Metropolitana de Bucaramanga** (Bucaramanga, Floridablanca, Girón y Piedecuesta). El sistema descarga el grafo vial desde OpenStreetMap, ubica puntos clave y electrolineras en la red, y simula eventos de recarga según el nivel de batería de cada vehículo.

---

## Requisitos previos

- **Python 3.10 o superior**
- **pip** actualizado
- Conexión a Internet (para la descarga inicial del mapa desde OpenStreetMap)

> En Windows se recomienda usar la terminal **PowerShell** o **CMD**. En macOS/Linux, la terminal estándar.

---

## 1. Clonar o descargar el proyecto

```bash
# Con git:
git clone <url-del-repositorio>
cd <nombre-de-la-carpeta>

# O simplemente coloca los archivos en una carpeta y abre una terminal allí.
```

---

## 2. Crear el entorno virtual

```bash
# Crear el entorno virtual en una carpeta llamada "venv"
python -m venv venv
```

### Activar el entorno virtual

| Sistema operativo | Comando |
|---|---|
| Windows (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| Windows (CMD) | `venv\Scripts\activate.bat` |
| macOS / Linux | `source venv/bin/activate` |

Cuando el entorno esté activo verás el prefijo `(venv)` al inicio de la línea de tu terminal.

---

## 3. Actualizar pip

```bash
python -m pip install --upgrade pip
```

---

## 4. Instalar las dependencias

### Opción A — desde el archivo `requirements.txt` (recomendado)

```bash
pip install -r requirements.txt
```

### Opción B — instalación manual una por una

```bash
pip install osmnx
pip install networkx
pip install matplotlib
pip install pandas
pip install folium
pip install numpy
```

> Las librerías `os`, `sys`, `time` y `random` son parte de la biblioteca estándar de Python y **no requieren instalación**.

---

## 5. Archivo `requirements.txt`

Si no tienes el archivo, créalo en la raíz del proyecto con este contenido:

```
osmnx>=1.9.0
networkx>=3.3
matplotlib>=3.9.0
pandas>=2.2.0
folium>=0.17.0
numpy>=1.26.0
```

---

## 6. Estructura esperada del proyecto

```
proyecto/
│
├── funcionesPreparacion.py   # Lógica principal: carga de mapa, simulación, utilidades
├── menuOpcionesE.py          # Menú interactivo de consola
├── requirements.txt          # Dependencias
├── README.md                 # Este archivo
│
└── amb/                      # Carpeta generada automáticamente al ejecutar
    ├── mapa.graphml           # Grafo de la red vial (se descarga la primera vez)
    ├── puntosclave.csv        # Puntos clave del AMB
    ├── electrolineras.csv     # Ubicaciones de electrolineras
    ├── carros.csv             # Modelos de vehículos eléctricos
    ├── mapaInteractivo.html   # Visualización interactiva (Folium)
    └── registros.csv          # Resultados de la simulación
```

---

## 7. Ejecutar el sistema

```bash
python menuOpcionesE.py
```

Al iniciar verás el menú principal. Las opciones deben seguirse en orden:

```
========================================

SISTEMA DE GESTIÓN DE ELECTROLINERAS

========================================

  Red vial: [no cargado]

========================================

1 | Cargar datos de la red vial de la ciudad
2 | Configurar parametros para la simulación de recorridos
3 | Ejecutar simulación de recorridos
4 | Mostrar estadisticas y resultados
5 | Salir
```

| Paso | Opción | Descripción |
|---|---|---|
| 1 | `1` | Descarga el grafo vial desde OpenStreetMap (solo la primera vez; las siguientes lo carga desde `amb/mapa.graphml`) |
| 2 | `2` | Define el número de recorridos a simular |
| 3 | `3` | Ejecuta la simulación y guarda los resultados en `amb/registros.csv` |
| 4 | `4` | Muestra estadísticas y resultados |

> **Nota:** La primera descarga del mapa puede tardar varios minutos dependiendo de la conexión a Internet, ya que obtiene la red vial completa de los cuatro municipios del AMB.

---

## 8. Desactivar el entorno virtual

Cuando termines de trabajar, desactiva el entorno con:

```bash
deactivate
```

---

## 9. Solución de problemas frecuentes

**`ModuleNotFoundError: No module named 'osmnx'`**
Asegúrate de que el entorno virtual esté activado antes de ejecutar el script.

**Error de permisos en Windows al activar el entorno**
Ejecuta PowerShell como administrador y corre:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**La descarga del mapa falla o se interrumpe**
Verifica tu conexión a Internet. Si el error persiste, la API de OpenStreetMap puede estar temporalmente saturada; espera unos minutos y vuelve a intentarlo.

**`FileNotFoundError` al cargar archivos CSV**
Ejecuta primero la opción `1` del menú para que se genere la carpeta `amb/` y sus archivos.
