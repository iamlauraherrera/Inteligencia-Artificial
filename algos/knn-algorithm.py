# ─────────────────────────────────────────────────────────────────────────────
# Algoritmo: K-Nearest Neighbors (K-NN) — Lógica mínima para simulación web
# Autor: Laura Herrera · Fecha: 2025-10-14
#
# Requisitos: Solo librerías estándar (math, random).
# Uso: Importado por app.py para la interfaz web. También puede ejecutarse
#      en consola para una prueba rápida (ver bloque __main__).
# ─────────────────────────────────────────────────────────────────────────────

import math
import random

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ 1) Funciones utilitarias                                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ distancia_euclidiana(p, q): retorna float                                   ║
║   p=(x1,y1), q=(x2,y2)                                                       ║
║ voto_mayoritario(labels): resuelve empates por orden alfabético              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
def distancia_euclidiana(p, q):
    (x1, y1), (x2, y2) = p, q
    dx, dy = (x1 - x2), (y1 - y2)
    return math.hypot(dx, dy)

def voto_mayoritario(labels):
    conteo = {}
    for l in labels:
        conteo[l] = conteo.get(l, 0) + 1
    # mayor frecuencia; desempate: etiqueta menor alfabéticamente
    mejor = max(conteo.items(), key=lambda kv: (kv[1], -ord(kv[0][0])))
    # mejor = (label, freq)
    # En caso de varias letras con misma freq y primer char igual, orden total:
    empatadas = [k for k, v in conteo.items() if v == mejor[1]]
    return sorted(empatadas)[0]

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ 2) Clase KNNModelo                                                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Atributos:                                                                   ║
║   puntos: list[(x:float, y:float, clase:str)]  # coords normalizadas [0..1]  ║
║   k: int                                                                     ║
║   clases: set[str]                                                           ║
║ Métodos (resumen):                                                           ║
║   agregar(x,y,c), limpiar(), aleatorios(n, clases)                           ║
║   predecir(x,y,k=None) -> (label, vecinos:[(idx, dist)])                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class KNNModelo:
    def __init__(self, k: int = 3):
        self.puntos = []     # [(x, y, 'A'|'B'|...)]
        self.k = max(1, int(k))
        self.clases = set()

    def set_k(self, k: int):
        self.k = max(1, int(k))

    def agregar(self, x: float, y: float, clase: str):
        x = min(1.0, max(0.0, float(x)))
        y = min(1.0, max(0.0, float(y)))
        clase = str(clase)
        self.puntos.append((x, y, clase))
        self.clases.add(clase)

    def limpiar(self):
        self.puntos.clear()
        self.clases.clear()

    def aleatorios(self, n: int = 40, clases=("A", "B")):
        for _ in range(max(0, int(n))):
            self.agregar(random.random(), random.random(), random.choice(clases))

    def predecir(self, x: float, y: float, k: int | None = None):
        """Devuelve (label_predicha, vecinos_ordenados)
        vecinos_ordenados = lista de (indice_en_dataset, distancia) de tamaño k.
        """
        if not self.puntos:
            return None, []
        kk = max(1, int(k if k is not None else self.k))
        # Distancias
        dists = []
        for i, (px, py, c) in enumerate(self.puntos):
            d = distancia_euclidiana((x, y), (px, py))
            dists.append((i, d))
        dists.sort(key=lambda t: t[1])
        vecinos = dists[:kk]
        labels = [self.puntos[i][2] for i, _ in vecinos]
        pred = voto_mayoritario(labels)
        return pred, vecinos


# ─────────────────────────────────────────────────────────────────────────────
# Prueba rápida en consola (opcional)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Demo KNN en consola (coords normalizadas [0..1])")
    knn = KNNModelo(k=3)
    knn.aleatorios(10, clases=("A", "B", "C"))
    px, py = 0.5, 0.5
    pred, vecinos = knn.predecir(px, py)
    print(f"Consulta=({px:.2f},{py:.2f}) -> clase={pred}, vecinos={vecinos[:3]}")