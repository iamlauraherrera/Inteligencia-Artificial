# Autor: Laura Herrera — Fecha: 2025-10-14

import os, sys, secrets, importlib.util
from pathlib import Path
from typing import Dict, Tuple
from flask import Flask, render_template, jsonify, request, session, send_from_directory
# Para cadenas de markov
import re
from urllib.parse import urlparse, urlencode, quote, unquote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Archivos de algoritmos disponibles (rutas relativas)
ALGO_FILES = [
    "algos/minimax-algorithm.py",
    "algos/a-algorithm.py",   
    "algos/knn-algorithm.py",
    "algos/wumpus-algorithm.py",
    "algos/markov-algorithm.py",
]

# ---------------- Utilidades de carga dinámica ----------------
def _algo_key(name: str) -> str:
    return Path(name).name  # filename

def _algo_find(name: str) -> Path:
    for f in ALGO_FILES:
        if _algo_key(f) == name:
            return Path(f).resolve()
    for cand in Path(".").rglob(name):
        if cand.is_file():
            return cand.resolve()
    raise FileNotFoundError(f"No encontré {name}")

def load_module_by_path(path: Path, logical_name: str):
    spec = importlib.util.spec_from_file_location(logical_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[logical_name] = mod
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

def _sid() -> str:
    sid = session.get("sid")
    if not sid:
        sid = secrets.token_urlsafe(16)
        session["sid"] = sid
    return sid
# ---------- PROXY GUTENBERG (evita CORS) ----------
_ALLOWED_NETLOCS = {"www.gutenberg.org", "gutenberg.org"}

def _http_text_get(url: str, timeout: float = 20.0) -> str:
    """Descarga texto usando urllib (sin dependencias externas)."""
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AI-Lab/1.0",
        "Accept": "text/plain, text/*;q=0.9, */*;q=0.8",
    })
    with urlopen(req, timeout=timeout) as r:
        raw = r.read()
    # decodificación: intentamos utf-8 y latin-1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")

_GUT_TXT_PATTERNS = [
    re.compile(r'href="([^"]+\.txt\.utf-8)"', re.I),
    re.compile(r'href="([^"]+pg\d+\.txt)"', re.I),
    re.compile(r'href="([^"]+/\d+(?:-\d+)?\.txt)"', re.I),
]

def _resolve_gutenberg_url(user_url: str) -> str:
    """
    ejemplo de aceptacion:
      - Página de libro: https://www.gutenberg.org/ebooks/11335
      - TXT directo   : https://www.gutenberg.org/ebooks/11335.txt.utf-8
    Devuelve URL TXT válida. Si .txt.utf-8 falla, busca el enlace 'Plain Text' en la página.
    """
    pu = urlparse(user_url)
    if pu.scheme not in ("http", "https"):
        raise ValueError("URL no válida (solo http/https)")
    if pu.netloc not in _ALLOWED_NETLOCS:
        raise ValueError("Dominio no permitido en proxy (solo gutenberg.org)")

    # Si ya es TXT, devolver tal cual
    if pu.path.lower().endswith(".txt") or pu.path.lower().endswith(".txt.utf-8"):
        return user_url

    # Si es índice general /ebooks -> pedimos un libro específico
    if pu.path.rstrip("/") == "/ebooks":
        raise ValueError("Abre un libro específico (p. ej. /ebooks/2000).")

    # ¿Coincide /ebooks/<id>?
    m = re.search(r"/ebooks/(\d+)", pu.path)
    if not m:
        # No sé resolver otras rutas
        return user_url

    book_id = m.group(1)
    # 1) Primer intento: .txt.utf-8
    candidate = f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8"
    try:
        txt = _http_text_get(candidate)
        # Heurística simple: si parece HTML, no sirve
        if "<html" in txt.lower():
            raise ValueError("No es texto plano.")
        return candidate
    except Exception:
        # 2) Fallback: abrir la página del libro y raspar enlace TXT
        page_url = f"https://www.gutenberg.org/ebooks/{book_id}"
        html = _http_text_get(page_url)
        href = None
        for pat in _GUT_TXT_PATTERNS:
            m2 = pat.search(html)
            if m2:
                href = m2.group(1)
                break
        if not href:
            raise ValueError("No encontré 'Plain Text' para este libro.")
        # Normalizar href
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://www.gutenberg.org" + href
        elif not href.startswith("http"):
            href = "https://www.gutenberg.org/" + href.lstrip("/")
        return href
# ---------------- Estado en memoria por sesión+archivo ----------------
# { (sid, algo_name) : (ui, mod, state_dict, label) }
_STORE: Dict[Tuple[str,str], Tuple[str, object, dict, str]] = {}

def _pick_attr(obj, *names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    raise AttributeError(f"{obj.__class__.__name__} no tiene {names}")

def _set_attr(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return
    setattr(obj, names[0], value)

# ---------------- Adaptador Minimax (TicTacToe) ----------------
def _ttt_init(mod):
    g = mod.TicTacToe()
    try:
        _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")
        _pick_attr(g, "jugadorBot", "botPlayer")
    except Exception:
        _set_attr(g, ["jugadorHumano","humanPLayer","humanPlayer"], "X")
        _set_attr(g, ["jugadorBot","botPlayer"], "O")
    BotClass = getattr(mod, "JugadorComputadora", None) or getattr(mod, "ComputerPlayer", None)
    bot = BotClass(_pick_attr(g, "jugadorBot", "botPlayer"))
    return {"g": g, "bot": bot, "fin": False}

def _ttt_status(g):
    win = getattr(g, "jugador_gana", None) or getattr(g, "is_player_win", None)
    full = getattr(g, "tablero_lleno", None) or getattr(g, "is_board_filled", None)
    board = _pick_attr(g, "tablero", "board")
    if win(board, "X"): return "Gana X"
    if win(board, "O"): return "Gana O"
    if full(board): return "Empate"
    x = sum(1 for c in board if c == "X")
    o = sum(1 for c in board if c == "O")
    return f"Turno de {'X' if x==o else 'O'}"

def _ttt_view(state):
    g = state["g"]
    board = _pick_attr(g, "tablero", "board")
    msg = _ttt_status(g)
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    winline = []
    if msg.startswith("Gana"):
        w = msg[-1]
        for a,b,c in lines:
            if board[a]==board[b]==board[c]==w:
                winline=[a,b,c]; break

    # >>> NUEVO: exponer letras para HUD y auto-IA
    humano = _pick_attr(g, "jugadorHumano","humanPLayer","humanPlayer")
    ia     = _pick_attr(g, "jugadorBot","botPlayer")

    return {
        "board": board,
        "winline": winline,
        "msg": msg,
        "humano": humano,
        "ia": ia
    }

def _ttt_step(state, action: str):
    g = state["g"]; bot = state["bot"]
    board = _pick_attr(g, "tablero", "board")
    if action == "reset":
        for i in range(9): board[i] = "-"
        state["fin"] = False
        return state
    if action.startswith("move:") and not state["fin"]:
        i = int(action.split(":")[1])
        if 0 <= i < 9 and board[i] == "-":
            human = _pick_attr(g, "jugadorHumano","humanPLayer","humanPlayer")
            board[i] = human
            if not _ttt_status(g).startswith("Turno"): state["fin"] = True
        return state
    if action == "ai" and not state["fin"]:
        mv = getattr(bot, "movimiento_maquina", None) or getattr(bot, "machine_move", None)
        pos = mv(board)
        if pos is not None and 0 <= pos < 9 and board[pos] == "-":
            botL = _pick_attr(g, "jugadorBot","botPlayer")
            board[pos] = botL
        if not _ttt_status(g).startswith("Turno"): state["fin"] = True
        return state
    return state
# ---------------- Adaptador A* (web, rápido y con random walls) ----------------
import heapq, random

def _astar_init(mod):
    n = 50
    return {
        "n": n,
        "cells": [0]*(n*n),   # 0=libre, 1=pared
        "origen": None,
        "meta": None,
        "frames": [],
        "idx": 0,
        "path": [],
        "msg": "Coloca paredes (izq/der arrastre). Shift=Origen, Alt=Meta, Espacio=Ejecutar, C=Limpiar."
    }

def _astar_view(state):
    fr = state["frames"][state["idx"]] if state.get("frames") else {}
    parcial = []
    if fr.get("actual") is not None:
        padre = dict(fr.get("padre", []))
        cur = fr["actual"]
        while cur in padre:
            parcial.append(cur)
            cur = padre[cur]
        if state["origen"] is not None:
            parcial.append(state["origen"])
        parcial = list(reversed(parcial))

    return {
        "n": state["n"], "cells": state["cells"],
        "origen": state["origen"], "meta": state["meta"],
        "path": state.get("path", []),
        "msg": state.get("msg",""),
        "frames_len": len(state.get("frames",[])),
        "frame_idx": state.get("idx",0),
        "visitados": (fr.get("visitados", []) or []),
        "frontera":  (fr.get("frontera", []) or []),
        "actual":    fr.get("actual", None),
        "g_actual":  fr.get("g_actual", None),
        "f_actual":  fr.get("f_actual", None),
        "padre":     fr.get("padre", []),
        "path_parcial": parcial,
    }

def _astar_step(state, action: str, mod):
    def ok(i): return 0 <= i < state["n"]*state["n"]

    if action == "clear":
        n = state["n"]
        state.update({"cells":[0]*(n*n),"frames":[],"idx":0,"path":[],"origen":None,"meta":None,"msg":"Limpio"})
        return state

    if action == "run":
        s, t = state["origen"], state["meta"]
        if s is None or t is None:
            state["msg"]="Debe fijar origen y meta (Shift/Alt + clic)."; return state
        if state["cells"][s]==1 or state["cells"][t]==1:
            state["msg"]="Origen/Meta no pueden ser pared."; return state
        out = _astar_compute_frames(state["n"], state["cells"], s, t)
        state["frames"] = out.get("frames", [])
        state["idx"] = 0
        state["path"] = out.get("camino", [])
        state["msg"] = "Listo" if state["path"] else "Sin solución"
        return state

    if action == "next":
        if state.get("frames"): state["idx"] = min(state["idx"]+1, len(state["frames"])-1)
        return state

    if action == "prev":
        if state.get("frames"): state["idx"] = max(state["idx"]-1, 0)
        return state

    if action.startswith("toggle:"):
        i = int(action.split(":")[1])
        if ok(i) and i not in (state.get("origen"), state.get("meta")):
            state["cells"][i] = 0 if state["cells"][i]==1 else 1
            state["frames"]=[]; state["path"]=[]; state["msg"]="Pared actualizada"
        return state

    if action.startswith("paint:"):
        # paint:<idx>:<0|1>
        _, idx, val = action.split(":")
        i, v = int(idx), int(val)
        if ok(i) and i not in (state.get("origen"), state.get("meta")) and v in (0,1):
            state["cells"][i] = v
            state["frames"]=[]; state["path"]=[]; state["msg"]="Pared actualizada"
        return state

    if action.startswith("bulk:"):
        # bulk:<0|1>:i1,i2,i3
        _, v, csv = action.split(":")
        v = int(v)
        if v in (0,1):
            for tok in csv.split(","):
                if not tok: continue
                i = int(tok)
                if ok(i) and i not in (state.get("origen"), state.get("meta")):
                    state["cells"][i] = v
            state["frames"]=[]; state["path"]=[]; state["msg"]="Pared actualizada (lote)"
        return state

    if action.startswith("set_origen:"):
        i = int(action.split(":")[1])
        if ok(i) and state["cells"][i]==0 and i != state.get("meta"):
            state["origen"]=i; state["frames"]=[]; state["path"]=[]; state["msg"]="Origen cambiado"
        return state

    if action.startswith("set_meta:"):
        i = int(action.split(":")[1])
        if ok(i) and state["cells"][i]==0 and i != state.get("origen"):
            state["meta"]=i; state["frames"]=[]; state["path"]=[]; state["msg"]="Meta cambiada"
        return state

    if action.startswith("random:"):
        # random:<p> con p in [0,1] (limitamos a 0.6)
        p = float(action.split(":")[1])
        p = max(0.0, min(0.6, p))
        n = state["n"]; s, t = state.get("origen"), state.get("meta")
        for i in range(n*n):
            if i==s or i==t: continue
            state["cells"][i] = 1 if random.random() < p else 0
        state["frames"]=[]; state["path"]=[]; state["msg"] = f"Pared aleatoria {int(p*100)}%"
        return state

    return state

# --- A* mínimo (Manhattan, 4-dir) para generar frames como en el video ---
def _to_rc(idx, n): return divmod(idx, n)
def _to_idx(r, c, n): return r*n + c
def _h(a, b, n):
    ra, ca = _to_rc(a, n); rb, cb = _to_rc(b, n)
    return abs(ra-rb)+abs(ca-cb)

def _vecinos(i, n, libres):
    r,c = _to_rc(i, n)
    if r+1<n and libres[_to_idx(r+1,c,n)]==1: yield _to_idx(r+1,c,n)
    if r-1>=0 and libres[_to_idx(r-1,c,n)]==1: yield _to_idx(r-1,c,n)
    if c+1<n and libres[_to_idx(r,c+1,n)]==1: yield _to_idx(r,c+1,n)
    if c-1>=0 and libres[_to_idx(r,c-1,n)]==1: yield _to_idx(r,c-1,n)

def _astar_compute_frames(n, cells, origen, meta):
    libres = [1 if cells[k]==0 else 0 for k in range(n*n)]
    s, t = origen, meta
    if libres[s]!=1 or libres[t]!=1:
        return {"frames": [], "camino": []}

    g = {s: 0.0}
    f = {s: float(_h(s,t,n))}
    came = {}
    visit = set()
    open_set = {s}
    heap = [(f[s], 0, s)]
    tie = 0
    frames = []

    def snap(actual):
        frames.append({
            "actual": actual,
            "visitados": sorted(list(visit)),
            "frontera": [x for (_,__,x) in heap if x in open_set],
            "g_actual": None if actual is None else g.get(actual),
            "f_actual": None if actual is None else f.get(actual),
            "padre": list(came.items())
        })

    snap(None)
    while heap:
        _, __, u = heapq.heappop(heap)
        if u not in open_set: continue
        open_set.remove(u)
        visit.add(u)
        snap(u)

        if u == t:
            path=[t]
            while path[-1] in came:
                path.append(came[path[-1]])
                if path[-1]==s: break
            path.reverse()
            return {"frames": frames, "camino": path}

        for v in _vecinos(u, n, libres):
            cand = g[u] + 1.0
            if cand < g.get(v, float("inf")):
                came[v] = u
                g[v] = cand
                f[v] = cand + _h(v, t, n)
                if v not in open_set and v not in visit:
                    tie += 1
                    heapq.heappush(heap, (f[v], tie, v))
                    open_set.add(v)

    return {"frames": frames, "camino": []}
# ---------------- Adaptador Wumpus (probabilístico) ----------------
from typing import Any

def _wumpus_init(mod):
    Mundo = getattr(mod, "MundoWumpusProb")
    mundo = Mundo(n=6, p_pozos=0.15, semilla=None)
    snap = mundo.snapshot("Inicio.")
    return {
        "mundo": mundo,
        "hist": [snap],   # historial de snapshots para prev/next
        "idx": 0
    }

def _wumpus_view(state):
    # devuelve el snapshot visible según idx
    if not state["hist"]:
        return {}
    return state["hist"][state["idx"]]

def _wumpus_step(state, action: str, mod):
    mundo = state["mundo"]
    def push(snap):
        # si estamos en medio del timeline y avanzamos, truncar lo que sigue
        if state["idx"] < len(state["hist"])-1:
            state["hist"] = state["hist"][:state["idx"]+1]
        state["hist"].append(snap)
        state["idx"] = len(state["hist"])-1

    if action == "clear":
        mundo.reiniciar(n=6, p=0.15, semilla=None)
        state["hist"] = [mundo.snapshot("Inicio.")]
        state["idx"] = 0
        return state

    if action.startswith("random:"):
        # random:<p> donde p ∈ [0, 0.35]
        p = float(action.split(":")[1])
        p = max(0.0, min(0.35, p))
        mundo.reiniciar(n=6, p=p, semilla=None)
        state["hist"] = [mundo.snapshot(f"Nuevo mundo (pozos={int(p*100)}%).")]
        state["idx"] = 0
        return state

    if action == "step":
        snap = mundo.paso()
        push(snap)
        return state

    if action == "run":
        # avanza hasta terminar o tope de pasos para no colgar
        for _ in range(200):
            snap = mundo.paso()
            push(snap)
            if snap.get("gano") or not snap.get("vivo", 1):
                break
        return state

    if action == "prev":
        if state["idx"] > 0:
            state["idx"] -= 1
        return state

    if action == "next":
        if state["idx"] < len(state["hist"])-1:
            state["idx"] += 1
        return state

    return state
# ---------------- Adaptador Markov (n-gramas) ----------------
from urllib.parse import unquote

def _markov_init(mod):
    # estado inicial
    orden = 2
    corpus = getattr(mod, "ai_corpus", "")
    Modelo = getattr(mod, "CadenaMarkov")
    m = Modelo(orden)
    m.entrenar(corpus)
    st = {
        "modelo": m,
        "orden": orden,
        "corpus": corpus,
        "generado": [],
        "estado": tuple(["<START>"]*orden),
        "msg": "",
    }
    return st

def _markov_view(state):
    m = state["modelo"]
    est = state["estado"]
    dist = m.dist_siguiente(est)
    # ordenar por prob desc y quedarse con top 12
    filas = []
    if dist:
        # obtener conteos crudos también
        cnts = m.transiciones.get(est, {})
        filas = sorted([(w, p, cnts[w]) for w,p in dist.items()], key=lambda t: t[1], reverse=True)[:12]
    return {
        "orden": state["orden"],
        "corpus": state["corpus"],
        "generado": state["generado"],
        "estado_actual": list(est),
        "distribucion": filas,  # [ [palabra, prob, conteo] ]
        "vocab": len({w for c in m.transiciones.values() for w in c.keys()}),
        "estados": len(m.estados),
        "transiciones": sum(sum(c.values()) for c in m.transiciones.values()),
    }

def _markov_step(state, action: str, mod):
    m = state["modelo"]

    if action == "reset":
        state.update(_markov_init(mod))
        return state

    if action.startswith("set_order:"):
        k = max(1, int(action.split(":")[1]))
        state["orden"] = k
        # re-entrenar con el mismo corpus
        Modelo = getattr(mod, "CadenaMarkov")
        m2 = Modelo(k)
        m2.entrenar(state["corpus"])
        state["modelo"] = m2
        state["estado"] = tuple(["<START>"]*k)
        state["generado"] = []
        return state

    if action.startswith("set_corpus:"):
        txt_enc = action.split(":",1)[1]
        txt = unquote(txt_enc)
        state["corpus"] = txt
        return state

    if action == "train":
        m = getattr(mod, "CadenaMarkov")(state["orden"])
        m.entrenar(state["corpus"])
        state["modelo"] = m
        state["estado"] = tuple(["<START>"]*state["orden"])
        state["generado"] = []
        return state

    if action.startswith("gen:"):
        n = max(1, int(action.split(":")[1]))
        gen = m.generar(n)
        state["generado"] = gen
        # deja el estado en <START>… para nueva simulación
        state["estado"] = tuple(["<START>"]*state["orden"])
        return state

    if action == "step":
        nuevo, tok = m.paso(state["estado"])
        if tok is None:
            # no hay transición — reinicia estado
            state["estado"] = tuple(["<START>"]*state["orden"])
        elif tok == "<END>":
            state["estado"] = tuple(["<START>"]*state["orden"])
        else:
            state["estado"] = nuevo
            state["generado"].append(tok)
        return state

    return state
# ---------------- Adaptador Markov (n-gramas) ------------------------
from urllib.parse import unquote

def _markov_init(mod):
    orden = 2
    corpus = getattr(mod, "ai_corpus", "")
    Modelo = getattr(mod, "CadenaMarkov")
    m = Modelo(orden)
    m.entrenar(corpus)
    st = {
        "modelo": m,
        "orden": orden,
        "corpus": corpus,
        "generado": [],
        "estado": tuple(["<START>"]*orden),
        "topn": 12,
        "autospeed": 200,
        "seed": None,
        "msg": "",
    }
    return st

def _markov_view(state):
    m = state["modelo"]
    est = state["estado"]
    dist = m.dist_siguiente(est)
    filas = []
    if dist:
        cnts = m.transiciones.get(est, {})
        topn = int(state.get("topn", 12))
        filas = sorted([(w, p, cnts[w]) for w,p in dist.items()], key=lambda t: t[1], reverse=True)[:topn]
    return {
        "orden": state["orden"],
        "corpus": state["corpus"],
        "generado": state["generado"],
        "estado_actual": list(est),
        "distribucion": filas,
        "vocab": len({w for c in m.transiciones.values() for w in c.keys()}),
        "estados": len(m.estados),
        "transiciones": sum(sum(c.values()) for c in m.transiciones.values()),
        "topn": state.get("topn", 12),
        "autospeed": state.get("autospeed", 200),
    }

def _markov_step(state, action: str, mod):
    if action == "reset":
        state.update(_markov_init(mod))
        return state

    if action.startswith("set_order:"):
        k = max(1, int(action.split(":")[1]))
        state["orden"] = k
        Modelo = getattr(mod, "CadenaMarkov")
        m2 = Modelo(k)
        m2.entrenar(state["corpus"])
        state["modelo"] = m2
        state["estado"] = tuple(["<START>"]*k)
        state["generado"] = []
        return state

    if action.startswith("set_corpus:"):
        txt_enc = action.split(":",1)[1]
        txt = unquote(txt_enc)
        state["corpus"] = txt
        return state

    if action == "train":
        Modelo = getattr(mod, "CadenaMarkov")
        m = Modelo(state["orden"])
        m.entrenar(state["corpus"])
        state["modelo"] = m
        state["estado"] = tuple(["<START>"]*state["orden"])
        state["generado"] = []
        return state

    if action.startswith("gen:"):
        n = max(1, int(action.split(":")[1]))
        if state.get("seed") is not None:
            import random as _r; _r.seed(state["seed"])
        gen = state["modelo"].generar(n)
        state["generado"] = gen
        state["estado"] = tuple(["<START>"]*state["orden"])
        return state

    if action == "step":
        if state.get("seed") is not None:
            import random as _r; _r.seed(state["seed"])
        nuevo, tok = state["modelo"].paso(state["estado"])
        if tok is None or tok == "<END>":
            state["estado"] = tuple(["<START>"]*state["orden"])
        else:
            state["estado"] = nuevo
            state["generado"].append(tok)
        return state

    if action.startswith("set_topn:"):
        t = max(1, min(50, int(action.split(":")[1])))
        state["topn"] = t
        return state

    if action.startswith("set_autospeed:"):
        sp = max(50, int(action.split(":")[1]))
        state["autospeed"] = sp
        return state

    if action.startswith("set_seed:"):
        sd = int(action.split(":")[1])
        state["seed"] = sd
        return state

    if action.startswith("set_start:"):
        txt = unquote(action.split(":",1)[1]).strip()
        toks = [t for t in txt.split() if t]
        k = state["orden"]
        if len(toks) < k:
            toks = (["<START>"]*(k-len(toks))) + toks
        else:
            toks = toks[-k:]
        state["estado"] = tuple(toks)
        state["generado"] = []
        return state

    return state
# ---------------- Adaptador kNN  ------------------------

# ----------------------------------------------------- Inicialización por archivo ------------------------------------------------
def init_for(algo_name: str):
    path = _algo_find(algo_name)
    mod = load_module_by_path(path, f"mod_{Path(algo_name).name.replace('.','_')}")
    name = Path(algo_name).name
    if name == "minimax-algorithm.py":
        return ("ttt", mod, _ttt_init(mod), "TicTacToe (Minimax)")
    if name == "a-algorithm.py":
        return ("astar", mod, _astar_init(mod), "Laberinto A* (web)")
    if name == "wumpus-algorithm.py":
        return ("wumpus", mod, _wumpus_init(mod), "Wumpus (probabilístico)")
    if name == "markov-algorithm.py":
        return ("markov", mod, _markov_init(mod), "Cadena de Markov (n-gramas)")
    return ("static", mod, {}, f"{name}")

def view_for(algo_name: str, mod, state):
    name = Path(algo_name).name
    if name == "minimax-algorithm.py": return _ttt_view(state)
    if name == "a-algorithm.py": return _astar_view(state)
    if name == "wumpus-algorithm.py": return _wumpus_view(state)
    if name == "markov-algorithm.py": return _markov_view(state)
    return {}

def step_for(algo_name: str, mod, state, action):
    name = Path(algo_name).name
    if name == "minimax-algorithm.py": return _ttt_step(state, action)
    if name == "a-algorithm.py": return _astar_step(state, action, mod)
    if name == "wumpus-algorithm.py": return _wumpus_step(state, action, mod)
    if name == "markov-algorithm.py": return _markov_step(state, action, mod)
    return state

# ---------------- Portada desde docs/ ----------------
@app.route("/")
def root_index():
    if Path("docs/index.html").exists():
        return send_from_directory("docs", "index.html")
    # fallback simple
    links = [f'<li><a href="/algo/{_algo_key(f)}">{_algo_key(f)}</a></li>' for f in ALGO_FILES]
    return f"<h1>Algoritmos</h1><ul>{''.join(links)}</ul>"

@app.route("/docs/<path:filename>")
def docs_static(filename):
    return send_from_directory("docs", filename)

@app.get("/proxy/text")
def proxy_text():
    """
    Descarga texto desde gutenberg.org evitando CORS del navegador.
    Parámetro: ?u=<url o página del libro>
    """
    u = (request.args.get("u") or "").strip()
    if not u:
        return ("Falta parámetro u", 400, {"Content-Type": "text/plain; charset=utf-8"})
    try:
        resolved = _resolve_gutenberg_url(u)
        txt = _http_text_get(resolved)
        # Heurística: si es HTML, error
        if "<html" in txt.lower():
            return ("El recurso recuperado no es texto plano.", 415, {"Content-Type": "text/plain; charset=utf-8"})
        # Limitar tamaño extremo (opcional): recortar a 2.5MB
        if len(txt) > 2_500_000:
            txt = txt[:2_500_000]
        return (txt, 200, {"Content-Type": "text/plain; charset=utf-8"})
    except (HTTPError, URLError) as e:
        return (f"Error HTTP al descargar: {e}", 502, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as e:
        return (f"Error: {e}", 400, {"Content-Type": "text/plain; charset=utf-8"})

# ---------------- Páginas por algoritmo ----------------
@app.route("/algo/<name>")
def algo_page(name: str):
    sid = _sid()
    key = (sid, name)
    if key not in _STORE:
        ui, mod, st, label = init_for(name)
        _STORE[key] = (ui, mod, st, label)
    tpl_name = name.replace(".py", ".html")
    return render_template(tpl_name, name=name)

# ---------------- APIs por algoritmo ----------------
@app.get("/api/<name>/state")
def api_state(name: str):
    sid = _sid(); key = (sid, name)
    if key not in _STORE:
        ui, mod, st, label = init_for(name)
        _STORE[key] = (ui, mod, st, label)
    ui, mod, st, label = _STORE[key]
    return jsonify({"ui": ui, "estado": view_for(name, mod, st), "label": label, "file": name})

@app.post("/api/<name>/act")
def api_act(name: str):
    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip()
    sid = _sid(); key = (sid, name)
    ui, mod, st, label = _STORE[key]
    st2 = step_for(name, mod, st, action)
    _STORE[key] = (ui, mod, st2, label)
    return jsonify({"ok": True, "estado": view_for(name, mod, st2)})

@app.post("/api/<name>/restart")
def api_restart(name: str):
    sid = _sid(); key = (sid, name)
    ui, mod, st, label = init_for(name)
    _STORE[key] = (ui, mod, st, label)
    return jsonify({"ok": True, "estado": view_for(name, mod, st)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
