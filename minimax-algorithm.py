"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ALGORITMO MINIMAX (Python)                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Autor:           Laura Herrera                                               ║
║ Proyecto:        Ta-Te-Ti (Tic Tac Toe) con interfaz gráfica (Tkinter)       ║
║ Descripción:     Implementación simple, clara y documentada de un juego      ║
║                  de Ta-Te-Ti con ventana gráfica, botones y reinicio.        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CUADRO DE FUNCIONES                                                          ║
║ ───────────────────────────────────────────────────────────────────────────  ║
║ 1) crear_ventana()                                                           ║
║    Qué hace: Inicializa la ventana principal, crea el tablero de botones     ║
║              y configura el estado inicial del juego.                        ║
║    Parámetros: Ninguno                                                       ║
║    Retorna:    Ninguno                                                       ║
║                                                                              ║
║ 2) manejar_click(fila: int, columna: int)                                    ║
║    Qué hace: Gestiona el clic en una celda; coloca la marca del jugador      ║
║              actual si la celda está vacía, comprueba victoria o empate      ║
║              y alterna el turno.                                             ║
║    Parámetros: fila (int) → Fila de la celda presionada                      ║
║                columna (int) → Columna de la celda presionada                ║
║    Retorna:    Ninguno                                                       ║
║                                                                              ║
║ 3) verificar_ganador() -> bool                                               ║
║    Qué hace: Revisa filas, columnas y diagonales para detectar si el         ║
║              jugador actual ganó.                                            ║
║    Parámetros: Ninguno (usa variables de estado globales)                    ║
║    Retorna:    True si hay ganador, False en caso contrario                  ║
║                                                                              ║
║ 4) tablero_lleno() -> bool                                                   ║
║    Qué hace: Verifica si todas las celdas están ocupadas (empate).           ║
║    Parámetros: Ninguno                                                       ║
║    Retorna:    True si no hay celdas vacías, False en caso contrario         ║
║                                                                              ║
║ 5) reiniciar_juego()                                                         ║
║    Qué hace: Limpia el tablero, reinicia etiquetas y estado para comenzar    ║
║              una nueva partida.                                              ║
║    Parámetros: Ninguno                                                       ║
║    Retorna:    Ninguno                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from tkinter import Tk, Button, Label, Frame, messagebox
from typing import List, Optional

# ============================
# Variables de estado globales
# ============================
ventana: Optional[Tk] = None
tablero: List[List[str]] = [["" for _ in range(3)] for _ in range(3)]
botones: List[List[Button]] = []
jugador_actual: str = "X"  # "X" inicia por defecto


def crear_ventana() -> None:
    """
    Autor: Laura Herrera
    Inicializa la interfaz gráfica del juego Ta-Te-Ti.
    - Crea la ventana principal.
    - Construye una cuadrícula 3x3 de botones para el tablero.
    - Añade etiqueta de estado y botón de reinicio.
    - Establece el jugador inicial.
    """
    global ventana, botones, jugador_actual

    ventana = Tk()
    ventana.title("Ta-Te-Ti — Autor: Laura Herrera")
    ventana.resizable(False, False)

    # Marco principal para el tablero
    marco_tablero = Frame(ventana, padx=10, pady=10)
    marco_tablero.grid(row=0, column=0, columnspan=3)

    # Crear los 9 botones (3x3)
    botones = []
    for i in range(3):
        fila_botones = []
        for j in range(3):
            btn = Button(
                marco_tablero,
                text="",
                width=6,
                height=3,
                font=("Helvetica", 24, "bold"),
                command=lambda f=i, c=j: manejar_click(f, c),
            )
            btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
            fila_botones.append(btn)
        botones.append(fila_botones)

    # Etiqueta de estado del turno
    etiqueta_turno = Label(ventana, text=f"Turno de: {jugador_actual}", font=("Helvetica", 12))
    etiqueta_turno.grid(row=1, column=0, padx=10, pady=(0, 10))

    # Botón de reinicio
    boton_reinicio = Button(ventana, text="Reiniciar", font=("Helvetica", 12), command=reiniciar_juego)
    boton_reinicio.grid(row=1, column=2, padx=10, pady=(0, 10))

    # Guardar referencia a la etiqueta en la ventana
    ventana.etiqueta_turno = etiqueta_turno  # type: ignore[attr-defined]

    ventana.mainloop()


def manejar_click(fila: int, columna: int) -> None:
    """
    Autor: Laura Herrera
    Gestiona el clic del usuario en el tablero.
    Coloca la marca del jugador actual si la celda está vacía y comprueba
    si hay ganador o empate; si no, alterna el turno.
    """
    global jugador_actual

    if tablero[fila][columna] != "":
        return  # Celda ocupada: ignorar

    # Actualizar modelo (tablero) y vista (botón)
    tablero[fila][columna] = jugador_actual
    botones[fila][columna].config(text=jugador_actual)

    # Verificar estado del juego
    if verificar_ganador():
        messagebox.showinfo("Fin de la partida", f"¡Jugador {jugador_actual} ha ganado!")
        reiniciar_juego()
        return

    if tablero_lleno():
        messagebox.showinfo("Empate", "No hay más movimientos disponibles. ¡Empate!")
        reiniciar_juego()
        return

    # Cambiar turno
    jugador_actual = "O" if jugador_actual == "X" else "X"
    # Actualizar etiqueta de turno
    assert ventana is not None
    ventana.etiqueta_turno.config(text=f"Turno de: {jugador_actual}")  # type: ignore[attr-defined]


def verificar_ganador() -> bool:
    """
    Autor: Laura Herrera
    Revisa si el jugador actual tiene una línea (3 en raya) en filas,
    columnas o diagonales.
    """
    # Comprobar filas
    for i in range(3):
        if tablero[i][0] == tablero[i][1] == tablero[i][2] != "":
            return True

    # Comprobar columnas
    for j in range(3):
        if tablero[0][j] == tablero[1][j] == tablero[2][j] != "":
            return True

    # Comprobar diagonales
    if tablero[0][0] == tablero[1][1] == tablero[2][2] != "":
        return True
    if tablero[0][2] == tablero[1][1] == tablero[2][0] != "":
        return True

    return False


def tablero_lleno() -> bool:
    """
    Autor: Laura Herrera
    Devuelve True si no hay celdas vacías en el tablero.
    """
    for fila in tablero:
        for celda in fila:
            if celda == "":
                return False
    return True


def reiniciar_juego() -> None:
    """
    Autor: Laura Herrera
    Reinicia el estado del juego:
    - Limpia el tablero lógico y visual.
    - Restablece el jugador a 'X' y actualiza la etiqueta de turno.
    """
    global tablero, jugador_actual

    # Limpiar tablero lógico
    tablero = [["" for _ in range(3)] for _ in range(3)]
    # Limpiar tablero visual
    for i in range(3):
        for j in range(3):
            botones[i][j].config(text="")

    # Restablecer turno y etiqueta
    jugador_actual = "X"
    assert ventana is not None
    ventana.etiqueta_turno.config(text=f"Turno de: {jugador_actual}")  # type: ignore[attr-defined]


if __name__ == "__main__":
    crear_ventana()
