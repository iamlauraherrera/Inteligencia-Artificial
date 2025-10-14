# Copilot Instructions for Inteligencia-Artificial

## Visión General
Este proyecto implementa algoritmos de Machine Learning, centrado en un juego de Tic-Tac-Toe (Triqui) con una IA basada en Minimax. La arquitectura principal es una aplicación web Flask (`app.py`) que interactúa con la lógica del juego definida en `minimax-algorithm.py`.

## Componentes Clave
- **`app.py`**: Servidor Flask. Carga dinámicamente el módulo de juego, gestiona sesiones y rutas web. Adapta nombres de atributos ES/EN para máxima compatibilidad.
- **`minimax-algorithm.py`**: Lógica del juego Tic-Tac-Toe y la IA Minimax. Define clases `TicTacToe`, `JugadorHumano`, `JugadorComputadora` y el algoritmo recursivo Minimax.
- **`templates/index.html`**: Interfaz web para jugar.

## Patrones y Convenciones
- **Carga dinámica de módulos**: `app.py` usa `importlib` para cargar el archivo de lógica del juego, permitiendo cambiar el motor de juego vía la variable de entorno `JUEGO_PATH`.
- **Compatibilidad ES/EN**: Helpers en `app.py` permiten que la lógica del juego use nombres en español o inglés sin modificar el frontend.
- **Sesiones en memoria**: Las partidas se almacenan en un diccionario `_store` indexado por un token de sesión.
- **Rutas principales**:
  - `/`: Muestra el tablero y el estado actual.
  - `/jugar/<int:i>`: Realiza el movimiento del jugador y de la IA.
  - `/reiniciar`: Reinicia la partida.

## Flujo de Datos
- El usuario interactúa vía la web (`index.html`).
- Las acciones llaman a rutas Flask, que modifican el estado del juego y actualizan el tablero.
- La IA responde automáticamente tras el movimiento humano.

## Workflows de Desarrollo
- **Ejecución local**: `python app.py` (el puerto por defecto es 8080, configurable vía `PORT`).
- **No hay tests automatizados ni scripts de build**.
- **Dependencias**: Solo librerías estándar de Python y Flask.

## Ejemplo de Extensión
Para agregar otro motor de juego, impleméntalo en un archivo Python y usa la variable de entorno `JUEGO_PATH` para cargarlo sin modificar el frontend.

## Reglas Específicas para Agentes AI
- Usa helpers de `app.py` para acceder a atributos del juego (compatibilidad ES/EN).
- No modifiques la lógica de sesión ni la carga dinámica sin justificación.
- Mantén la interfaz web en `templates/index.html` sincronizada con los cambios en la lógica del juego.
- Documenta cualquier convención nueva en este archivo.

## Referencias
- `app.py`, `minimax-algorithm.py`, `templates/index.html`, `README.md`

---
¿Hay secciones poco claras o faltantes? Indica qué detalles necesitas para mejorar estas instrucciones.