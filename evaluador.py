"""
evaluador.py
------------
Controles y evaluación de resultados:
  1) Validar los datos que ingresa el usuario (cuotas y k).
  2) Resumir la distribución simulada.
  3) Comparar un mercado concreto contra los mercados al azar.
"""

import numpy as np

from simulacion import N_MIN, N_MAX

# Margen para aceptar errores de redondeo (por ejemplo 33.33 x 3 = 99.99)
TOLERANCIA_SUMA = 0.1  # puntos porcentuales


# ---------------------------------------------------------------------
# 1) VALIDACIONES
# ---------------------------------------------------------------------
def validar_cuotas(cuotas_porcentaje):
    """
    Revisa las cuotas que escribe el usuario, en PORCENTAJE (ej: 40 = 40%).
    Devuelve (es_valido, mensaje). Si no es válido, el mensaje explica por qué.
    """
    cuotas = np.asarray(cuotas_porcentaje, dtype=float)
    n = len(cuotas)

    if not (N_MIN <= n <= N_MAX):
        return False, f"Debe haber entre {N_MIN} y {N_MAX} empresas (hay {n})."
    if np.any(cuotas < 0):
        return False, "Ninguna cuota puede ser negativa."

    suma = cuotas.sum()
    if abs(suma - 100) > TOLERANCIA_SUMA:
        return False, f"Las cuotas suman {suma:.2f}% y deben sumar 100%."

    return True, "Las cuotas son válidas."


def validar_k(k, n):
    """
    Revisa que k tenga sentido para el CRk: entre 1 y N - 1.
    (Si k >= N, el CRk siempre da 100% y no entrega información.)
    """
    if not (1 <= k <= n - 1):
        return False, f"Con {n} empresas, k debe estar entre 1 y {n - 1}."
    return True, "k es válido."


def porcentajes_a_fracciones(cuotas_porcentaje):
    """Convierte cuotas en % (40) a fracciones (0.40) y corrige el redondeo para que sumen 1 exacto."""
    cuotas = np.asarray(cuotas_porcentaje, dtype=float)
    return cuotas / cuotas.sum()


# ---------------------------------------------------------------------
# 2) RESUMEN DE LA SIMULACIÓN
# ---------------------------------------------------------------------
def resumir_simulacion(resultados):
    """Estadísticas básicas de la distribución simulada."""
    r = np.asarray(resultados, dtype=float)
    return {
        "promedio": float(r.mean()),
        "desviacion": float(r.std()),
        "minimo": float(r.min()),
        "p5": float(np.percentile(r, 5)),
        "mediana": float(np.percentile(r, 50)),
        "p95": float(np.percentile(r, 95)),
        "maximo": float(r.max()),
    }


# ---------------------------------------------------------------------
# 3) COMPARACIÓN CONTRA MERCADOS AL AZAR
# ---------------------------------------------------------------------
def percentil_concentracion(valor, resultados, indicador):
    """
    Porcentaje de mercados al azar que están MENOS concentrados que el mercado evaluado.
      - CRk, IHH, ID: menos concentrado = valor MÁS BAJO.
      - IE (entropía): menos concentrado = valor MÁS ALTO (va al revés).
    Resultado entre 0 y 100.
    """
    r = np.asarray(resultados, dtype=float)
    if indicador == "IE":
        return float(np.mean(r >= valor) * 100)
    return float(np.mean(r <= valor) * 100)


def interpretar(percentil):
    """Traduce el percentil a un mensaje simple."""
    if percentil >= 95:
        return "El mercado está significativamente MÁS concentrado que un mercado al azar."
    if percentil <= 5:
        return "El mercado está significativamente MENOS concentrado que un mercado al azar."
    return "El nivel de concentración es similar al de un mercado al azar."


def evaluar_mercado(valor, resultados, indicador):
    """Junta todo: devuelve el percentil y su interpretación."""
    p = percentil_concentracion(valor, resultados, indicador)
    return {"percentil": p, "mensaje": interpretar(p)}


# ---------------------------------------------------------------------
# 4) UMBRALES TEÓRICOS ESTÁNDAR
# ---------------------------------------------------------------------
# IHH: FNE Chile (Guía 2021), igual a DOJ/FTC EE.UU. (2010)
IHH_MODERADO, IHH_ALTO = 1500, 2500
# CR4: tipología clásica de oligopolios (Shepherd)
CR4_MODERADO, CR4_ALTO = 0.40, 0.60
# ID: criterio de la ex Comisión Federal de Competencia de México (2.500 en escala 0-10.000)
ID_UMBRAL = 0.25
# IE: sin umbral oficial; se deriva de los umbrales del IHH usando el
# "número equivalente de empresas" (N_eq = 1/IHH  y  N_eq = e^IE)
IE_ALTO = float(np.log(10000 / IHH_ALTO))          # ln(4)    = 1.386
IE_MODERADO = float(np.log(10000 / IHH_MODERADO))  # ln(6.67) = 1.897


def _miles(x):
    """Escribe números con punto de miles, al estilo chileno (2.500 en vez de 2,500)."""
    return f"{x:,.0f}".replace(",", ".")


def clasificar_umbral(indicador, valor, k=4):
    """
    Clasifica el valor según el umbral teórico estándar del indicador.
    Devuelve un diccionario con el 'nivel' y la 'justificacion' técnica.
    """
    if indicador == "IHH":
        if valor < IHH_MODERADO:
            nivel = "Mercado no concentrado"
        elif valor <= IHH_ALTO:
            nivel = "Mercado moderadamente concentrado"
        else:
            nivel = "Mercado altamente concentrado"
        justificacion = (
            f"IHH = {_miles(valor)}. Se usan los umbrales de la Fiscalía Nacional Económica "
            f"(Guía para el Análisis de Operaciones de Concentración Horizontales, 2021), "
            f"que coinciden con los del DOJ/FTC de EE.UU. (2010): bajo {_miles(IHH_MODERADO)} no concentrado, "
            f"entre {_miles(IHH_MODERADO)} y {_miles(IHH_ALTO)} moderado, sobre {_miles(IHH_ALTO)} alto. "
            f"Un IHH de {_miles(IHH_ALTO)} equivale a un mercado con 4 empresas iguales."
        )

    elif indicador == "CRk":
        if k != 4:
            nivel = "Sin umbral estándar"
            justificacion = (
                f"CR{k} = {valor:.1%}. Los umbrales clásicos están definidos para el CR4. "
                f"Para clasificar el mercado con un estándar, use k = 4. "
                f"La comparación con mercados al azar sigue siendo válida para cualquier k."
            )
        else:
            if valor < CR4_MODERADO:
                nivel = "Concentración baja (competencia efectiva u oligopolio débil)"
            elif valor <= CR4_ALTO:
                nivel = "Concentración moderada (oligopolio)"
            else:
                nivel = "Concentración alta (oligopolio estrecho)"
            justificacion = (
                f"CR4 = {valor:.1%}. Según la tipología clásica de estructuras de mercado (Shepherd), "
                f"si las 4 mayores empresas tienen menos del {CR4_MODERADO:.0%} la concentración es baja, "
                f"entre {CR4_MODERADO:.0%} y {CR4_ALTO:.0%} es moderada, y sobre {CR4_ALTO:.0%} se habla de "
                f"oligopolio estrecho, con alta probabilidad de coordinación entre empresas."
            )

    elif indicador == "ID":
        if valor < ID_UMBRAL:
            nivel = "Sin dominancia relevante"
        else:
            nivel = "Dominancia relevante"
        justificacion = (
            f"ID = {valor:.3f}. Se usa el umbral de {ID_UMBRAL} (2.500 en escala 0-10.000) que aplicaba "
            f"la ex Comisión Federal de Competencia de México, creadora del índice (García Alba). "
            f"Un ID de {ID_UMBRAL} equivale a 4 empresas iguales: valores mayores indican que una o "
            f"pocas empresas explican la mayor parte de la concentración."
        )

    elif indicador == "IE":
        n_equivalente = float(np.exp(valor))
        if valor > IE_MODERADO:
            nivel = "Mercado no concentrado"
        elif valor >= IE_ALTO:
            nivel = "Mercado moderadamente concentrado"
        else:
            nivel = "Mercado altamente concentrado"
        justificacion = (
            f"IE = {valor:.3f}, equivalente a {n_equivalente:.1f} empresas iguales. La entropía no tiene "
            f"umbral oficial, por lo que se derivan de los umbrales del IHH mediante el número equivalente "
            f"de empresas: {IE_ALTO:.3f} = ln(4) y {IE_MODERADO:.3f} = ln(6,67). "
            f"Recuerde que a MAYOR entropía, MENOR concentración."
        )

    else:
        raise ValueError(f"Indicador desconocido: {indicador}")

    return {"nivel": nivel, "justificacion": justificacion}


# ---------------------------------------------------------------------
# Prueba rápida: solo se ejecuta si corres "python evaluador.py"
# ---------------------------------------------------------------------
if __name__ == "__main__":
    from indicadores import calcular_indicador
    from simulacion import simular_montecarlo

    print("1) Validaciones")
    print("  [50, 30, 20]      ->", validar_cuotas([50, 30, 20]))
    print("  [50, 30, 10]      ->", validar_cuotas([50, 30, 10]))
    print("  [33.33]*3         ->", validar_cuotas([33.33, 33.33, 33.33]))
    print("  k=3 con 3 empresas ->", validar_k(3, 3))
    print()

    print("2) Comparación de un mercado (70%, 10%, 10%, 10%) con IHH")
    cuotas = porcentajes_a_fracciones([70, 10, 10, 10])
    resultados = simular_montecarlo("IHH", n=4, iteraciones=1000, semilla=42)
    valor = calcular_indicador("IHH", cuotas)
    resumen = resumir_simulacion(resultados)
    evaluacion = evaluar_mercado(valor, resultados, "IHH")

    print(f"  IHH del mercado: {valor:.1f}")
    print(f"  Promedio al azar: {resumen['promedio']:.1f}  (p5={resumen['p5']:.1f}, p95={resumen['p95']:.1f})")
    print(f"  Percentil: {evaluacion['percentil']:.1f}%")
    print(f"  {evaluacion['mensaje']}")
    print()

    print("3) Umbrales teóricos para el mismo mercado (70%, 10%, 10%, 10%)")
    for nombre in ["CRk", "IHH", "ID", "IE"]:
        k = 2 if nombre == "CRk" else 4
        v = calcular_indicador(nombre, cuotas, k)
        print(f"  {nombre}: {clasificar_umbral(nombre, v, k)['nivel']}")
    print()
    print("  Justificación del IHH:")
    print("  " + clasificar_umbral("IHH", valor)["justificacion"])