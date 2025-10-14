"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ALGORITMO MINIMAX (Python)                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Autor:           Laura Herrera                                               ║
║ Fecha de entrega: 14/10/2023                                                 ║
║ Proyecto:        (Tic Tac Toe)  desarrollada en Python.                      ║
║ Descripción:     Implementación simple, clara y documentada del juego        ║
║                  Triqui (Tic-Tac-Toe) con ventana gráfica, botones y         ║
║                  reinicio.                                                   ║
║ Librerias:      Solo estándar (random, math, os). No se usan librerías       ║
║                  externas.                                                   ║
║ Nota: La ejecucion de la parte logica solo muestra en consola.               ║
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
║      (list[str]): Lista de 9 posiciones (0,8) representando matriz 3x3       ║
║       values: 'X','O','-' (separacion).                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
class TicTacToe:

    def __init__(self):
        #Inicializa tablero y asigna (X,O) aleatoriamente para el humano y la computadora
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
    ║   mostrar_tablero(): Imprime el tablero del juego 3x3.                                 ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """ 
    def mostrar_tablero(self):
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
        return "-" not in estado
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   jugador_gana(estado,jugador): Verifica si un jugador ha ganado.            ║
    ║       retorna: bool. True si ese jugador tiene 3 en línea.                   ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def jugador_gana(self, estado, jugador):
        #True si hay 3 en línea (filas/columnas/diagonales).
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
    ║   verificar_ganador(): Anuncia ganador/empate (Finalizacion del juego)       ║
    ║       retorna: bool.                                                         ║
    ║            -True si la partida terminó (ganó alguien o empate)               ║
    ║            -False si la partida continua                                     ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def verificar_ganador(self):\
        #si gana el humano
        if self.jugador_gana(self.tablero, self.jugadorHumano):
            os.system("cls" if os.name == "nt" else "clear")
            print(f" ¡Jugador {self.jugadorHumano} gana la partida!")
            return True
        #si gana la computadora
        if self.jugador_gana(self.tablero, self.jugadorBot):
            os.system("cls" if os.name == "nt" else "clear")
            print(f" ¡Jugador {self.jugadorBot} gana la partida!")
            return True
        #si hay empate
        if self.tablero_lleno(self.tablero):
            os.system("cls" if os.name == "nt" else "clear")
            print(" ¡Empate!")
            return True
        return False
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   iniciar(): Ejecuta la partida (humano - computador) hasta terminar         ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def iniciar(self):
        # Bucle principal: humano - computador (Minimax) hasta fin.
        bot = JugadorComputadora(self.jugadorBot)
        humano = JugadorHumano(self.jugadorHumano)

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            # Muestra el turno del ser humano
            print(f" Turno del jugador {self.jugadorHumano}")
            self.mostrar_tablero() # metodo para mostrar el tablero

            # Turno Humano
            casilla = humano.movimiento_humano(self.tablero)
            # se asigna la letra del humano a la casilla que eligio
            self.tablero[casilla] = self.jugadorHumano
            if self.verificar_ganador(): # Verifica si el ser humano ganó
                break

            # Turno Computadora
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
        # Define la letra con la que va a iniciar la partida el humano
        self.letra = letra
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   movimiento_humano(estado): Solicita y valida la jugada del humano          ║
    ║       retorna: índice (0-8) de la casilla elegida libre                      ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def movimiento_humano(self, estado: list[str]) -> int:
        while True:
            try:
                # Pide al humano una casilla (1-9)
                casilla = int(input("Ingresa la casilla (1-9)="))
            except ValueError:
                print("Entrada inválida. Debe ser un número del 1 al 9")
                continue
            #valida si esa casilla esta libre
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
    # Inicializa constructor
    def __init__(self, letra: str):
        self.jugadorBot = letra
        self.jugadorHumano = "X" if letra == "O" else "O" # letra contraria al bot
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   jugador_de_turno(estado): Nos deduce el turno de quien debe jugar.         ║
    ║       retorna: string. 'X' u 'O'.                                            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def jugador_de_turno(self, estado: list[str]) -> str:
        # suma de posiciones mas una para deducir el turno hasta (9)
        x = sum(1 for c in estado if c == "X")
        o = sum(1 for c in estado if c == "O")
        if self.jugadorHumano == "X":
            return "X" if x == o else "O"
        return "O" if x == o else "X"
    """ 
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   acciones(estado): Toma el tablero y me da cuantas opciones de movimientos  ║
    ║                     tengo.                                                   ║
    ║       retorna: Posiciones de casillas vacías ('-').                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def acciones(self, estado: list[str]) -> list[int]:
        return [i for i, c in enumerate(estado) if c == "-"] #verifica la disponibilidad de las casillas (c)
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   resultado(estado, accion): Toma un tablero y un movimiento y me modifica   ║
    ║                               el tablero con el movimiento realizado.        ║
    ║       retorna: Copia del tablero aplicando la acción.                        ║
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
        return self.jugador_gana(estado, "X") or self.jugador_gana(estado, "O")
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   minimax(estado, jugador): Algoritmo Minimax recursivo                      ║
    ║       retorna: dict {'position': mejor_indice, 'score': puntaje}.            ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    # Algoritmo Minimax recursivo tomando los tres estados posibles:      
    def minimax(self, estado: list[str], jugador: str) -> dict:
        max_jugador = self.jugadorHumano # el humano es el quien busca la maxima puntuacion
        otro = 'O' if jugador == 'X' else 'X' # el otro jugador
        # 1) Si el estado es terminal (gana X u O), retorna un puntaje.
        if self.terminal(estado): # Comprueba si ha ganado alguien
            libre = len(self.acciones(estado)) + 1
            #devuelve objeto con la posicion y el puntaje
            return {'position': None,
                    'score': (1 * libre) if otro == max_jugador # si gano el humano
                    else (-1 * libre)} 
        # 2) Si el tablero está lleno (empate), retorna puntaje 0.
        elif self.tablero_lleno(estado):
            return {'position': None, 'score': 0} #devuelve el mismo objeto con puntaje 0 (empate)
        if jugador == max_jugador: # si es el turno del humano
            mejor = {'position': None, 'score': -math.inf} #menos infinito
        else:
            mejor = {'position': None, 'score': math.inf} #mas infinito
            #la maquina escoge la menor puntuacion posible y el humano la mayor
        # 3) Si no, explora todas las acciones posibles y elige la mejor según el jugador.
        for mov in self.acciones(estado):
            nuevo = self.resultado(estado, mov)
            puntaje = self.minimax(nuevo, otro) #llamada recursiva a la puntuacion
            # añadimos la posicion a mov
            puntaje = {'position': mov, 'score': puntaje['score']}

            if jugador == max_jugador: #si la puntuacion es mayor que la mejor obtenida
                if puntaje['score'] > mejor['score']:
                    mejor = puntaje
            else:
                if puntaje['score'] < mejor['score']: #Nos quedamos con la menor puntuacion
                    mejor = puntaje

        return mejor #Almacena la posicion con la menor o mayor puntuacion
    """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCION:                                                                     ║
    ║   movimiento_maquina(estado): Realiza el movimiento de la maquina mediante   ║
    ║                               Minimax.                                       ║
    ║       retorna: Posicion (0-8) de la casilla elegida por la IA.               ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    def movimiento_maquina(self, estado: list[str]) -> int:
        casilla = self.minimax(estado, self.jugadorBot)['position'] #mueve la posicion a la que quiere ir la maquina
        return casilla

# Iniciar el juego
if __name__ == "__main__":
    tictactoe = TicTacToe()
    tictactoe.iniciar()