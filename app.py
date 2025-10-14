# app.py
# UI web para algoritmos en ./algos/ (usa tu "minimax-algorithm.py" tal cual).
# Flask + HTML/JS inline + alternancia (X <-> O) para TicTacToe.

import os, secrets, importlib.util
from pathlib import Path
from flask import Flask, render_template_string, session, jsonify, request

# ====== CONFIG ======
ALGO_DIR = os.environ.get("ALGO_DIR", "algos")
ALGO_FILES = [
    "minimax-algorithm.py",  # tu archivo exacto dentro de ./algos
    # Agrega más aquí si quieres: "KNN.py", "Markov.py", "Wumpus prob.py", "Astar.py"
]

# ====== utilidades para cargar módulos por ruta ======
def _algo_path(name: str) -> str:
    """Busca name dentro de ./algos (exacto) y, si no, recursivo."""
    base = Path(ALGO_DIR)
    p = base / name
    if p.exists():
        return str(p.resolve())
    for cand in base.rglob(name):
        if cand.is_file():
            return str(cand.resolve())
    raise FileNotFoundError(f"No encontré '{name}' dentro de '{ALGO_DIR}'")

def load_module_by_path(path: str, logical_name="algo_mod"):
    spec = importlib.util.spec_from_file_location(logical_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # __name__ != "__main__" (no dispara consola)
    return mod

# ====== Flask & store por sesión ======
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
_store = {}   # dict[(sid, filename)] = (ui, mod, state, label)
_choice = {}  # dict[sid] = filename actual

def _sid():
    sid = session.get("sid")
    if not sid:
        sid = secrets.token_urlsafe(16)
        session["sid"] = sid
    return sid

def _algo_name():
    sid = _sid()
    # filtra solo los que realmente existen en ./algos
    existing = []
    for f in ALGO_FILES:
        try:
            _algo_path(f)
            existing.append(f)
        except FileNotFoundError:
            pass
    if not existing:
        raise RuntimeError(f"No hay algoritmos disponibles en '{ALGO_DIR}'.")
    if sid not in _choice or _choice[sid] not in existing:
        _choice[sid] = existing[0]
    return _choice[sid]

# ====== Helpers SEGUROS para nombres ES/EN ======
def _pick_attr(obj, *names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    raise AttributeError(f"{obj.__class__.__name__} no tiene ninguno de: {names}")

def _set_attr(obj, names, value):
    # Asigna en el primer nombre que exista; si ninguno existe, crea el primero.
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return
    setattr(obj, names[0], value)

def _ensure_letters(g, human_letter=None):
    """Normaliza SIEMPRE letras de humano/bot para evitar atributos faltantes."""
    if human_letter is None:
        try:
            human_letter = _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")
        except AttributeError:
            human_letter = "X"
    bot_letter = "O" if human_letter == "X" else "X"
    _set_attr(g, ["jugadorHumano", "humanPLayer", "humanPlayer"], human_letter)
    _set_attr(g, ["jugadorBot", "botPlayer"], bot_letter)
    return human_letter, bot_letter

# ====== Adaptador específico para tu TicTacToe en "minimax-algorithm.py" ======
def ttt_init(mod, force_human_letter=None):
    g = mod.TicTacToe()  # no llamar iniciar()
    # Forzar/normalizar letras (evita AttributeError por botPlayer ausente)
    _ensure_letters(g, force_human_letter)
    BotClass = getattr(mod, "JugadorComputadora", None) or getattr(mod, "ComputerPlayer", None)
    if BotClass is None:
        raise ImportError("No encontré JugadorComputadora ni ComputerPlayer en tu módulo.")
    bot = BotClass(_pick_attr(g, "jugadorBot", "botPlayer"))
    return {"type": "ttt", "g": g, "bot": bot}

def ttt_view(state):
    g = state["g"]
    board = _pick_attr(g, "tablero", "board")
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    line = []; win = None
    for a,b,c in lines:
        if board[a] != '-' and board[a] == board[b] == board[c]:
            line = [a,b,c]; win = board[a]; break
    msg = "Empate" if '-' not in board and not win else (f"Gana {win}" if win else "Tu turno / Bot")
    acts = [f"move:{i}" for i,v in enumerate(board) if v == '-']
    return {"board": board, "line": line, "msg": msg, "actions": acts}

def ttt_step(state, action):
    if not action.startswith("move:"): return state
    i = int(action.split(":")[1])
    g = state["g"]; bot = state["bot"]
    board = _pick_attr(g, "tablero", "board")
    if not (0 <= i < 9) or board[i] != '-': return state
    human = _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")
    board[i] = human
    if _ttt_fin(g): return state
    mv = getattr(bot, "movimiento_maquina", None) or getattr(bot, "machine_move", None)
    pos = mv(board)
    if pos is not None and 0 <= pos < 9 and board[pos] == '-':
        bot_letter = _pick_attr(g, "jugadorBot", "botPlayer")
        board[pos] = bot_letter
    return state

def _ttt_win(g, letter):
    fn = getattr(g, "jugador_gana", None) or getattr(g, "is_player_win", None)
    board = _pick_attr(g, "tablero", "board")
    return fn(board, letter)

def _ttt_lleno(g):
    fn = getattr(g, "tablero_lleno", None) or getattr(g, "is_board_filled", None)
    board = _pick_attr(g, "tablero", "board")
    return fn(board)

def _ttt_fin(g):
    human = _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")
    bot   = _pick_attr(g, "jugadorBot", "botPlayer")
    return _ttt_win(g, human) or _ttt_win(g, bot) or _ttt_lleno(g)

# ====== Dispatcher por archivo ======
def init_for(filename):
    path = _algo_path(filename)
    mod = load_module_by_path(path, f"mod_{Path(filename).name.replace('.','_')}")
    # Adaptador para tu minimax:
    if Path(filename).name == "minimax-algorithm.py":
        nxt = session.get("next_human_letter", "X")   # alterna X/O entre reinicios
        st = ttt_init(mod, force_human_letter=nxt)
        session["next_human_letter"] = "O" if nxt == "X" else "X"
        return ("grid", mod, st, f"{filename} — Humano: {nxt}")
    # Futuro: si un archivo expone init/view/step (y opcional meta.ui), úsalo directo
    if hasattr(mod, "init") and hasattr(mod, "view") and hasattr(mod, "step"):
        st = mod.init()
        meta = mod.meta() if hasattr(mod, "meta") else {"ui":"custom", "name": filename}
        ui = meta.get("ui", "custom")
        return (ui, mod, st, meta.get("name", filename))
    raise RuntimeError(f"{filename} no tiene interfaz conocida (esperaba TicTacToe o init/view/step).")

def view_for(filename, mod, state):
    if Path(filename).name == "minimax-algorithm.py":
        return ttt_view(state)
    return mod.view(state)

def step_for(filename, mod, state, action):
    if Path(filename).name == "minimax-algorithm.py":
        return ttt_step(state, action)
    return mod.step(state, action)

# ====== Rutas ======
@app.route("/")
def home():
    sid = _sid()
    fname = _algo_name()
    key = (sid, fname)
    if key not in _store:
        ui, mod, st, label = init_for(fname)
        _store[key] = (ui, mod, st, label)
    ui, mod, st, label = _store[key]
    return render_template_string(TPL_HTML,
        files=ALGO_FILES, current=fname, label=label, ui=ui, initial=view_for(fname, mod, st))

@app.get("/api/state")
def api_state():
    sid = _sid(); fname = _algo_name()
    ui, mod, st, _ = _store[(sid, fname)]
    return jsonify({"ui": ui, "estado": view_for(fname, mod, st), "file": fname})

@app.post("/api/act")
def api_act():
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    sid = _sid(); fname = _algo_name()
    ui, mod, st, label = _store[(sid, fname)]
    st2 = step_for(fname, mod, st, action)
    _store[(sid, fname)] = (ui, mod, st2, label)
    return jsonify({"ok": True, "estado": view_for(fname, mod, st2)})

@app.post("/api/restart")
def api_restart():
    sid = _sid(); fname = _algo_name()
    ui, mod, st, label = init_for(fname)
    _store[(sid, fname)] = (ui, mod, st, label)
    return jsonify({"ok": True, "estado": view_for(fname, mod, st), "label": label})

@app.post("/api/set_file")
def api_set_file():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if name not in ALGO_FILES:
        return jsonify({"ok": False, "error": "Archivo no permitido"}), 400
    sid = _sid()
    _choice[sid] = name
    ui, mod, st, label = init_for(name)
    _store[(sid, name)] = (ui, mod, st, label)
    return jsonify({"ok": True, "file": name, "label": label, "estado": view_for(name, mod, st), "ui": ui})

# ====== Plantilla inline (grid para TTT) ======
TPL_HTML = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>IA – Simulador</title>
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu; }
    body { margin:0; background:#0f172a; color:#e5e7eb; }
    header { display:flex; gap:12px; align-items:center; padding:12px 16px; background:#111827; border-bottom:1px solid #1f2937; flex-wrap:wrap; }
    h1 { font-size:1.05rem; margin:0; color:#fafafa; }
    select, button { background:#1f2937; color:#e5e7eb; border:1px solid #374151; border-radius:10px; padding:8px 12px; }
    .btn { background:#2563eb; border-color:#2563eb; }
    .btn.secondary { background:#374151; border-color:#374151; }
    .container { max-width:880px; margin:16px auto; padding:0 16px; display:grid; grid-template-columns: 1fr 260px; gap:16px; }
    .card { background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; }
    .title { font-weight:600; color:#fafafa; margin-bottom:8px; }
    #board.grid { display:grid; gap:8px; grid-template-columns: repeat(3, 1fr); }
    .cell { display:flex; align-items:center; justify-content:center; background:#1f2937; border:1px solid #374151; border-radius:12px; aspect-ratio:1/1; font-size:1.8rem; transition:transform .12s ease, background .2s ease }
    .cell:hover { transform:translateY(-1px); background:#243041; cursor:pointer; }
    .cell.win { background:#064e3b !important; border-color:#047857; box-shadow:0 0 18px rgba(34,197,94,.35); }
    .disabled { opacity:.6; pointer-events:none; }
    .status { min-height:1.2em; color:#cbd5e1; }
  </style>
</head>
<body>
  <header>
    <h1>Simulador de Algoritmos</h1>
    <div>
      <label>Archivo:</label>
      <select id="selFile">
        {% for f in files %}
          <option value="{{ f }}" {{ 'selected' if f==current else '' }}>{{ f }}</option>
        {% endfor %}
      </select>
      <button id="btnRestart" class="btn secondary">Reiniciar (alterna inicio)</button>
    </div>
    <div class="status" id="label">{{ label }}</div>
  </header>

  <div class="container">
    <div class="card">
      <div class="title">Visualización</div>
      <div id="board" class="grid"></div>
    </div>
    <div class="card">
      <div class="title">Acciones</div>
      <div id="actions"></div>
      <div class="title" style="margin-top:12px;">Estado</div>
      <pre id="stateText" style="white-space:pre-wrap; font-size:.9rem; color:#cbd5e1;"></pre>
    </div>
  </div>

  <script>
  const selFile = document.getElementById('selFile');
  const btnRestart = document.getElementById('btnRestart');
  const board = document.getElementById('board');
  const actionsBox = document.getElementById('actions');
  const stateText = document.getElementById('stateText');

  function drawGrid(state) {
    board.innerHTML = '';
    const cells = state.board || Array(9).fill('-');
    for (let i=0;i<9;i++) {
      const v = cells[i];
      const c = document.createElement('div');
      c.className = 'cell';
      c.textContent = v==='-' ? '' : v;
      if (state.line && state.line.includes(i)) c.classList.add('win');
      if (v === '-') {
        c.onclick = () => act(`move:${i}`);
      } else {
        c.classList.add('disabled');
      }
      board.appendChild(c);
    }
    const msg = state.msg || '';
    stateText.textContent = msg + '\\n' + JSON.stringify(state, null, 2);
  }

  async function getState() {
    const j = await fetch('/api/state').then(r=>r.json());
    render(j.ui || 'grid', j.estado);
  }
  async function act(action) {
    const j = await fetch('/api/act',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})}).then(r=>r.json());
    if (j.ok) render('grid', j.estado);
  }
  async function restart() {
    const j = await fetch('/api/restart',{method:'POST'}).then(r=>r.json());
    document.getElementById('label').textContent = j.label || '';
    render('grid', j.estado);
  }
  async function setFile(name) {
    const j = await fetch('/api/set_file',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})}).then(r=>r.json());
    if (j.ok) {
      document.getElementById('label').textContent = j.label || name;
      render(j.ui || 'grid', j.estado);
    } else {
      alert(j.error || 'No se pudo cambiar de archivo');
    }
  }
  function render(ui, state) {
    actionsBox.innerHTML = '';
    if (Array.isArray(state.actions)) {
      state.actions.forEach(a=>{
        const b = document.createElement('button');
        b.textContent = a; b.className='btn';
        b.onclick = ()=>act(a);
        actionsBox.appendChild(b);
      });
    }
    drawGrid(state);
  }

  selFile.addEventListener('change', ()=> setFile(selFile.value));
  btnRestart.addEventListener('click', restart);
  getState();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
