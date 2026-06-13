# DriveAhead MVP

A small Python 2D arena car game prototype inspired by head-crash car battlers.

## MVP Scope

- Local 2-player 1v1 on one keyboard.
- Three data-driven vehicles: Buggy, Truck, Sport.
- Three static maps: Arena, Bridge, Hills.
- Pymunk rigid-body physics with car bodies, wheels, suspension, and head weak spots.
- Score rounds by hitting the opponent head. First to 5 wins.
- Network protocol skeleton for a later LAN 1v1 host/client mode.

## Install

```bash
uv venv
uv sync --extra dev
```

## Run

```bash
uv run python -m driveahead
```

Controls:

| Action | Player 1 | Player 2 |
| --- | --- | --- |
| Forward | D | Left |
| Back / reverse | A | Right |
| Shift weight back | W | Up |
| Shift weight forward | S | Down |
| Boost / jump placeholder | Left Shift | Right Shift |
| Cycle map | M | M |
| Cycle P1 car | 1 | 1 |
| Cycle P2 car | 2 | 2 |
| Start / restart | Enter | Enter |
| Quit | Esc | Esc |

## Extend Content

Add vehicles in `driveahead/content/vehicles.py` by creating another `VehicleSpec`.
Add maps in `driveahead/content/maps.py` by creating another `MapSpec`.

The physics and rendering layers consume those specs instead of hard-coding
content behavior.

## Tests

```bash
uv run pytest
```
