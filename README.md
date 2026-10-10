# simulators

This repo contains the simulators used to carry out experiments. Simulations are
built as 2D desktop apps with the [Python Arcade](https://api.arcade.academy/) library.

## Project structure

```
simulators/
├── arcade_starter/
│   └── main.py        # Starter template: window, game loop, keyboard input, HUD
├── assets/
│   ├── fonts/
│   ├── images/
│   └── sounds/
└── requirements.txt   # Python dependencies
```

## Setup

Requires Python 3 (any version supported by the current Arcade release).

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Running the starter

```bash
python arcade_starter/main.py
```

This opens a resizable 960×540 window with a square you can move around.

| Action      | Keys          |
|-------------|---------------|
| Move        | WASD / Arrows |
| Fullscreen  | F11           |
| Quit        | ESC           |

## Creating a new simulator

1. Copy `arcade_starter/` to a new folder (e.g. `my_experiment/`).
2. Edit the constants at the top of `main.py` (`WIDTH`, `HEIGHT`, `TITLE`, `MOVE_SPEED`).
3. Put the simulation logic in `on_update` and the rendering in `on_draw`.
4. Keep images, sounds and fonts in the matching `assets/` subfolder.
