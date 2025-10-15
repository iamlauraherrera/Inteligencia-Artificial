# -*- coding: utf-8 -*-
"""
KNN Regresión (kms -> precio)
--------------------------------
Archivo lógico para el adaptador Flask (app.py)

Expone:
- Clase: KNNRegresionCarros
- Funciones adaptadoras: train(), predict(), curve(), reset()

Uso típico desde app.py (pseudocódigo):
    mod = importlib(... 'algo/knn-regression.py')
    mod.train(csv='carros.csv', k=3)
    mod.predict(kms=20000)
    mod.curve(max_kms=140000, paso=1000)

Requisitos de entorno:
    - numpy, pandas, scikit-learn
Columnas esperadas en el CSV:
    'kms', 'precio' (cualquier capitalización; se normaliza a minúsculas)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor


# ----------------------------- Núcleo --------------------------------- #

@dataclass
class DatosEscalados:
    """Contenedor de escaladores y arrays escalados."""
    escala_kms: MinMaxScaler
    escala_precio: MinMaxScaler
    kms_scaled: np.ndarray          # (n, 1)
    precio_scaled: np.ndarray       # (n, 1)


class KNNRegresionCarros:
    """
    Implementación de KNN-Regression para (kms → precio).

    Flujo:
      1) cargar_csv(ruta)
      2) _escalar(df)
      3) entrenar(...)
      4) predecir_precio(kms) / curva_predicha(...)
    """

    def __init__(self, n_vecinos: int = 3):
        self.n_vecinos = int(n_vecinos)
        self.df: Optional[pd.DataFrame] = None
        self.escalado: Optional[DatosEscalados] = None
        self.knn: Optional[KNeighborsRegressor] = None
        self._csv_path: Optional[str] = None

    # ------------------------ Carga y validaciones ------------------------

    def cargar_csv(self, ruta_csv: str) -> pd.DataFrame:
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"No encontré el archivo: {ruta_csv}")
        df = pd.read_csv(ruta_csv)

        # Validar columnas (en minúsculas)
        lower_cols = [c.lower() for c in df.columns]
        df.columns = lower_cols
        esperadas = {"kms", "precio"}
        if not esperadas.issubset(set(lower_cols)):
            raise ValueError(f"El CSV debe contener columnas {esperadas}. "
                             f"Columnas actuales: {list(df.columns)}")

        # Limpieza simple: quitar NaN y negativos
        df = df.dropna(subset=["kms", "precio"]).copy()
        df = df[(df["kms"] >= 0) & (df["precio"] >= 0)].copy()
        if df.empty:
            raise ValueError("El CSV quedó vacío tras la limpieza (revisa datos).")

        self.df = df
        self._csv_path = ruta_csv
        return df

    # ----------------------------- Escalado -------------------------------

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

    # --------------------------- Entrenamiento ----------------------------

    def entrenar(self, ruta_csv: str, n_vecinos: Optional[int] = None) -> None:
        """Carga datos, escala y entrena el KNN."""
        if n_vecinos is not None:
            self.n_vecinos = int(n_vecinos)

        df = self.cargar_csv(ruta_csv)
        esc = self._escalar(df)

        knn = KNeighborsRegressor(n_neighbors=self.n_vecinos)
        knn.fit(esc.kms_scaled, esc.precio_scaled)
        self.knn = knn

    # ---------------------------- Predicciones ----------------------------

    def predecir_precio(self, kms: float) -> float:
        """
        Predice precio (escala original) para un kms dado.
        """
        if self.knn is None or self.escalado is None:
            raise RuntimeError("Primero llama a entrenar(ruta_csv).")

        kms_arr = np.array([[float(kms)]], dtype=float)
        kms_s = self.escalado.escala_kms.transform(kms_arr)
        precio_s = self.knn.predict(kms_s)
        precio = self.escalado.escala_precio.inverse_transform(precio_s)
        return float(precio[0, 0])

    def curva_predicha(self, max_kms: int = 140_000, paso: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera (x, y) de 0..max_kms con paso ‘paso’ y devuelve kms y precios (escala original).
        """
        if self.knn is None or self.escalado is None:
            raise RuntimeError("Primero llama a entrenar(ruta_csv).")

        xs = np.arange(0, max(1, int(max_kms)) + 1, max(1, int(paso)), dtype=float).reshape(-1, 1)
        xs_s = self.escalado.escala_kms.transform(xs)
        ys_s = self.knn.predict(xs_s)
        ys = self.escalado.escala_precio.inverse_transform(ys_s).reshape(-1)
        return xs.reshape(-1), ys


# ---------------------- Estado de módulo (singleton) -------------------- #

class _State:
    """Estado global simple para el adaptador."""
    def __init__(self):
        self.model: Optional[KNNRegresionCarros] = None
        self.csv: Optional[str] = None
        self.k: Optional[int] = None

STATE = _State()


def _ensure_model() -> KNNRegresionCarros:
    if STATE.model is None:
        STATE.model = KNNRegresionCarros(n_vecinos=STATE.k or 3)
    return STATE.model


# ----------------------- Funciones adaptadoras -------------------------- #

def train(csv: str = "carros.csv", k: int = 3) -> Dict[str, Any]:
    """
    Entrena el modelo global con el CSV indicado y k vecinos.
    Retorna {'ok': True, 'csv': ..., 'k': ..., 'n': <filas>} o {'ok': False, 'error': ...}
    """
    try:
        STATE.k = int(k)
        STATE.csv = csv
        model = KNNRegresionCarros(n_vecinos=STATE.k)
        model.entrenar(csv, n_vecinos=STATE.k)
        STATE.model = model
        n = len(model.df) if model.df is not None else 0
        return {"ok": True, "csv": csv, "k": STATE.k, "n": n}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def predict(kms: float) -> Dict[str, Any]:
    """
    Predice precio para 'kms' usando el modelo entrenado.
    Retorna {'ok': True, 'kms': <float>, 'precio': <float>} o {'ok': False, 'error': ...}
    """
    try:
        model = _ensure_model()
        precio = model.predecir_precio(float(kms))
        return {"ok": True, "kms": float(kms), "precio": float(precio)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def curve(max_kms: int = 140_000, paso: int = 1000) -> Dict[str, Any]:
    """
    Devuelve la curva predicha como arrays serializables (listas).
    Retorna {'ok': True, 'xs': [...], 'ys': [...]} o {'ok': False, 'error': ...}
    """
    try:
        model = _ensure_model()
        xs, ys = model.curva_predicha(max_kms=max_kms, paso=paso)
        # Convertimos a listas nativas para JSON
        return {"ok": True, "xs": xs.astype(float).tolist(), "ys": ys.astype(float).tolist()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def reset() -> Dict[str, Any]:
    """
    Limpia el estado global del módulo.
    """
    try:
        STATE.model = None
        STATE.csv = None
        STATE.k = None
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ------------------------ Mini demo CLI opcional ------------------------ #
if __name__ == "__main__":
    # Uso rápido terminal: python algo/knn-regression.py carros.csv 3 20000
    import sys
    _csv = sys.argv[1] if len(sys.argv) > 1 else "carros.csv"
    _k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    _kms = float(sys.argv[3]) if len(sys.argv) > 3 else 20000.0

    r1 = train(csv=_csv, k=_k)
    print("Entrenar:", r1)
    if r1.get("ok"):
        r2 = predict(_kms)
        print("Predecir:", r2)
        r3 = curve(140000, 5000)
        print("Curva: xs(len)=", len(r3.get("xs", [])), "ys(len)=", len(r3.get("ys", [])))
