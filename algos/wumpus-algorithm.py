"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 Mundo de Wumpus (Probabilístico, simple)                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Autor: Laura Herrera                                                         ║
║ Fecha: 2025-10-14                                                            ║
║ Descripción: Lógica mínima para simular el Wumpus World con                 ║
║              creencias probabilísticas sobre Pozos y Wumpus.                ║
║              Sin librerías externas.                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Dict, Optional

Coord = Tuple[int, int]

def vecinos(n: int, r: int, c: int) -> List[Coord]:
    out = []
    if r+1 < n: out.append((r+1, c))
    if r-1 >= 0: out.append((r-1, c))
    if c+1 < n: out.append((r, c+1))
    if c-1 >= 0: out.append((r, c-1))
    return out

def aplanar(rc: Coord, n: int) -> int:
    return rc[0]*n + rc[1]

def dentro(n: int, rc: Coord) -> bool:
    r,c = rc; return 0 <= r < n and 0 <= c < n

@dataclass
class MundoWumpusProb:
    n: int = 6
    p_pozos: float = 0.15
    semilla: Optional[int] = None

    # Estado oculto (mundo “real”)
    pozos: Set[Coord] = field(default_factory=set)
    wumpus: Coord = (0, 0)
    oro: Coord = (0, 0)
    wumpus_vivo: bool = True

    # Estado del agente
    agente: Coord = (0, 0)
    visitados: Set[Coord] = field(default_factory=lambda: {(0,0)})
    seguros: Set[Coord] = field(default_factory=lambda: {(0,0)})
    tiene_oro: bool = False
    vivo: bool = True
    gano: bool = False

    # Creencias (probabilidades por celda)
    p_pit: List[float] = field(default_factory=list)
    p_wumpus: List[float] = field(default_factory=list)

    # Historial simple (para diagnósticos si se quiere)
    pasos: int = 0

    def __post_init__(self):
        if self.semilla is not None:
            random.seed(self.semilla)
        self._generar_mundo()
        self._inicializar_creencias()

    # ---------------- Mundo y sensores ----------------
    def _generar_mundo(self):
        libres = [(r,c) for r in range(self.n) for c in range(self.n) if (r,c)!=(0,0)]
        # coloca wumpus
        self.wumpus = random.choice(libres)
        libres2 = [xy for xy in libres if xy != self.wumpus]
        # coloca oro
        self.oro = random.choice(libres2)
        libres3 = [xy for xy in libres2 if xy != self.oro]
        # coloca pozos con prob p_pozos (evita (0,0))
        self.pozos = set()
        for rc in libres3:
            if random.random() < self.p_pozos:
                self.pozos.add(rc)
        # asegúrate de que inicio no sea trampa indirecta imposible
        # (opcional) nada

    def _inicializar_creencias(self):
        N = self.n*self.n
        # pozos: asumimos priors independientes (excepto (0,0) seguro)
        self.p_pit = [self.p_pozos]*N
        self.p_pit[0] = 0.0  # (0,0) seguro

        # wumpus: single-target prior uniforme excepto (0,0)
        self.p_wumpus = [0.0]*N
        masa = N-1
        for i in range(1, N):
            self.p_wumpus[i] = 1.0/masa
        # conocimiento inicial
        self._actualizar_por_sensores(self.agente)

    def _sensores(self, rc: Coord) -> Dict[str, bool]:
        r,c = rc
        breezy = any(v in self.pozos for v in vecinos(self.n, r, c))
        stench = self.wumpus_vivo and any(v == self.wumpus for v in vecinos(self.n, r, c))
        glitter = (rc == self.oro)
        return {"brisa": breezy, "hedor": stench, "brillo": glitter}

    # ---------------- Actualizaciones de creencias (muy simples) ----------------
    def _actualizar_por_sensores(self, rc: Coord):
        """Actualiza p_pit y p_wumpus con reglas sencillas (estilo CSP probabilista)."""
        r,c = rc
        self.seguros.add(rc)
        self.visitados.add(rc)
        idx = aplanar(rc, self.n)
        self.p_pit[idx] = 0.0
        self.p_wumpus[idx] = 0.0  # asume que donde estoy no está el wumpus, claro

        s = self._sensores(rc)
        ady = vecinos(self.n, r, c)

        # Si NO hay brisa: todos adyacentes sin pozo
        if not s["brisa"]:
            for v in ady:
                self.p_pit[aplanar(v, self.n)] = 0.0
        else:
            # Hay brisa: refuerza prob en adyacentes que aún no son seguras
            for v in ady:
                k = aplanar(v, self.n)
                if v not in self.seguros:
                    self.p_pit[k] = min(0.6, max(self.p_pit[k], 0.3))

        # Si NO hay hedor: descarta wumpus en adyacentes
        if not s["hedor"]:
            for v in ady:
                self.p_wumpus[aplanar(v, self.n)] = 0.0
        else:
            # Hay hedor: concentra prob en adyacentes no visitados
            masa = 0.0
            for v in ady:
                if v not in self.visitados:
                    masa += 1.0
            for v in ady:
                k = aplanar(v, self.n)
                if v not in self.visitados:
                    self.p_wumpus[k] = 1.0/masa if masa>0 else 0.0
                else:
                    self.p_wumpus[k] = 0.0
        # normaliza p_wumpus si wumpus vivo (masa total 1 en celdas no descartadas)
        if self.wumpus_vivo:
            total = sum(self.p_wumpus)
            if total > 0:
                self.p_wumpus = [x/total for x in self.p_wumpus]
        else:
            self.p_wumpus = [0.0]*(self.n*self.n)

    # ---------------- Política simple (greedy por riesgo) ----------------
    def _frontera(self) -> Set[Coord]:
        out: Set[Coord] = set()
        for rc in self.seguros:
            for v in vecinos(self.n, rc[0], rc[1]):
                if v not in self.visitados:
                    out.add(v)
        return out

    def _riesgo(self, rc: Coord) -> float:
        k = aplanar(rc, self.n)
        rw = self.p_wumpus[k] if self.wumpus_vivo else 0.0
        return self.p_pit[k] + rw

    def proximo_mov(self) -> Optional[Coord]:
        """Elige la celda fronteriza con riesgo esperado mínimo."""
        cand = list(self._frontera())
        if not cand:
            # fallback: cualquier vecino no visitado de la posición actual
            cand = [v for v in vecinos(self.n, *self.agente) if v not in self.visitados]
        if not cand:
            return None
        cand.sort(key=self._riesgo)
        return cand[0]

    # ---------------- Paso de simulación ----------------
    def paso(self) -> Dict[str, object]:
        """Avanza un paso con la política actual. Retorna un snapshot para UI."""
        if not self.vivo or self.gano:
            return self.snapshot("Fin de simulación.")

        # Si hay oro aquí: tomarlo y ganar (simple)
        if self.agente == self.oro:
            self.tiene_oro = True
            self.gano = True
            return self.snapshot("¡Tomó el oro! Éxito.")

        # Elegir siguiente
        nxt = self.proximo_mov()
        if nxt is None:
            # nada que hacer: estancado
            return self.snapshot("Sin movimientos seguros. Estancado.")

        # Mover
        self.agente = nxt
        self.pasos += 1

        # Verificar muerte
        if nxt in self.pozos:
            self.vivo = False
            return self.snapshot("Cayó en un pozo. Fin.")
        if self.wumpus_vivo and nxt == self.wumpus:
            self.vivo = False
            return self.snapshot("El Wumpus lo devoró. Fin.")

        # Si no murió, actualizar creencias con sensores
        self._actualizar_por_sensores(nxt)

        # Si hay oro: ganar
        if nxt == self.oro:
            self.tiene_oro = True
            self.gano = True
            return self.snapshot("¡Tomó el oro! Éxito.")

        return self.snapshot("Paso realizado.")

    # ---------------- Reinicio/aleatorio ----------------
    def reiniciar(self, n: Optional[int] = None, p: Optional[float] = None, semilla: Optional[int] = None):
        if n is not None: self.n = n
        if p is not None: self.p_pozos = p
        if semilla is not None: self.semilla = semilla
        # reset básicos
        self.pozos.clear()
        self.visitados = {(0,0)}
        self.seguros = {(0,0)}
        self.agente = (0,0)
        self.tiene_oro = False
        self.vivo = True
        self.gano = False
        self.wumpus_vivo = True
        self.pasos = 0
        self._generar_mundo()
        self._inicializar_creencias()

    # ---------------- Snapshot para UI ----------------
    def snapshot(self, msg: str = "") -> Dict[str, object]:
        N = self.n*self.n
        def vbool(cond: bool) -> int: return 1 if cond else 0
        # sensores en la casilla actual
        s = self._sensores(self.agente)
        return {
            "n": self.n,
            "msg": msg,
            "agente": aplanar(self.agente, self.n),
            "oro": aplanar(self.oro, self.n),
            "wumpus_vivo": vbool(self.wumpus_vivo),
            "tiene_oro": vbool(self.tiene_oro),
            "vivo": vbool(self.vivo),
            "gano": vbool(self.gano),
            "visitados": [aplanar(rc, self.n) for rc in sorted(self.visitados)],
            "seguros":   [aplanar(rc, self.n) for rc in sorted(self.seguros)],
            "pozos":     [aplanar(rc, self.n) for rc in sorted(self.pozos)],  # OJO: la UI no debe mostrarlos (debug)
            "breeze":    vbool(s["brisa"]),
            "stench":    vbool(s["hedor"]),
            "glitter":   vbool(s["brillo"]),
            "p_pit":     [round(x,3) for x in self.p_pit],      # para overlay numérico
            "p_wumpus":  [round(x,3) for x in self.p_wumpus],   # para overlay numérico
            "pasos": self.pasos
        }
