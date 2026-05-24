#Aqui se definen todas las constantes

#para el modelo
LAT_MIN = 6.980
LAT_MAX = 7.155
LON_MIN = -73.175
LON_MAX = -73.045
PASO = 0.004


G = None

estadistica = None

SALIDA = "Datos"

MAPA_INTERACTIVO = "mapa_sugerencias.html"

MAPA_CIUDAD = "amb.graphml"

ARCHIVO_RECORRIDOS = "recorridos.json"

ARCHIVO_ESTADISTICAS = "estadisticas.csv"

ARCHIVO_RESULTADOS = "resultados.csv"


CIUDADES = [
    "Bucaramanga, Santander, Colombia"  ,
    "Floridablanca, Santander, Colombia",
    "Girón, Santander, Colombia"        ,
    "Piedecuesta, Santander, Colombia"
]

PUNTOS_CLAVE = [
    {"ide": 1 , "nombre": "UIS Campus Central"                      , "lat": 7.138910870846234 , "lon": -73.12032665780893},
    {"ide": 2 , "nombre": "UIS Campus Florida"                      , "lat": 7.061655811364763 , "lon": -73.08857057324246},
    {"ide": 3 , "nombre": "UIS Parque Tecnológico Guatiguará"       , "lat": 6.994784145580453 , "lon": -73.06667862587386},
    {"ide": 4 , "nombre": "UIS Campus Bucarica (Centro)"            , "lat": 7.12103758498896  , "lon": -73.12316849078937},
    {"ide": 5 , "nombre": "CENFER"                                  , "lat": 7.0825389469325275, "lon": -73.15430831704738},
    {"ide": 6 , "nombre": "UNAB"                                    , "lat": 7.117167340341574 , "lon": -73.10527508962832},
    {"ide": 7 , "nombre": "UTS (Unidades Tecnológicas de Santander)", "lat": 7.105157239184978 , "lon": -73.12385424317661},
    {"ide": 8 , "nombre": "Universidad Pontificia Bolivariana UPB"  , "lat": 7.03935832884894  , "lon": -73.07256052223526},
    {"ide": 9 , "nombre": "PTAR Río Frío"                           , "lat": 7.065755983770025 , "lon": -73.12805114126374},
    {"ide": 10, "nombre": "Sede Recreacional Catay"                 , "lat": 6.976343071508123 , "lon": -73.04130608532574},
]



ELECTROLINERAS = [
    {"ide": 1, "nombre": "Homecenter"                                 , "lat": 7.115794947043329, "lon": -73.12049190407198},
    {"ide": 2, "nombre": "Centro Comercial Quinta Etapa"              , "lat": 7.115473864260488, "lon": -73.10771498564486},
    {"ide": 3, "nombre": "Centro Comercial Cacique"                   , "lat": 7.099383171372943, "lon": -73.10738728564714},
    {"ide": 4, "nombre": "Centro Comercial Canaveral"                 , "lat": 7.070722605372017, "lon": -73.10545322620052},
    {"ide": 5, "nombre": "Estacion de Servicio Terpel de Piedecuesta" , "lat": 6.998348410998912, "lon": -73.05270638323637},
    {"ide": 6, "nombre": "Éxito de la Rosita"                         , "lat": 7.113534997127967, "lon": -73.12309979445544},
    {"ide": 7, "nombre": "Centro Comercial la Florida"                , "lat": 7.070730036568059, "lon": -73.10553799907328},
    {"ide": 8, "nombre": "Promotores del Oriente (vía a Girón)"       , "lat": 7.085743648912543, "lon": -73.16471385719439},
]

CARROS = [
    {"ide": 1, "modelo": "BYD SEAL 82.5 kWh RWD Design"  ,"gama": "alta", "cap_bat": 84.0, "autonomia": 455, "consumo": 0.172},
    {"ide": 2, "modelo": "BYD DOLPHIN SURF 30 kWh Active","gama": "baja", "cap_bat": 32.0, "autonomia": 190, "consumo": 0.158}
]

BATERIA = 100.0