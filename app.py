# app.py
# Interfaz web para tu TicTacToe cargando minimax-algorithm.py por ruta (sin renombrar).

import os, secrets, importlib.util
from flask import Flask, render_template, redirect, url_for, session

# --- Carga del motor por ruta (soporta nombres con guion) ---
RUTA_JUEGO = os.environ.get("JUEGO_PATH", "minimax-algorithm.py")

def cargar_modulo_por_ruta(ruta, nombre_logico="juego_mod"):
    spec = importlib.util.spec_from_file_location(nombre_logico, ruta)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar el módulo desde {ruta}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

juego = cargar_modulo_por_ruta(RUTA_JUEGO)

# --- Helpers SEGUROS para nombres ES/EN ---
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
    # variantes: jugadorHumano / humanPLayer / humanPlayer
    return _pick_attr(g, "jugadorHumano", "humanPLayer", "humanPlayer")

def _bot(g):
    # variantes: jugadorBot / botPlayer
    return _pick_attr(g, "jugadorBot", "botPlayer")

def _gana(g, letra):
    fn = _pick_method(g, "jugador_gana", "is_player_win")
    return fn(_tablero(g), letra)

def _lleno(g):
    fn = _pick_method(g, "tablero_lleno", "is_board_filled")
    return fn(_tablero(g))

# --- Flask app ---
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
_store = {}  # sesiones en memoria (simple)

def _nueva_partida():
    g = juego.TicTacToe()  # no llamamos iniciar()
    BotClass = getattr(juego, "JugadorComputadora", None) or getattr(juego, "ComputerPlayer", None)
    if BotClass is None:
        raise ImportError("No encontré JugadorComputadora ni ComputerPlayer en tu módulo.")
    bot = BotClass(_bot(g))
    return g, bot

def _state():
    sid = session.get("sid")
    if not sid or sid not in _store:
        sid = secrets.token_urlsafe(16)
        session["sid"] = sid
        _store[sid] = _nueva_partida()
    return sid, _store[sid]

@app.route("/")
def home():
    _, (g, bot) = _state()
    t = _tablero(g)

    # Mensajes de fin
    mensaje = clase = ""
    if _gana(g, _humano(g)):
        mensaje, clase = f"¡Ganas con {_humano(g)}!", "win"
    elif _gana(g, _bot(g)):
        mensaje, clase = f"El bot gana con {_bot(g)}.", "lose"
    elif _lleno(g):
        mensaje, clase = "¡Empate!", "draw"

    # Turno (según conteo)
    x = sum(1 for c in t if c == "X")
    o = sum(1 for c in t if c == "O")
    turno = "X" if x == o else "O"

    return render_template(
        "index.html",
        tablero=t, jhumano=_humano(g), jbot=_bot(g),
        mensaje=mensaje, clase=clase, turno=turno
    )

@app.route("/jugar/<int:i>")
def jugar(i):
    _, (g, bot) = _state()
    t = _tablero(g)
    if 0 <= i < 9 and t[i] == "-":
        # Jugada humana
        t[i] = _humano(g)
        if _gana(g, _humano(g)) or _lleno(g):
            return redirect(url_for("home"))

        # Jugada IA
        ia = getattr(bot, "movimiento_maquina", None) or getattr(bot, "machine_move", None)
        if ia is None:
            raise AttributeError("El bot no tiene movimiento_maquina ni machine_move.")
        pos = ia(_tablero(g))
        if pos is not None and 0 <= pos < 9 and t[pos] == "-":
            t[pos] = _bot(g)

    return redirect(url_for("home"))

@app.route("/reiniciar")
def reiniciar():
    sid, _ = _state()
    _store[sid] = _nueva_partida()
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Codespaces suele usar 8080
    app.run(host="0.0.0.0", port=port, debug=True)
