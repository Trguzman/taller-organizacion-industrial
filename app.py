"""
app.py
------
Página web en Streamlit que une todos los módulos:
indicadores.py, simulacion.py, evaluador.py y graficos.py.

Para abrirla:  streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st

from indicadores import calcular_indicador
from simulacion import (
    simular_montecarlo, generar_cuotas_aleatorias,
    N_MIN, N_MAX, ITER_MIN, ITER_MAX, ITER_DEFECTO,
)
from evaluador import (
    validar_cuotas, porcentajes_a_fracciones, resumir_simulacion,
    evaluar_mercado, clasificar_umbral,
)
from graficos import histograma, NOMBRES

# ---------------------------------------------------------------------
# Configuración general de la página
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Concentración de mercado",
    page_icon="📊",
    layout="wide",
)

# Un poco de estilo: tarjetas suaves para las métricas
st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background: #EEF2F6;
        border-left: 4px solid #1F4E79;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def simular_cacheado(indicador, n, iteraciones, k, semilla):
    """Guarda la simulación en memoria para no repetirla si nada cambió."""
    return simular_montecarlo(indicador, n, iteraciones, k, semilla)


def formatear(indicador, valor):
    """Muestra cada indicador en su formato habitual."""
    if indicador == "CRk":
        return f"{valor:.1%}".replace(".", ",")
    if indicador == "IHH":
        return f"{valor:,.0f}".replace(",", ".")
    return f"{valor:.3f}".replace(".", ",")


# Memoria de la sesión (se mantiene mientras el usuario usa la página)
if "semilla" not in st.session_state:
    st.session_state.semilla = 1
if "cuotas_azar" not in st.session_state:
    st.session_state.cuotas_azar = None


# ---------------------------------------------------------------------
# Barra lateral: configuración
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("1. Indicador")
    indicador = st.selectbox(
        "¿Con qué indicador quieres medir?",
        options=["CRk", "IHH", "ID", "IE"],
        format_func=lambda x: NOMBRES[x].format(k="k"),
    )

    st.header("2. Simulación")
    n = st.slider("Número de empresas (N)", N_MIN, N_MAX, 10)

    k = 4
    if indicador == "CRk":
        k = st.number_input(
            "Empresas más grandes a sumar (k)",
            min_value=1, max_value=n - 1, value=min(4, n - 1), step=1,
            help="Los umbrales estándar existen para k = 4 (CR4).",
        )

    iteraciones = st.slider(
        "Iteraciones Monte Carlo", ITER_MIN, ITER_MAX, ITER_DEFECTO, step=100,
        help="Cantidad de mercados al azar que se generan.",
    )

    if st.button("Volver a simular", width="stretch"):
        st.session_state.semilla += 1

    st.header("3. Mercado a evaluar")
    modo = st.radio(
        "¿Quieres comparar un mercado?",
        ["Solo ver la simulación", "Cuotas al azar", "Mis propias cuotas"],
    )


# ---------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------
st.title("¿Qué tan concentrado está un mercado?")
st.write(
    "Compara la concentración de un mercado con la de miles de mercados "
    "generados al azar con el mismo número de empresas (simulación Monte Carlo), "
    "y clasifícala según los umbrales teóricos de cada indicador."
)

# ---------------------------------------------------------------------
# Mercado a evaluar
# ---------------------------------------------------------------------
cuotas = None  # cuotas del mercado evaluado, como fracciones

if modo == "Cuotas al azar":
    actuales = st.session_state.cuotas_azar
    if actuales is None or len(actuales) != n:
        st.session_state.cuotas_azar = generar_cuotas_aleatorias(n)
    if st.button("Generar otras cuotas"):
        st.session_state.cuotas_azar = generar_cuotas_aleatorias(n)
    cuotas = st.session_state.cuotas_azar

elif modo == "Mis propias cuotas":
    st.subheader("Ingresa las cuotas de mercado (%)")
    tabla_inicial = pd.DataFrame({
        "Empresa": [f"Empresa {i + 1}" for i in range(n)],
        "Cuota (%)": [round(100 / n, 2)] * n,
    })
    tabla = st.data_editor(
        tabla_inicial,
        key=f"editor_{n}",  # si cambia N, la tabla se reinicia
        hide_index=True,
        width="stretch",
        disabled=["Empresa"],
        column_config={
            "Cuota (%)": st.column_config.NumberColumn(
                min_value=0.0, max_value=100.0, step=0.01, format="%.2f"
            )
        },
    )
    porcentajes = tabla["Cuota (%)"].fillna(0).to_numpy()
    st.caption(f"Suma actual: {porcentajes.sum():.2f}%")

    es_valido, mensaje = validar_cuotas(porcentajes)
    if es_valido:
        cuotas = porcentajes_a_fracciones(porcentajes)
    else:
        st.error(f"⚠️ {mensaje} Corrige las cuotas para evaluar el mercado.")

# ---------------------------------------------------------------------
# Simulación y resultados
# ---------------------------------------------------------------------
with st.spinner("Simulando mercados al azar..."):
    resultados = simular_cacheado(indicador, n, iteraciones, k, st.session_state.semilla)
resumen = resumir_simulacion(resultados)

valor = calcular_indicador(indicador, cuotas, k) if cuotas is not None else None

# Métricas principales
if valor is not None:
    evaluacion = evaluar_mercado(valor, resultados, indicador)
    umbral = clasificar_umbral(indicador, valor, k)

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor del mercado", formatear(indicador, valor))
    c2.metric("Percentil frente al azar", f"{evaluacion['percentil']:.1f}%".replace(".", ","))
    c3.metric("Promedio de mercados al azar", formatear(indicador, resumen["promedio"]))
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Promedio", formatear(indicador, resumen["promedio"]))
    c2.metric("Percentil 5", formatear(indicador, resumen["p5"]))
    c3.metric("Percentil 95", formatear(indicador, resumen["p95"]))

# Histograma
fig = histograma(resultados, indicador, k=k, valor_mercado=valor)
st.plotly_chart(fig, width="stretch")

if indicador == "IE":
    st.caption("En la entropía, un valor más ALTO significa un mercado MENOS concentrado.")

# Interpretación
if valor is not None:
    col_azar, col_umbral = st.columns(2)

    with col_azar:
        st.subheader("Comparado con el azar")
        p = evaluacion["percentil"]
        if p >= 95:
            st.error(evaluacion["mensaje"])
        elif p <= 5:
            st.success(evaluacion["mensaje"])
        else:
            st.info(evaluacion["mensaje"])
        st.write(
            f"El {p:.1f}% de los mercados al azar con {n} empresas está menos "
            f"concentrado que este mercado.".replace(".", ",", 1)
        )

    with col_umbral:
        st.subheader("Según el umbral teórico")
        nivel = umbral["nivel"]
        if "alt" in nivel.lower() or nivel == "Dominancia relevante":
            st.error(nivel)
        elif "moderad" in nivel.lower():
            st.warning(nivel)
        elif nivel == "Sin umbral estándar":
            st.info(nivel)
        else:
            st.success(nivel)
        with st.expander("Ver justificación técnica"):
            st.write(umbral["justificacion"])

    with st.expander("Ver cuotas del mercado evaluado"):
        tabla_cuotas = pd.DataFrame({
            "Empresa": [f"Empresa {i + 1}" for i in range(len(cuotas))],
            "Cuota (%)": np.round(np.asarray(cuotas) * 100, 2),
        }).sort_values("Cuota (%)", ascending=False)
        st.dataframe(tabla_cuotas, hide_index=True, width="stretch")

with st.expander("Ver estadísticas de la simulación"):
    st.dataframe(
        pd.DataFrame({
            "Estadística": ["Promedio", "Desviación estándar", "Mínimo",
                            "Percentil 5", "Mediana", "Percentil 95", "Máximo"],
            "Valor": [formatear(indicador, resumen[c]) for c in
                      ["promedio", "desviacion", "minimo", "p5", "mediana", "p95", "maximo"]],
        }),
        hide_index=True, width="stretch",
    )

with st.expander("¿Cómo se calculan los indicadores?"):
    st.markdown(
        r"""
- **CRk**: suma de las cuotas de las $k$ empresas más grandes. $CR_k = \sum_{i=1}^{k} s_i$
- **IHH**: suma de las cuotas al cuadrado, en porcentaje (0 a 10.000). $IHH = \sum (100\,s_i)^2$
- **ID**: mide cuánto del IHH se explica por las empresas grandes. $ID = \sum h_i^2$, con $h_i = s_i^2 / \sum s_j^2$
- **IE**: entropía de las cuotas. $IE = -\sum s_i \ln(s_i)$. Va de 0 (monopolio) a $\ln(N)$ (todas iguales).

Las cuotas al azar se generan con una distribución de Dirichlet, que da la misma
probabilidad a cualquier reparto posible del 100% del mercado.
"""
    )