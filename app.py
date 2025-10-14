# app.py
# Interfaz web para TicTacToe con motor en "minimax-algorithm.py" (cargado por ruta).
# Un solo archivo: servidor Flask + plantilla HTML/JS inline + alternancia de inicio.

import os, secrets, importlib.util
from flask import Flask, render_template_string, redirect, url_for, session, jsonify

# === Carga del motor por ruta (soporta nombre con guion) ===
RUTA_JUEGO = os.environ.get("JUEGO_PATH", "minimax-algorithm.py")

def cargar_modulo_por_ruta(ruta, nombre_logico="juego_mod"):
    spec = importlib.util.spec_from_file_location(nombre_logico, ruta)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el módulo desde {ruta}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # __name__ no es "__main__", así no dispara consola
    return mod

juego = cargar_modulo_por_ruta(RUTA_JUEGO)

# === Helpers SEGUROS para nombres ES/EN ===
def _pick_attr(obj, *names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    raise AttributeError(f"{obj.__class__.__name__} no tiene ninguno de: {names}")

def _pick_method(obj, *names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    raise AttributeError(f"{obj.__class__.__name__} no define ninguno de: {names}")

def _tablero(g):
    return _pick_attr(g, "tablero", "board")

def _humano(g):
    return _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")

def _bot(g):
    return _pick_attr(g, "jugadorBot", "botPlayer")

def _gana(g, letra):
    fn = _pick_method(g, "jugador_gana", "is_player_win")
    return fn(_tablero(g), letra)

def _lleno(g):
    fn = _pick_method(g, "tablero_lleno", "is_board_filled")
    return fn(_tablero(g))

def _set_attr(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return
    raise AttributeError(f"No puedo asignar {names} en {obj.__class__.__name__}")

def _set_letters(g, human_letter):
    bot_letter = "O" if human_letter == "X" else "X"
    _set_attr(g, ["jugadorHumano", "humanPLayer", "humanPlayer"], human_letter)
    _set_attr(g, ["jugadorBot", "botPlayer"], bot_letter)
    return human_letter, bot_letter

WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),
             (0,3,6),(1,4,7),(2,5,8),
             (0,4,8),(2,4,6)]

def _linea_ganadora(board):
    for a,b,c in WIN_LINES:
        if board[a] != '-' and board[a] == board[b] == board[c]:
            return [a,b,c], board[a]
    return [], None

# === Flask app (memoria por sesión) ===
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
_store = {}

def _nueva_partida():
    # Alterna quién empieza: guardamos la siguiente letra del humano en sesión
    next_h = session.get("next_human_letter", "X")  # primera vez: humano=X
    g = juego.TicTacToe()  # no llamamos iniciar()
    h, b = _set_letters(g, next_h)  # forzamos letras (anula random del motor)

    BotClass = getattr(juego, "JugadorComputadora", None) or getattr(juego, "ComputerPlayer", None)
    if BotClass is None:
        raise ImportError("No encontré JugadorComputadora ni ComputerPlayer en tu módulo.")
    bot = BotClass(b)

    # Prepara el siguiente reinicio: flip X↔O
    session["next_human_letter"] = "O" if next_h == "X" else "X"
    return g, bot

def _state():
    sid = session.get("sid")
    if not sid or sid not in _store:
        sid = secrets.token_urlsafe(16)
        session["sid"] = sid
        _store[sid] = _nueva_partida()
    return sid, _store[sid]

def _estado_dict(g):
    t = _tablero(g)
    jh, jb = _humano(g), _bot(g)
    mensaje = clase = ""
    fin = False

    if _gana(g, jh):
        fin, mensaje, clase = True, f"¡Ganas con {jh}!", "win"
    elif _gana(g, jb):
        fin, mensaje, clase = True, f"El bot gana con {jb}.", "lose"
    elif _lleno(g):
        fin, mensaje, clase = True, "¡Empate!", "draw"

    x = sum(1 for c in t if c == "X"); o = sum(1 for c in t if c == "O")
    turno = "X" if x == o else "O"

    linea, ganador = _linea_ganadora(t)
    empieza = "Humano" if jh == "X" else "Bot"  # informativo
    return {"tablero": t, "jhumano": jh, "jbot": jb, "mensaje": mensaje, "clase": clase,
            "turno": turno, "fin": fin, "linea": linea, "ganador": ganador, "empieza": empieza}

@app.route("/")
def home():
    _, (g, _) = _state()
    return render_template_string(TPL_HTML, **_estado_dict(g))

# Fallback sin JS (recarga)
@app.route("/jugar/<int:i>")
def jugar(i):
    _, (g, bot) = _state()
    t = _tablero(g)
    if 0 <= i < 9 and t[i] == "-":
        t[i] = _humano(g)
        if not (_gana(g, _humano(g)) or _lleno(g)):
            ia = getattr(bot, "movimiento_maquina", None) or getattr(bot, "machine_move", None)
            pos = ia(_tablero(g))
            if pos is not None and 0 <= pos < 9 and t[pos] == "-":
                t[pos] = _bot(g)
    return redirect(url_for("home"))

@app.route("/reiniciar")
def reiniciar():
    sid, _ = _state()
    _store[sid] = _nueva_partida()
    return redirect(url_for("home"))

# API para JS (sin recargar)
@app.get("/api/state")
def api_state():
    _, (g, _) = _state()
    return jsonify(_estado_dict(g))

@app.post("/api/jugar/<int:i>")
def api_jugar(i):
    _, (g, bot) = _state()
    t = _tablero(g)
    if 0 <= i < 9 and t[i] == "-":
        t[i] = _humano(g)
        if not (_gana(g, _humano(g)) or _lleno(g)):
            ia = getattr(bot, "movimiento_maquina", None) or getattr(bot, "machine_move", None)
            pos = ia(_tablero(g))
            if pos is not None and 0 <= pos < 9 and t[pos] == "-":
                t[pos] = _bot(g)
    return jsonify(_estado_dict(g))

@app.post("/api/reiniciar")
def api_reiniciar():
    sid, _ = _state()
    _store[sid] = _nueva_partida()
    _, (g, _) = _state()
    return jsonify(_estado_dict(g))

# === Plantilla HTML+CSS+JS inline (sin /templates) ===
TPL_HTML = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Tres en Raya</title>
  <style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu; }
    body { display:flex; align-items:center; justify-content:center; min-height:100vh; background:#0f172a; margin:0; }
    .card { background:#111827; color:#e5e7eb; padding:24px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.35); width:min(520px,92vw); }
    h1 { margin:0 0 12px; font-size:1.25rem; color:#fafafa; }
    .meta { color:#9ca3af; font-size:.92rem; margin-bottom:16px; display:flex; justify-content:space-between; gap:8px; flex-wrap:wrap; }
    #board { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
    .cell { aspect-ratio:1/1; display:flex; align-items:center; justify-content:center; font-size:2rem; border-radius:12px;
            background:#1f2937; color:#f9fafb; border:1px solid #374151; text-decoration:none; transition:transform .12s ease, background .2s ease }
    .cell:hover { transform:translateY(-1px); background:#243041; }
    .disabled { pointer-events:none; opacity:.65; }
    .win { background:#064e3b !important; border-color:#047857; animation: glow 1.2s ease-in-out infinite alternate; }
    @keyframes glow { from { box-shadow:0 0 0 rgba(34,197,94,.0);} to { box-shadow:0 0 18px rgba(34,197,94,.45);} }
    .pop { animation: pop .18s ease-out; }
    @keyframes pop { from { transform:scale(.6); opacity:.2; } to { transform:scale(1); opacity:1; } }

    .footer { display:flex; gap:8px; margin-top:16px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
    .btn { background:#2563eb; color:#fff; padding:10px 14px; border-radius:10px; text-decoration:none; border:0; cursor:pointer; }
    .btn.secondary { background:#374151; }
    .status { color:#cbd5e1; min-height:1.2em; }
    .msg.win { color:#22c55e; } .msg.draw { color:#f59e0b; } .msg.lose { color:#ef4444; }

    /* confetti mínimo */
    .confetti { position: fixed; top: -10px; width: 8px; height: 12px; opacity: .9; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Tres en Raya</h1>
    <div class="meta">
      <div>Tú: <strong id="jhumano">{{ jhumano }}</strong> | Bot: <strong id="jbot">{{ jbot }}</strong></div>
      <div>Empieza: <strong id="empieza">{{ empieza }}</strong></div>
    </div>

    <div id="board" aria-label="Tablero 3x3"></div>

    <div class="footer">
      <div class="status"><span id="statusText" class="msg {{ clase }}">{{ mensaje or ('Turno del ' + turno) }}</span></div>
      <div><button id="btnReset" class="btn secondary" type="button">Reiniciar (alterna inicio)</button></div>
    </div>
  </div>

  <script>
    const boardEl = document.getElementById('board');
    const statusEl = document.getElementById('statusText');
    const jhEl = document.getElementById('jhumano');
    const jbEl = document.getElementById('jbot');
    const empiezaEl = document.getElementById('empieza');
    const btnReset = document.getElementById('btnReset');
    let prevBoard = Array(9).fill('-');

    async function api(path, opts={}) {
      const res = await fetch(path, { method: 'GET', headers: { 'Accept': 'application/json' }, ...opts });
      return res.json();
    }

    function render(state) {
      const {tablero, jhumano, jbot, mensaje, clase, turno, fin, linea, ganador, empieza} = state;

      jhEl.textContent = jhumano;
      jbEl.textContent = jbot;
      empiezaEl.textContent = empieza || (jhumano === 'X' ? 'Humano' : 'Bot');

      statusEl.className = 'msg ' + (clase || '');
      statusEl.textContent = mensaje || `Turno del ${turno}`;

      boardEl.innerHTML = '';
      for (let i = 0; i < 9; i++) {
        const v = tablero[i];
        const cell = document.createElement(v === '-' && !fin ? 'a' : 'div');
        cell.className = 'cell';
        if (linea && linea.includes(i)) cell.classList.add('win');

        if (v !== '-') {
          cell.textContent = v;
          if (prevBoard[i] !== v) cell.classList.add('pop');
          if (fin) cell.classList.add('disabled');
        } else if (!fin) {
          cell.href = '#';
          cell.dataset.idx = i;
          cell.addEventListener('click', onCellClick, { once: true });
        } else {
          cell.classList.add('disabled');
        }
        boardEl.appendChild(cell);
      }

      if (clase === 'win') launchConfetti();
      prevBoard = tablero.slice();
    }

    async function onCellClick(e) {
      e.preventDefault();
      const idx = parseInt(e.currentTarget.dataset.idx, 10);
      const state = await api(`/api/jugar/${idx}`, { method: 'POST' });
      render(state);
    }

    btnReset.addEventListener('click', async () => {
      const state = await api('/api/reiniciar', { method: 'POST' });
      prevBoard = Array(9).fill('-');
      render(state);
    });

    function launchConfetti() {
      const colors = ['#22c55e','#86efac','#34d399','#10b981','#059669'];
      for (let i = 0; i < 30; i++) {
        const s = document.createElement('div');
        s.className = 'confetti';
        s.style.left = (Math.random()*100) + 'vw';
        s.style.background = colors[i % colors.length];
        s.style.transform = `rotate(${Math.random()*360}deg)`;
        s.style.animation = `fall ${1.2 + Math.random()*0.8}s linear`;
        s.style.width = (6 + Math.random()*6) + 'px';
        s.style.height = (8 + Math.random()*10) + 'px';
        document.body.appendChild(s);
        setTimeout(() => s.remove(), 2000);
      }
    }
    const style = document.createElement('style');
    style.textContent = `@keyframes fall { to { transform: translateY(110vh) rotate(720deg); opacity:.8; } }`;
    document.head.appendChild(style);

    // estado inicial
    (async () => render(await api('/api/state')))();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Codespaces suele usar 8080
    app.run(host="0.0.0.0", port=port, debug=True)
