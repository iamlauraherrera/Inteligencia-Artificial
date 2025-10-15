# ─────────────────────────────────────────────────────────────────────────────
# Algoritmo: K-NN (Regresión) — Precio de auto vs. kilometraje
# Autor: Laura Herrera · Fecha: 2025-10-14
#
# Requisitos: Solo librerías estándar (math, random).
# Uso: Importado por app.py para la interfaz web. Puede correrse en consola
#      (ver bloque __main__) para una prueba rápida.
# ─────────────────────────────────────────────────────────────────────────────

import math
import random

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ 1) Datos y utilidades                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   Representamos cada punto como (x, y)                                       ║
║   x = kilometraje (km)    y = precio (USD)                                   ║
║   Distancia 1D: |x - xq|                                                     ║
║   Regresión KNN: promedio (o ponderado) de y en los k vecinos más cercanos.  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

def distancia_1d(a: float, b: float) -> float:
    return abs(a - b)

def promedio(valores):
    if not valores: 
        return 0.0
    return sum(valores) / len(valores)

def promedio_ponderado(pares_dist_y, eps=1e-9):
    """
    pares_dist_y: lista de (dist, y)
    w_i = 1 / (dist + eps)   (si dist -> 0, el peso domina)
    """
    if not pares_dist_y:
        return 0.0
    num = 0.0
    den = 0.0
    for d, y in pares_dist_y:
        w = 1.0 / (d + eps)
        num += w * y
        den += w
    return num / den if den > 0 else 0.0


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ 2) Clase KNNRegresion                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Atributos:                                                                   ║
║   datos: list[(km: float, precio: float)]                                    ║
║   k: int                                                                     ║
║   ponderado: bool  (True = 1/dist, False = promedio simple)                  ║
║ Métodos clave:                                                               ║
║   set_k(k), set_ponderado(bool)                                              ║
║   agregar(km, precio), aleatorios(n, rango_km, rango_precio), limpiar()      ║
║   predecir(km) -> float                                                      ║
║   curva(xmin, xmax, npts) -> list[(x, y_hat)]                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class KNNRegresion:
    def __init__(self, k: int = 5, ponderado: bool = True):
        self.datos: list[tuple[float, float]] = []
        self.k = max(1, int(k))
        self.ponderado = bool(ponderado)

    def set_k(self, k: int):
        self.k = max(1, int(k))

    def set_ponderado(self, b: bool):
        self.ponderado = bool(b)

    def agregar(self, km: float, precio: float):
        self.datos.append((float(km), float(precio)))

    def limpiar(self):
        self.datos.clear()

    def aleatorios(self, n: int = 50, rango_km=(5_000, 250_000), rango_precio=(2_000, 50_000), semilla: int | None=None):
        if semilla is not None:
            random.seed(semilla)
        for _ in range(max(0, int(n))):
            km = random.uniform(*rango_km)
            # Relación negativa típica: a más km, menor precio + ruido
            base = max(rango_precio[0], rango_precio[1] - km * (rango_precio[1] - rango_precio[0]) / max(1, (rango_km[1]-rango_km[0])))
            ruido = random.uniform(-0.10, 0.10) * base
            precio = max(rango_precio[0], min(rango_precio[1], base + ruido))
            self.agregar(km, precio)

    def predecir(self, km_query: float) -> float | None:
        if not self.datos:
            return None
        # distancias
        dists = [ (distancia_1d(km, km_query), precio) for (km, precio) in self.datos ]
        dists.sort(key=lambda t: t[0])
        vecinos = dists[:self.k]
        if self.ponderado:
            yhat = promedio_ponderado(vecinos)
        else:
            yhat = promedio([y for _, y in vecinos])
        return yhat

    def curva(self, xmin: float, xmax: float, npts: int = 50) -> list[tuple[float, float]]:
        """Muestrea la 'curva' de regresión sobre el rango [xmin, xmax]."""
        if npts <= 1:
            npts = 2
        paso = (xmax - xmin) / (npts - 1)
        out = []
        for i in range(npts):
            x = xmin + i * paso
            y = self.predecir(x)
            if y is None: y = 0.0
            out.append((x, y))
        return out


# ─────────────────────────────────────────────────────────────────────────────
# Prueba rápida en consola (opcional)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    knn = KNNRegresion(k=7, ponderado=True)
    # Datos de ejemplo sintéticos
    knn.aleatorios(n=60, rango_km=(10_000, 200_000), rango_precio=(3_000, 45_000), semilla=7)
    q = 120_000
    y = knn.predecir(q)
    print(f"Consulta: km={q} -> precio estimado ≈ {y:.2f} USD")
