"""
simulacion.py
-------------
Simulación Monte Carlo: genera muchos mercados al azar y calcula
el indicador elegido en cada uno. El resultado es la distribución
que después se mostrará en el histograma.
"""

import numpy as np

from indicadores import calcular_indicador

# Límites que usará la app
N_MIN, N_MAX = 2, 100
ITER_MIN, ITER_MAX, ITER_DEFECTO = 100, 10_000, 1_000


def generar_cuotas_aleatorias(n, rng=None):
    """
    Genera n cuotas de mercado al azar que suman exactamente 1.
    Usa la distribución de Dirichlet, que reparte el 100% de forma
    "justa": cualquier combinación de cuotas tiene la misma probabilidad.
    """
    if rng is None:
        rng = np.random.default_rng()
    return rng.dirichlet(np.ones(n))


def simular_montecarlo(indicador, n, iteraciones=ITER_DEFECTO, k=4, semilla=None):
    """
    Repite el experimento 'iteraciones' veces:
      1) genera un mercado al azar con n empresas,
      2) calcula el indicador elegido ("CRk", "IHH", "ID" o "IE").
    Devuelve un arreglo con todos los resultados.

    'semilla' es opcional: si se fija un número, la simulación
    da siempre los mismos resultados (útil para revisar o comparar).
    """
    if not (N_MIN <= n <= N_MAX):
        raise ValueError(f"El número de empresas debe estar entre {N_MIN} y {N_MAX}.")
    if not (ITER_MIN <= iteraciones <= ITER_MAX):
        raise ValueError(f"Las iteraciones deben estar entre {ITER_MIN} y {ITER_MAX}.")

    rng = np.random.default_rng(semilla)
    resultados = np.empty(iteraciones)

    for i in range(iteraciones):
        cuotas = generar_cuotas_aleatorias(n, rng)
        resultados[i] = calcular_indicador(indicador, cuotas, k)

    return resultados


# ---------------------------------------------------------------------
# Prueba rápida: solo se ejecuta si corres "python simulacion.py"
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # 1) Un mercado al azar debe sumar 100%
    ejemplo = generar_cuotas_aleatorias(5, np.random.default_rng(1))
    print("Cuotas de un mercado al azar con 5 empresas:", np.round(ejemplo, 3))
    print("Suma de las cuotas:", round(ejemplo.sum(), 6))
    print()

    # 2) Simulación del IHH con 5 empresas y 1000 iteraciones
    n = 5
    resultados = simular_montecarlo("IHH", n, iteraciones=1000, semilla=42)
    print(f"Simulación IHH con N={n} y {len(resultados)} iteraciones")
    print(f"  Promedio simulado: {resultados.mean():.1f}")
    print(f"  Promedio teórico:  {20000 / (n + 1):.1f}")
    print(f"  Mínimo: {resultados.min():.1f}   Máximo: {resultados.max():.1f}")