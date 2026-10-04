=====================================================================
  ¿QUÉ TAN CONCENTRADO ESTÁ UN MERCADO?
  Simulación Monte Carlo de indicadores de concentración
  Organización Industrial - [Universidad Catolica del Norte] -
  Autor: [Tomás Guzmán]
=====================================================================

App publicada: [agregar aquí la URL de Streamlit Community Cloud]


1. DESCRIPCIÓN
---------------------------------------------------------------------
Aplicación web en Python y Streamlit que mide la concentración de un
mercado con cuatro indicadores y la compara con miles de mercados
generados al azar mediante simulación Monte Carlo.

El usuario puede:
  - Elegir un indicador: CRk, IHH, ID o IE.
  - Elegir el número de empresas (N entre 2 y 100).
  - Elegir el número de iteraciones (entre 100 y 10.000; por defecto 1.000).
  - Ver la distribución de resultados en un histograma.
  - Evaluar un mercado con cuotas generadas al azar o con cuotas
    personalizadas. Si las cuotas no suman 100%, la app muestra una alerta.

Para cada mercado evaluado, la app entrega:
  - Su percentil frente a los mercados al azar.
  - Su clasificación según el umbral teórico del indicador, con la
    justificación técnica correspondiente.


2. CONTENIDO DEL ARCHIVO .ZIP
---------------------------------------------------------------------
  app.py               Interfaz web en Streamlit (une todos los módulos)
  indicadores.py       Fórmulas de CRk, IHH, ID e IE
  simulacion.py        Generación de cuotas al azar y simulación Monte Carlo
  evaluador.py         Validaciones, percentil y clasificación por umbrales
  graficos.py          Histograma con Plotly
  requirements.txt     Librerías necesarias (dependencias)
  README.txt           Este archivo
  .streamlit/config.toml   Tema visual de la app (carpeta oculta)


3. REQUISITOS
---------------------------------------------------------------------
  - Python 3.11 o superior (la app se desarrolló con Python 3.14).
  - Conexión a internet para instalar las librerías la primera vez.

Para revisar si Python está instalado, abra una terminal y escriba:

    Mac / Linux:   python3 --version
    Windows:       python --version

Si no está instalado, descárguelo desde https://www.python.org/downloads/
(En Windows, marque la opción "Add Python to PATH" durante la instalación.)


4. EJECUCIÓN LOCAL PASO A PASO
---------------------------------------------------------------------

PASO 1. Descomprimir el archivo .zip
    Descomprima el archivo en una carpeta de su computador.

PASO 2. Abrir una terminal en la carpeta del proyecto
    Mac:      Abra la app Terminal y escriba "cd " (con un espacio al
              final), arrastre la carpeta descomprimida a la ventana y
              presione Enter.
    Windows:  Abra la carpeta descomprimida, escriba "cmd" en la barra
              de direcciones del explorador y presione Enter.

PASO 3. Crear un entorno virtual
    Mac / Linux:   python3 -m venv .venv
    Windows:       python -m venv .venv

PASO 4. Activar el entorno virtual
    Mac / Linux:   source .venv/bin/activate
    Windows:       .venv\Scripts\activate

    Si funcionó, la línea de la terminal comenzará con "(.venv)".

PASO 5. Instalar las librerías
    pip install -r requirements.txt

    Puede tardar uno o dos minutos. Termina con "Successfully installed".

PASO 6. Ejecutar la app
    streamlit run app.py

    La app se abrirá automáticamente en el navegador, en la dirección
    http://localhost:8501
    Si no se abre, copie esa dirección en el navegador.

    La primera vez, Streamlit puede pedir un correo electrónico en la
    terminal. Puede dejarlo en blanco y presionar Enter.

PASO 7. Cerrar la app
    En la terminal, presione Ctrl + C.

Para volver a abrir la app otro día, solo repita los pasos 2, 4 y 6
(el entorno virtual y las librerías ya quedaron instalados).


5. PROBAR LOS MÓDULOS POR SEPARADO (OPCIONAL)
---------------------------------------------------------------------
Con el entorno virtual activo, cada módulo tiene una prueba propia:

    python indicadores.py    Calcula los 4 indicadores en 3 mercados de ejemplo
    python simulacion.py     Compara el IHH simulado con su valor teórico
    python evaluador.py      Prueba validaciones, percentil y umbrales
    python graficos.py       Abre un histograma de ejemplo en el navegador


6. PROBLEMAS FRECUENTES
---------------------------------------------------------------------
  - "command not found: python3" (Mac) o "python no se reconoce" (Windows):
    Python no está instalado o no está en el PATH. Ver sección 3.

  - "ModuleNotFoundError: No module named 'streamlit'":
    El entorno virtual no está activo. Repita el paso 4 y luego el 6.

  - "externally-managed-environment" al instalar:
    Se está instalando fuera del entorno virtual. Repita los pasos 3 y 4.

  - En Windows, error de permisos al activar el entorno en PowerShell:
    Use la terminal "cmd" en vez de PowerShell (ver paso 2).

  - "Port 8501 is already in use":
    La app ya está abierta en otra terminal. Ciérrela con Ctrl + C o
    use la pestaña del navegador que ya está abierta.


7. METODOLOGÍA (RESUMEN)
---------------------------------------------------------------------
Indicadores (s_i = cuota de la empresa i como fracción, N = n° de empresas):
  CRk  = suma de las cuotas de las k empresas más grandes      (0 a 1)
  IHH  = suma de (100 * s_i)^2                                  (0 a 10.000)
  ID   = suma de h_i^2, con h_i = s_i^2 / suma de s_j^2          (0 a 1)
  IE   = -suma de s_i * ln(s_i)                                 (0 a ln N)
         En la entropía, un valor MAYOR indica MENOR concentración.

Simulación Monte Carlo:
  En cada iteración se genera un mercado al azar con N empresas usando
  una distribución de Dirichlet (parámetros iguales a 1), que da la misma
  probabilidad a cualquier reparto posible del 100% del mercado.

Comparación con el azar (percentil de concentración):
  Porcentaje de mercados al azar menos concentrados que el evaluado.
    >= 95%  significativamente MÁS concentrado que el azar
    <=  5%  significativamente MENOS concentrado que el azar
    entre   similar al azar

Umbrales teóricos:
  IHH  < 1.500 no concentrado | 1.500 a 2.500 moderado | > 2.500 alto
       Fuente: Fiscalía Nacional Económica, Guía para el Análisis de
       Operaciones de Concentración Horizontales (2021); coincide con
       DOJ/FTC de EE.UU. (2010).
  CR4  < 40% baja | 40% a 60% moderada | > 60% alta (oligopolio estrecho)
       Fuente: tipología clásica de estructuras de mercado (Shepherd).
       Solo se aplica con k = 4.
  ID   < 0,25 sin dominancia relevante | >= 0,25 dominancia relevante
       Fuente: criterio de la ex Comisión Federal de Competencia de
       México (2.500 en escala 0 a 10.000). Dejó de usarse oficialmente
       en 2015.
  IE   > 1,897 no concentrado | 1,386 a 1,897 moderado | < 1,386 alto
       Umbral DERIVADO (sin norma oficial), obtenido de los umbrales del
       IHH mediante el número equivalente de empresas: e^IE = 10.000/IHH.