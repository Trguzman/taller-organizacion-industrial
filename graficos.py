"""
graficos.py
-----------
Histograma de la simulación Monte Carlo con Plotly.
Muestra:
  - la distribución de los mercados al azar (barras),
  - los percentiles 5 y 95 (líneas grises punteadas),
  - el mercado evaluado, si existe (línea roja),
  - las zonas de los umbrales teóricos (fondo de color).
"""

import numpy as np
import plotly.graph_objects as go

from evaluador import (
    resumir_simulacion,
    IHH_MODERADO, IHH_ALTO,
    CR4_MODERADO, CR4_ALTO,
    ID_UMBRAL,
    IE_MODERADO, IE_ALTO,
)

# Colores de las zonas de umbral
VERDE, AMARILLO, ROJO = "#2ca02c", "#ffbf00", "#d62728"

NOMBRES = {
    "CRk": "Ratio de concentración (CR{k})",
    "IHH": "Índice de Herfindahl-Hirschman (IHH)",
    "ID": "Índice de Dominancia (ID)",
    "IE": "Índice de Entropía (IE)",
}


def _zonas_umbral(indicador, k):
    """
    Devuelve las zonas de umbral como lista de (desde, hasta, color, texto).
    Si el indicador no tiene umbral estándar (CRk con k distinto de 4), devuelve [].
    """
    inf = float("inf")
    if indicador == "IHH":
        return [(0, IHH_MODERADO, VERDE, "No concentrado"),
                (IHH_MODERADO, IHH_ALTO, AMARILLO, "Moderado"),
                (IHH_ALTO, inf, ROJO, "Alto")]
    if indicador == "CRk" and k == 4:
        return [(0, CR4_MODERADO, VERDE, "Baja"),
                (CR4_MODERADO, CR4_ALTO, AMARILLO, "Moderada"),
                (CR4_ALTO, inf, ROJO, "Alta")]
    if indicador == "ID":
        return [(0, ID_UMBRAL, VERDE, "Sin dominancia"),
                (ID_UMBRAL, inf, ROJO, "Dominancia")]
    if indicador == "IE":  # al revés: valores bajos = más concentrado
        return [(0, IE_ALTO, ROJO, "Alto"),
                (IE_ALTO, IE_MODERADO, AMARILLO, "Moderado"),
                (IE_MODERADO, inf, VERDE, "No concentrado")]
    return []


def histograma(resultados, indicador, k=4, valor_mercado=None,
               mostrar_umbrales=True, n_barras=40):
    """
    Crea y devuelve la figura del histograma.
      resultados:      valores simulados (salida de simular_montecarlo)
      indicador:       "CRk", "IHH", "ID" o "IE"
      valor_mercado:   valor del mercado evaluado (opcional)
      mostrar_umbrales: True para pintar las zonas de umbral
    """
    r = np.asarray(resultados, dtype=float)
    resumen = resumir_simulacion(r)
    nombre = NOMBRES[indicador].format(k=k)

    # Rango del eje X: datos + mercado evaluado, con un pequeño margen
    valores = [r.min(), r.max()] + ([valor_mercado] if valor_mercado is not None else [])
    x_min, x_max = min(valores), max(valores)
    margen = (x_max - x_min) * 0.05 or 0.01
    x_min, x_max = max(0.0, x_min - margen), x_max + margen

    fig = go.Figure()

    # 1) Zonas de umbral (fondo), recortadas al rango visible
    if mostrar_umbrales:
        for desde, hasta, color, texto in _zonas_umbral(indicador, k):
            a, b = max(desde, x_min), min(hasta, x_max)
            if a < b:
                fig.add_vrect(x0=a, x1=b, fillcolor=color, opacity=0.10,
                              line_width=0, layer="below",
                              annotation_text=texto, annotation_position="top left",
                              annotation_font_size=11)

    # 2) Barras de la simulación
    fig.add_trace(go.Histogram(
        x=r, nbinsx=n_barras, name="Mercados al azar",
        marker_color="#4C78A8", opacity=0.85,
    ))

    # 3) Percentiles 5 y 95
    for clave, texto in [("p5", "P5"), ("p95", "P95")]:
        fig.add_vline(x=resumen[clave], line_dash="dot", line_color="gray",
                      annotation_text=texto, annotation_position="bottom right")

    # 4) Mercado evaluado
    if valor_mercado is not None:
        fig.add_vline(x=valor_mercado, line_color="red", line_width=3,
                      annotation_text="Mercado evaluado",
                      annotation_position="top right",
                      annotation_font_color="red")

    fig.update_layout(
        title=f"Distribución de {nombre} en {len(r):,} mercados al azar".replace(",", "."),
        xaxis_title=nombre,
        yaxis_title="Frecuencia (n° de mercados)",
        bargap=0.05,
        showlegend=False,
        margin=dict(t=70, b=50, l=60, r=30),
    )
    fig.update_xaxes(range=[x_min, x_max])
    if indicador == "CRk":
        fig.update_xaxes(tickformat=".0%")  # mostrar CRk como porcentaje

    return fig


# ---------------------------------------------------------------------
# Prueba rápida: solo se ejecuta si corres "python graficos.py"
# Abre el gráfico en tu navegador.
# ---------------------------------------------------------------------
if __name__ == "__main__":
    from indicadores import calcular_indicador
    from simulacion import simular_montecarlo

    cuotas = [0.70, 0.10, 0.10, 0.10]
    resultados = simular_montecarlo("IHH", n=4, iteraciones=1000, semilla=42)
    valor = calcular_indicador("IHH", cuotas)

    fig = histograma(resultados, "IHH", valor_mercado=valor)
    fig.show()
    print("Gráfico abierto en el navegador.")