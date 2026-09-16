# Omega Pellets: Experiment Zero

**Omega Pellets: Experiment Zero** is a retro-inspired arcade game developed in Python using Pygame.

Inspired by classic Snake gameplay, Omega Pellets expands the formula with multiple pellet types, speed manipulation, competitive/cooperative two-player gameplay, timed experiments, persistent unlockables, sound effects, and unlockable retro visual modes.

Experiment Zero represents the prototype and foundation of the larger **Omega Pellets** project.

---

## About the Game

You control an experimental organism inside a contained testing environment.

Your objective is simple:

**Consume pellets, increase your score, survive, and avoid crashing into yourself or the containment boundaries.**

Different pellets affect the organism in different ways, meaning not every pellet simply makes you grow.

---

## Pellet Types

| Pellet | Effect |
|---|---|
| Green | Grows the organism by one segment |
| Yellow | Removes one additional segment without going below the minimum length |
| Red | Increases movement speed |
| Blue | Decreases movement speed |

Every pellet consumed awards **1 point**.

---

## Game Modes

### Single Player

Control one specimen and attempt to achieve the highest score possible before the experiment ends.

**Controls:**

- `W A S D` — Move
- `P` — Pause
- `ESC` — Return to menu
- `R` — Restart after game over

### Two Player

Two specimens share the same containment environment.

Player scores are competitive, but survival also requires avoiding the other specimen.

**Player 1**

- `W A S D` — Move

**Player 2**

- `Arrow Keys` — Move

**Shared Controls**

- `P` — Pause
- `ESC` — Return to menu
- `R` — Restart

Contact between the two specimens results in a:

**CONTAINMENT FAILURE**

---

## Experiment Timer

Each experiment lasts:

**120 seconds**

When time expires, the experiment ends.

In two-player mode, the player with the highest score wins. Equal scores result in a draw.

---

## Unlockable Features

Experiment Zero includes a persistent progression system.

| Required Score | Unlock |
|---:|---|
| 25 | Sound Mode |
| 50 | Classic Black & White Mode |
| 75 | Classic Game Boy Mode |

Reaching **75 or higher** unlocks all currently available modes.

Unlock progress and the player's high score are saved between game sessions.

---

## Sound Mode

Sound effects become available after reaching a score of **25**.

Sound effects are used for events including:

- Consuming pellets
- Crashing
- Experiment/round completion

The current prototype generates its retro sound effects programmatically and does not require external audio assets.

---

## Visual Modes

### Experiment Zero

The default presentation of the prototype.

It uses the original dark laboratory-style grid, colored pellets, and distinct player colors.

### Classic Black & White

Unlocked at **50 points**.

A minimalist monochrome mode inspired by early arcade and computer games.

The mode includes its own bitmap-style typography and monochrome presentation.

### Classic Game Boy

Unlocked at **75 points**.

A green monochrome LCD-inspired presentation based on the appearance of classic handheld games.

It includes:

- Green LCD-style palette
- Dark pixel-based organisms
- Bitmap typography
- Game Boy-inspired interface presentation

---

## Prototype Philosophy

Experiment Zero is intentionally simple.

Rather than representing the final visual direction of Omega Pellets, it represents the earliest experimental version of the game's mechanics.

The prototype focuses on:

- Movement
- Pellet behavior
- Growth and reduction
- Speed manipulation
- Collision systems
- Multiplayer
- Scoring
- Timed rounds
- Unlockable content
- Retro presentation modes

Future versions of Omega Pellets may expand considerably beyond this prototype.

---

## Requirements

- Python 3
- Pygame

The project was developed and tested using Python 3.12 and Pygame.

Install Pygame with:

```bash
py -3.12 -m pip install pygame

Running the Game

Clone or download the repository.

Open a terminal inside the project directory and run:

py -3.12 main.py

You can check the Python file for syntax errors before launching with:

py -3.12 -m py_compile main.py
Current Version

Experiment Zero v0.4.0

Current features include:

Single-player gameplay
Local two-player gameplay
Four pellet types
Growth and shrinking mechanics
Dynamic movement speed
120-second experiment timer
Countdown before each experiment
Collision detection
Containment boundaries
Pause system
Pellet feedback
Score tracking
Persistent high score
Persistent unlock system
Unlockable sound effects
Unlockable Classic Black & White mode
Unlockable Classic Game Boy mode
Retro bitmap typography
Game-over and winner detection
Development Status

Experiment Zero is feature-complete as the initial Omega Pellets prototype.

Development can now move toward expanding the concept beyond the Experiment Zero foundation.

License

A license has not yet been specified for this project.

Unless a license is added to the repository, the source code should not be assumed to grant permission for redistribution, modification, or commercial use.

Credits

Omega Pellets
Created and developed by Omega Katana

Built with Python and Pygame.

Welcome to Experiment Zero.

