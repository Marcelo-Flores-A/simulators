# simulators

This repo contains the simulators used to carry out experiments. Simulations are
built as 2D desktop apps with the [Python Arcade](https://api.arcade.academy/) library.

## Project structure

```
simulators/
├── arcade_starter/
│   ├── main.py            # Fruit survival game: menu, game loop, predator AI, HUD
│   └── audio_manager.py   # Loads and plays sound effects / background music
├── assets/
│   ├── fonts/
│   ├── images/
│   └── sounds/            # .mp3 clips used by the audio manager
└── requirements.txt       # Python dependencies
```

## Setup

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Running

Run from the **repository root**. Sounds are loaded from the relative path
`assets/sounds`, so starting the game from another directory leaves it silent.

```bash
python arcade_starter/main.py
```

## The fruit survival game

An endless, Pac-Man-inspired survival game. Collect fruit to score points and stay
away from the predators. The game ends as soon as a predator touches any player.

- **Modes:** Single Player or Two Players (co-op, shared score), picked from the main menu.
- **Fruit:** 15 fruits on the map at all times. Each one collected is worth 10 points
  and is replaced by a new one somewhere random.
- **Predators:** 3 predators chase whichever player is closest. Their color shows
  what they are doing:

  | Color  | State        | Behavior                                                   |
  |--------|--------------|------------------------------------------------------------|
  | Yellow | Guarding     | Circles the area with the most fruit                       |
  | Orange | Intercepting | Player is moving 100–200 px away: predicts and cuts them off |
  | Red    | Hunting      | Player is moving within 100 px: chases them directly        |

  Predators only chase players who are **moving**. If you stand still they go back
  to guarding. They also have randomized reaction times, accuracy and brief
  hesitations, so they don't move perfectly.

### Controls

| Context | Action               | Keys                              |
|---------|----------------------|-----------------------------------|
| Menu    | Navigate / select    | W/S or ↑/↓, Enter, or mouse click |
| Game    | Move Player 1        | WASD                              |
| Game    | Move Player 2        | Arrow keys (two-player mode only) |
| Game    | Pause / resume       | P                                 |
| Game    | Toggle fullscreen    | F11                               |
| Game    | Back to menu         | ESC                               |

To quit, close the window.

### Audio

`audio_manager.py` maps game events (fruit collected, rare "special" fruit sound,
pause, game over, menu clicks, background music) to clips in `assets/sounds/`.
Each fruit collected has a 1 in 10 chance of playing the special sound. If a file is missing or
fails to load, a warning is printed and the game keeps running without that sound.
