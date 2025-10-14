# Autor: Laura Herrera — Fecha: 2025-10-14

import os, sys, secrets, importlib.util
from pathlib import Path
from typing import Dict, Tuple
from flask import Flask, render_template, jsonify, request, session, send_from_directory

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Archivos de algoritmos disponibles (rutas relativas)
ALGO_FILES = [
    "algos/minimax-algorithm.py",
    "algos/a-algorithm.py",   
    # "algos/knn-algorithm.py",
    # "algos/markov-algorithm.py",
    # "algos/wumpus-algorithm.py",
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
    return {"board": board, "winline": winline, "msg": msg}

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

# ---------------- Adaptador A* (web, SIN pygame) ----------------
def _astar_init(mod):
    n = 25
    cells = [0]*(n*n)
    origen, meta = 0, n*n-1
    return {"n":n,"cells":cells,"origen":origen,"meta":meta,"frames":[],"idx":0,"path":[],"msg":"Pinta paredes con click. Shift=Origen, Alt=Meta."}

def _astar_view(state):
    fr = state["frames"][state["idx"]] if state.get("frames") else {}
    parcial = []
    if fr.get("actual") is not None:
        padre = dict(fr.get("padre", []))
        cur = fr["actual"]
        parcial = [cur]
        while cur in padre:
            cur = padre[cur]
            parcial.append(cur)
            if cur == state["origen"]:
                break
        parcial.reverse()
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
    if action == "clear":
        state.update({"cells":[0]*(state["n"]*state["n"]),"frames":[],"idx":0,"path":[],"msg":"Limpio"})
        return state
    if action == "run":
        Lab = getattr(mod, "LaberintoAEstrella")  # de a-algorithm.py (adaptador web)
        lab = Lab(state["n"], state["cells"], state["origen"], state["meta"])
        out = lab.buscar_camino_animado()
        state["frames"] = out.get("frames", [])
        state["idx"] = 0
        state["path"] = out.get("camino", [])
        state["msg"] = "Listo" if state["path"] else "Sin solución"
        return state
    if action == "next":
        if state.get("frames"):
            state["idx"] = min(state["idx"]+1, len(state["frames"])-1)
        return state
    if action == "prev":
        if state.get("frames"):
            state["idx"] = max(state["idx"]-1, 0)
        return state
    if action.startswith("toggle:"):
        i = int(action.split(":")[1])
        if i not in (state["origen"], state["meta"]):
            state["cells"][i] = 0 if state["cells"][i]==1 else 1
            state["frames"]=[]; state["path"]=[]
            state["msg"]="Pared actualizada"
        return state
    if action.startswith("set_origen:"):
        i = int(action.split(":")[1])
        if state["cells"][i]==0 and i != state["meta"]:
            state["origen"]=i; state["frames"]=[]; state["path"]=[]
            state["msg"]="Origen cambiado"
        return state
    if action.startswith("set_meta:"):
        i = int(action.split(":")[1])
        if state["cells"][i]==0 and i != state["origen"]:
            state["meta"]=i; state["frames"]=[]; state["path"]=[]
            state["msg"]="Meta cambiada"
        return state
    return state

# ---------------- Inicialización por archivo ----------------
def init_for(algo_name: str):
    path = _algo_find(algo_name)
    mod = load_module_by_path(path, f"mod_{Path(algo_name).name.replace('.','_')}")
    name = Path(algo_name).name
    if name == "minimax-algorithm.py":
        return ("ttt", mod, _ttt_init(mod), "TicTacToe (Minimax)")
    if name == "a-algorithm.py":
        return ("astar", mod, _astar_init(mod), "Laberinto A* (web)")
    # Placeholder para los demás: solo renderiza la plantilla si existe
    return ("static", mod, {}, f"{name}")

def view_for(algo_name: str, mod, state):
    name = Path(algo_name).name
    if name == "minimax-algorithm.py": return _ttt_view(state)
    if name == "a-algorithm.py": return _astar_view(state)
    return {}

def step_for(algo_name: str, mod, state, action):
    name = Path(algo_name).name
    if name == "minimax-algorithm.py": return _ttt_step(state, action)
    if name == "a-algorithm.py": return _astar_step(state, action, mod)
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
