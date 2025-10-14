# Instrucciones de ejecución (rápidas) — Inteligencia-Artificial

Estas instrucciones muestran cómo ejecutar los algoritmos y la UI del proyecto. El uso de un virtual environment (venv) es opcional pero recomendado.

## Resumen rápido
- La UI y el simulador web están en `app.py` (usa Flask). Por defecto busca algoritmos en `./algos`.
- El motor Minimax (CLI) está en `algos/minimax-algorithm.py` y puede ejecutarse por separado, solo sin interfaz de simulación.

## Requisitos mínimos
- Python 3.9+ (por las anotaciones `list[str]`).

## Opcional: crear y activar virtualenv
Recomendado para aislar dependencias. Opcional si instalas globalmente.
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Instalar dependencias
Usando el archivo `requirements.txt` creado en la raíz:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Si prefieres instalar solo Flask:
```bash
pip install Flask>=2.0,<3.0
```

## Ejecutar servidor web (UI)
1. Desde la raíz del repo:
```bash
export PORT=8080   # opcional, por defecto 8080
python app.py
```
2. Abrir en tu navegador: `http://localhost:8080` (o usar `$BROWSER http://localhost:8080`).
3. Abrir por GitHub https://github.com/iamlauraherrera/Inteligencia-Artificial

Notas:
- `app.py` busca los archivos listados en la variable `ALGO_FILES` dentro de `app.py` y los carga desde `ALGO_DIR` (`algos` por defecto).

## Ejecutar el motor Minimax en consola (modo CLI)
```bash
python algos/minimax-algorithm.py
```
El archivo contiene `if __name__ == "__main__"` para que la ejecución CLI no se dispare al importarlo desde `app.py`.

## Variables de entorno útiles
- `PORT` — puerto donde corre la app web (por defecto 8080).
- `ALGO_DIR` — carpeta donde buscar algoritmos (por defecto `algos`).
- `ALGO_FILES` — lista declarada en `app.py` con nombres permitidos (edítala si añades nuevos archivos).

## Integración y convenciones específicas
- El adaptador de `app.py` para TicTacToe del algoritmo minmax (Triqui) espera que el módulo exponga `TicTacToe` y una clase de IA (`JugadorComputadora`) con método `movimiento_maquina`.
- `app.py` incluye helpers que permiten compatibilidad entre nombres en español e inglés
- Evita ejecutar lógica a nivel de módulo en tus archivos de algoritmo: usa `if __name__ == "__main__":` para código CLI.

## Solución rápida de problemas
- ImportError al cargar un motor: revisa la traza en la terminal que corre `app.py`.
- Error de versión de Python: confirma `python --version` y usa 3.9+.
- Peticiones a `/api/*` fallan: abrir DevTools del navegador y revisar la pestaña Network y la consola; también vigila la salida de la terminal del servidor.
