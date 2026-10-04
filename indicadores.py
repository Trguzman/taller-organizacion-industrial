"""
indicadores.py
--------------
Funciones para calcular indicadores de concentración de mercado.

IMPORTANTE: todas las funciones reciben las cuotas de mercado como
FRACCIONES que suman 1. Por ejemplo, 40% se escribe 0.40.
"""

import numpy as np


def _preparar(cuotas):
    """Convierte la lista de cuotas en un arreglo de NumPy para poder calcular."""
    return np.asarray(cuotas, dtype=float)


def ratio_concentracion(cuotas, k=4):
    """
    CRk: suma de las cuotas de las k empresas más grandes.
    Resultado entre 0 y 1 (por ejemplo, 0.75 = 75%).
    Si hay menos empresas que k, se suman todas.
    """
    s = _preparar(cuotas)
    k = min(k, len(s))
    ordenadas = np.sort(s)[::-1]  # de mayor a menor
    return float(ordenadas[:k].sum())


def herfindahl_hirschman(cuotas):
    """
    IHH: suma de los cuadrados de las cuotas expresadas en porcentaje.
    Escala de 0 a 10.000 (10.000 = monopolio).
    """
    s = _preparar(cuotas)
    return float(np.sum((s * 100) ** 2))


def indice_dominancia(cuotas):
    """
    ID: mide qué parte del IHH se explica por las empresas más grandes.
    Primero calcula el aporte de cada empresa al IHH (h_i = s_i^2 / suma de s^2)
    y luego suma esos aportes al cuadrado.
    Resultado entre 0 y 1 (1 = una sola empresa domina todo).
    """
    s = _preparar(cuotas)
    cuadrados = s ** 2
    aportes = cuadrados / cuadrados.sum()
    return float(np.sum(aportes ** 2))


def indice_entropia(cuotas):
    """
    IE: -suma(s_i * ln(s_i)).
    Va de 0 (monopolio) a ln(N) (todas las empresas con la misma cuota).
    OJO: a MAYOR entropía, MENOR concentración (al revés que los otros tres).
    Las empresas con cuota 0 no aportan, así que se omiten.
    """
    s = _preparar(cuotas)
    s = s[s > 0]
    return float(0.0 - np.sum(s * np.log(s)))


def calcular_indicador(nombre, cuotas, k=4):
    """
    Calcula el indicador elegido por su nombre: "CRk", "IHH", "ID" o "IE".
    Esta función la usarán después la simulación y la app.
    """
    if nombre == "CRk":
        return ratio_concentracion(cuotas, k)
    if nombre == "IHH":
        return herfindahl_hirschman(cuotas)
    if nombre == "ID":
        return indice_dominancia(cuotas)
    if nombre == "IE":
        return indice_entropia(cuotas)
    raise ValueError(f"Indicador desconocido: {nombre}")


# ---------------------------------------------------------------------
# Prueba rápida: solo se ejecuta si corres "python indicadores.py"
# ---------------------------------------------------------------------
if __name__ == "__main__":
    ejemplos = {
        "Monopolio (1 empresa con 100%)": [1.0],
        "4 empresas iguales (25% c/u)": [0.25, 0.25, 0.25, 0.25],
        "3 empresas (50%, 30%, 20%)": [0.50, 0.30, 0.20],
    }

    for descripcion, cuotas in ejemplos.items():
        print(descripcion)
        print(f"  CR2 = {ratio_concentracion(cuotas, k=2):.4f}")
        print(f"  IHH = {herfindahl_hirschman(cuotas):.1f}")
        print(f"  ID  = {indice_dominancia(cuotas):.4f}")
        print(f"  IE  = {indice_entropia(cuotas):.4f}")
        print()