"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ALGORITMO MINIMAX (Python)                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Autor:           Laura Herrera                                               ║
║ Fecha de entrega: 14/10/2023                                                 ║
║ Proyecto:        (Tic Tac Toe) con interfaz gráfica (Tkinter) desarrollada   ║
║                  en Python.                                                  ║
║ Descripción:     Implementación simple, clara y documentada del juego        ║
║                  Triqui (Tic-Tac-Toe) con ventana gráfica, botones y         ║
║                  reinicio.                                                   ║
║ Librerias:      Solo estándar (random, math, os). No se usan librerías       ║
║                  externas.                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import random
import math

"""     Módulo principal: clase TicTacToe y lógica del juego.
╔══════════════════════════════════════════════════════════════════════════════╗
║ 1) class TicTacToe()                                                         ║
║ ──────────────────────────────────────────────────────────────────────────── ║
║  Atributos:                                                                  ║
║      (list[str]): Lista de 9 posiciones representando el 3x3                 ║
║       values: 'X', 'O' o '-'.                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class TicTacToe:

    def __init__(self):
        """Inicializa tablero y asigna X/O aleatoriamente."""
        self.tablero = ['-' for _ in range(9)]
        if random.randint(0, 1) == 1:
            self.jugadorHumano = 'X'
            self.jugadorBot = 'O'
        else:
            self.jugadorHumano = 'O'
            self.jugadorBot = 'X'
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   mostrar_tablero(): Imprime el tablero 3x3.                                 ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """ 
    def mostrar_tablero(self):
        """Imprime el tablero 3x3."""
        print("")
        for i in range(3):
            print(" ", self.tablero[0 + (i * 3)], " | ", self.tablero[1 + (i * 3)], " | ", self.tablero[2 + (i * 3)])
        print("")
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   tablero_lleno(estado): Verifica si el tablero está lleno.                  ║
    ║       retorna: bool. True si no hay '-' en el estado.                        ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def tablero_lleno(self, estado):
        """True si no hay '-'."""
        return "-" not in estado
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   jugador_gana(estado,jugador): Verifica si un jugador ha ganado.            ║
    ║       retorna: bool. True si ese jugador tiene 3 en línea.                   ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def jugador_gana(self, estado, jugador):
        """True si hay 3 en línea (filas/columnas/diagonales)."""
        # Filas
        if estado[0] == estado[1] == estado[2] == jugador: return True
        if estado[3] == estado[4] == estado[5] == jugador: return True
        if estado[6] == estado[7] == estado[8] == jugador: return True
        # Columnas
        if estado[0] == estado[3] == estado[6] == jugador: return True
        if estado[1] == estado[4] == estado[7] == jugador: return True
        if estado[2] == estado[5] == estado[8] == jugador: return True
        # Diagonales
        if estado[0] == estado[4] == estado[8] == jugador: return True
        if estado[2] == estado[4] == estado[6] == jugador: return True
        return False
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   verificar_ganador(): Anuncia ganador/empate y retorna True si terminó.     ║
    ║       retorna: bool.                                                         ║
    ║            -True si la partida terminó (ganó alguien o empate)               ║
    ║            -False si sigue                                                   ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def verificar_ganador(self):
        """Anuncia ganador/empate y retorna True si terminó."""
        if self.jugador_gana(self.tablero, self.jugadorHumano):
            os.system("cls" if os.name == "nt" else "clear")
            print(f" ¡Jugador {self.jugadorHumano} gana la partida!")
            return True
        if self.jugador_gana(self.tablero, self.jugadorBot):
            os.system("cls" if os.name == "nt" else "clear")
            print(f" ¡Jugador {self.jugadorBot} gana la partida!")
            return True
        if self.tablero_lleno(self.tablero):
            os.system("cls" if os.name == "nt" else "clear")
            print(" ¡Empate!")
            return True
        return False
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   iniciar(): Ejecuta el bucle del juego (humano - computador) hasta terminar ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def iniciar(self):
        """Bucle principal: humano → IA (Minimax) hasta fin."""
        bot = JugadorComputadora(self.jugadorBot)
        humano = JugadorHumano(self.jugadorHumano)

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print(f" Turno del jugador {self.jugadorHumano}")
            self.mostrar_tablero()

            # Turno Humano
            casilla = humano.movimiento_humano(self.tablero)
            self.tablero[casilla] = self.jugadorHumano
            if self.verificar_ganador():
                break

            # Turno Bot (IA Minimax)
            casilla = bot.movimiento_maquina(self.tablero)
            self.tablero[casilla] = self.jugadorBot
            if self.verificar_ganador():
                break

        print()
        self.mostrar_tablero()
"""     
╔══════════════════════════════════════════════════════════════════════════════╗
║ 2) class JugadorHumano(TicTacToe)                                            ║
║ ──────────────────────────────────────────────────────────────────────────── ║
║  Atributos:                                                                  ║
║      letra (string): 'X','O'.                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class JugadorHumano:
    # Guarda la letra y solicita jugada válida (1-9).

    def __init__(self, letra: str):
        # Define la letra ('X' u 'O')."""
        self.letra = letra
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   movimiento_humano(estado): Solicita y valida la jugada del humano          ║
    ║       retorna: índice (0-8) de la casilla elegida libre                      ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def movimiento_humano(self, estado: list[str]) -> int:
        # Pide una casilla (1-9) y retorna índice [0..8] libre.
        while True:
            try:
                casilla = int(input("Ingresa la casilla (1-9)="))
            except ValueError:
                print("Entrada inválida. Debe ser un número del 1 al 9")
                continue
            if 1 <= casilla <= 9 and estado[casilla - 1] == "-":
                return casilla - 1
            print("Movimiento no válido. Intenta con una casilla libre del 1 al 9")
"""     
╔══════════════════════════════════════════════════════════════════════════════╗
║ 3) class JugadorComputadora(TicTacToe)                                       ║
║ ──────────────────────────────────────────────────────────────────────────── ║
║  Atributos:                                                                  ║
║      jugadorBot (string): 'X','O'.                                           ║
║      jugadorHumano (string): 'X','O' asignada al humano.                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class JugadorComputadora(TicTacToe):

    def __init__(self, letra: str):
        # Inicializa IA con su letra y deduce la del humano.
        self.jugadorBot = letra
        self.jugadorHumano = "X" if letra == "O" else "O"
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   jugador_de_turno(estado): Devuelve 'X' u 'O' según conteo en tablero.      ║
    ║       retorna: string. 'X' u 'O'.                                            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def jugador_de_turno(self, estado: list[str]) -> str:
        # Devuelve a quién le toca ('X' u 'O').
        x = sum(1 for c in estado if c == "X")
        o = sum(1 for c in estado if c == "O")
        if self.jugadorHumano == "X":
            return "X" if x == o else "O"
        return "O" if x == o else "X"
    """ 
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   acciones(estado):
    ║       retorna: índices de casillas vacías ('-').                             ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def acciones(self, estado: list[str]) -> list[int]:
        return [i for i, c in enumerate(estado) if c == "-"]
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   resultado(estado, accion):            ║
    ║       retorna: Copia del estado aplicando la acción.                         ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def resultado(self, estado: list[str], accion: int) -> list[str]:
        # Nuevo estado tras aplicar la acción.
        nuevo = estado.copy()
        jugador = self.jugador_de_turno(estado)
        nuevo[accion] = jugador
        return nuevo
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   terminal(estado): Verifica si el juego terminó (alguien ganó).             ║
    ║       retorna: bool. True si X u O ganó.                                     ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def terminal(self, estado: list[str]) -> bool:
        # True si X u O ganó.
        return self.jugador_gana(estado, "X") or self.jugador_gana(estado, "O")
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   minimax(estado, jugador): Algoritmo Minimax recursivo                      ║
    ║       retorna: dict {'position': mejor_indice, 'score': puntaje}.            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def minimax(self, estado: list[str], jugador: str) -> dict:
        max_jugador = self.jugadorHumano
        otro = 'O' if jugador == 'X' else 'X'

        if self.terminal(estado):
            libre = len(self.acciones(estado)) + 1
            return {'position': None,
                    'score': (1 * libre) if otro == max_jugador else (-1 * libre)}
        elif self.tablero_lleno(estado):
            return {'position': None, 'score': 0}

        mejor = {'position': None, 'score': -math.inf} if jugador == max_jugador \
                else {'position': None, 'score': math.inf}

        for mov in self.acciones(estado):
            nuevo = self.resultado(estado, mov)
            puntaje = self.minimax(nuevo, otro)
            puntaje = {'position': mov, 'score': puntaje['score']}

            if jugador == max_jugador:
                if puntaje['score'] > mejor['score']:
                    mejor = puntaje
            else:
                if puntaje['score'] < mejor['score']:
                    mejor = puntaje

        return mejor
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   movimiento_maquina(estado): Elige la casilla óptima mediante Minimax.      ║
    ║       retorna: índice (0-8) de la casilla elegida por la IA.                 ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def movimiento_maquina(self, estado: list[str]) -> int:
        # Elige la casilla óptima mediante Minimax.
        return self.minimax(estado, self.jugadorBot)['position']

# Iniciar el juego
if __name__ == "__main__":
    tictactoe = TicTacToe()
    tictactoe.iniciar()
