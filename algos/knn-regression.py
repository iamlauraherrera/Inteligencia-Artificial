# Regresión KNN con datos de carros (kms vs precio).
# Autor: Laura Herrera— Fecha: 2025-10-14
#
# Requisitos:
#   - pandas, numpy, scikit-learn, matplotlib (opcional para graficar)
#   - Archivo CSV con columnas: 'kms', 'precio'
#
# Flujo:
#   1) Cargar datos
#   2) Escalar kms y precio con MinMax
#   3) Entrenar KNN (n_neighbors configurable)
#   4) Predecir precio para un kms dado o generar curva 0..N
#   5) (Opcional) Graficar datos crudos + curva predicha
# ------------------------------------------------------------

from __future__ import annotations
import os
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Tuple, Optional

from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor

# Matplotlib es opcional; solo lo importamos si vamos a graficar.
try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False


@dataclass
class DatosEscalados:
    """Contenedor de escaladores y arrays escalados."""
    escala_kms: MinMaxScaler
    escala_precio: MinMaxScaler
    kms_scaled: np.ndarray          # shape (n, 1)
    precio_scaled: np.ndarray       # shape (n, 1)


class KNNRegresionCarros:
    """
    Implementación compacta de KNN-Regression para (kms → precio).

    - Usa MinMaxScaler (como en tu notebook) para kms y precio.
    - Mantiene el modelo y los escaladores para invertir la escala en predicciones.
    """

    def __init__(self, n_vecinos: int = 3):
        self.n_vecinos = int(n_vecinos)
        self.df: Optional[pd.DataFrame] = None
        self.escalado: Optional[DatosEscalados] = None
        self.knn: Optional[KNeighborsRegressor] = None

    # ------------------------ Carga y validaciones ------------------------

    def cargar_csv(self, ruta_csv: str) -> pd.DataFrame:
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No encontré el archivo: {ruta_csv}")
        df = pd.read_csv(ruta_csv)

        # Validación mínima de columnas
        esperadas = {"kms", "precio"}
        if not esperadas.issubset(df.columns.str.lower()):
            raise ValueError(f"El CSV debe contener columnas: {esperadas}. "
                             f"Columnas actuales: {list(df.columns)}")

        # Normaliza nombres por si vienen con mayúsculas
        df = df.rename(columns={c: c.lower() for c in df.columns})
        # Limpieza simple: elimina filas con NaN o valores negativos
        df = df.dropna(subset=["kms", "precio"]).copy()
        df = df[(df["kms"] >= 0) & (df["precio"] >= 0)].copy()

        if df.empty:
            raise ValueError("El CSV quedó vacío tras la limpieza (revisa datos).")

        self.df = df
        return df

    # ------------------------ Escalamiento ------------------------

    def _escalar(self, df: pd.DataFrame) -> DatosEscalados:
        escala_kms = MinMaxScaler()
        escala_precio = MinMaxScaler()

        kms = df["kms"].values.reshape(-1, 1)
        precio = df["precio"].values.reshape(-1, 1)

        kms_s = escala_kms.fit_transform(kms)
        precio_s = escala_precio.fit_transform(precio)

        esc = DatosEscalados(
            escala_kms=escala_kms,
            escala_precio=escala_precio,
            kms_scaled=kms_s,
            precio_scaled=precio_s,
        )
        self.escalado = esc
        return esc

    # ------------------------ Entrenamiento ------------------------

    def entrenar(self, ruta_csv: str, n_vecinos: Optional[int] = None) -> None:
        """Carga datos, escala y entrena el KNN."""
        if n_vecinos is not None:
            self.n_vecinos = int(n_vecinos)

        df = self.cargar_csv(ruta_csv)
        esc = self._escalar(df)

        knn = KNeighborsRegressor(n_neighbors=self.n_vecinos)
        knn.fit(esc.kms_scaled, esc.precio_scaled)
        self.knn = knn

    # ------------------------ Predicción ------------------------

    def predecir_precio(self, kms: float) -> float:
        """
        Predice precio (en la escala original) para un kms dado.
        Requiere haber llamado a entrenar() antes.
        """
        if self.knn is None or self.escalado is None:
            raise RuntimeError("Primero llama a entrenar(ruta_csv).")

        kms_arr = np.array([[kms]], dtype=float)
        kms_s = self.escalado.escala_kms.transform(kms_arr)
        precio_s = self.knn.predict(kms_s)
        precio = self.escalado.escala_precio.inverse_transform(precio_s)
        return float(precio[0, 0])

    def curva_predicha(self, max_kms: int = 140_000, paso: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera (x, y) de 0..max_kms con paso ‘paso’ y devuelve kms y precios (escala original).
        Útil para graficar la curva completa como en tu notebook.
        """
        if self.knn is None or self.escalado is None:
            raise RuntimeError("Primero llama a entrenar(ruta_csv).")

        xs = np.arange(0, max(1, int(max_kms)) + 1, max(1, int(paso)), dtype=float).reshape(-1, 1)
        xs_s = self.escalado.escala_kms.transform(xs)
        ys_s = self.knn.predict(xs_s)
        ys = self.escalado.escala_precio.inverse_transform(ys_s).reshape(-1)
        return xs.reshape(-1), ys

    # ------------------------ Gráfica (opcional) ------------------------

    def graficar(self, max_kms: int = 140_000, paso: int = 1, linewidth: int = 4) -> None:
        """
        Grafica puntos originales y la curva KNN (si matplotlib está disponible).
        """
        if not _HAS_MPL:
            print("matplotlib no está disponible. Instálalo para ver la gráfica.")
            return
        if self.df is None:
            raise RuntimeError("No hay datos cargados. Llama a entrenar(ruta_csv) primero.")

        xs, ys = self.curva_predicha(max_kms=max_kms, paso=paso)

        plt.figure(figsize=(8, 5))
        # Curva predicha
        plt.plot(xs, ys, linewidth=linewidth, alpha=0.8)
        # Puntos crudos
        plt.scatter(self.df["kms"], self.df["precio"], marker="*", s=120, alpha=0.7)

        plt.title("Vehículos — KNN Regresión", fontsize=16)
        plt.xlabel("Kms recorridos")
        plt.ylabel("Precio ($)")
        plt.ticklabel_format(style="plain")
        plt.tight_layout()
        plt.show()


# ------------------------ Uso desde terminal ------------------------

def _demo():
    """
    Ejecución de ejemplo:
      $ python knn-regression.py carros.csv 3 20000

    - Entrena con 'carros.csv'
    - k vecinos = 3
    - Predice precio para 20,000 kms
    - Muestra la gráfica (si está matplotlib)
    """
    import sys
    ruta = "carros.csv"
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    kms_prueba = float(sys.argv[3]) if len(sys.argv) > 3 else 20_000

    modelo = KNNRegresionCarros(n_vecinos=k)
    modelo.entrenar(ruta, n_vecinos=k)
    pred = modelo.predecir_precio(kms_prueba)

    print(f"→ KNN(k={k}) precio estimado para {kms_prueba:,.0f} kms: {pred:,.2f}")

    # Gráfica rápida (si tienes matplotlib)
    try:
        modelo.graficar(max_kms=140_000, paso=500)
    except Exception as e:
        print(f"(Aviso) No se pudo graficar: {e}")


if __name__ == "__main__":
    _demo()
