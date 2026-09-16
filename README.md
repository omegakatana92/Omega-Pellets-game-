# Omega Pellets

**Omega Pellets** is a sci-fi aquatic laboratory arcade game created by **OmegaKatanaXIII / Omega Productions** with Python and Pygame.

You play as an Omega Labs scientist controlling and analyzing bioengineered aquatic serpents designed to consume garbage, pollution, and waste. The research is part of an environmental initiative intended to help clean water systems on colonies and artificial planets known as Artnets.

## Current Release

**v0.8.2 — Terminal Transition Fix**

The current build expands the original Experiment Zero prototype into the full Omega Labs presentation, including:

- Single-player and local two-player experiments
- Four scientific pellet effects: BIOMASS+, BIOMASS-, VELOCITY+, and VELOCITY-
- Three serpent growth forms
- 120-second laboratory sessions
- Scientist monitoring HUD and aquatic containment environment
- Pause, incident-report, shutdown, and session-initialization sequences
- Persistent high score and unlock progression
- Concept Art Archive unlocked at score 5
- Experiment Zero Prototype unlocked at score 25
- Classic Black & White unlocked at score 50
- Classic Game Boy unlocked at score 75
- Music, sound effects, and Omega Labs voice announcements
- Credits mode
- Omega Katana production intro
- Opening Omega Labs lore sequence
- Scientist-access terminal and system initialization before the main menu

## Story

The Intergalactic Alliance launches an environmental competition to develop new ways to clean polluted water systems and environments. Omega Labs answers with an unusual proposal: a bioengineered aquatic organism capable of consuming garbage, pollution, and waste.

Before these organisms can be deployed to colonies and Artnets, the specimens must be tested. The player operates the Omega Labs control system, guides the specimens, analyzes their responses, and records the results.

## Controls

### Player 1

- `W` — Up
- `A` — Left
- `S` — Down
- `D` — Right

### Player 2

- Arrow keys — Movement

### Shared

- `P` — Pause / resume
- `ESC` — Return / exit session as appropriate
- `R` — Restart after an experiment ends
- `ENTER` — Select menu options

## Pellet Database

| Pellet | Laboratory Effect | Gameplay Effect |
|---|---|---|
| Green | BIOMASS+ | +1 score and +1 body segment |
| Yellow | BIOMASS- | +1 score and reduces body length, minimum 3 |
| Red | VELOCITY+ | +1 score and increases movement speed |
| Blue | VELOCITY- | +1 score and decreases movement speed |

## Progression

Progress is stored outside the project folder in the user's home directory as `.omega_pellets_unlocks.json`.

| High Score | Unlock |
|---:|---|
| 5 | Concept Art Archive |
| 25 | Experiment Zero Prototype |
| 50 | Classic Black & White |
| 75 | Classic Game Boy |

Sound effects are available from the beginning and are not an unlock.

## Requirements

- Python 3.12 recommended
- Pygame 2.6.1

Install Pygame:

```bash
py -3.12 -m pip install pygame==2.6.1
```

Run the game:

```bash
py -3.12 main.py
```

Syntax check:

```bash
py -3.12 -m py_compile main.py
```

The `assets` directory must remain beside `main.py` so the game can load its music, voice recordings, concept art, and intro artwork.

## Experiment Zero

Experiment Zero is preserved inside Omega Pellets as an unlockable playable archive. It represents the original grid-based prototype and the starting point of the project rather than the current main presentation.

## Credits

### Game

- Creator / Game Development — **OmegaKatanaXIII**
- Voice Actor — **OmegaKatanaXIII**
- Concept Artwork — **OmegaKatanaXIII**
- Production — **Omega Productions**
- Built with **Python & Pygame**

### Music used by the game

- Main Menu — **80s Mysterywave Music** — DesertDev
- Single Player — **Scanner** — Karl Casey / White Bat Audio
- Two Player — **Deadly Force** — Karl Casey / White Bat Audio
- Credits — **Warped** — Alexander Ehlers
- Opening / Lore Sequence — **Flags** — Alexander Ehlers
- Options — `assembly_not_required.ogg`

The repository does not currently document the author/license details for `assembly_not_required.ogg`; those details should be verified before distributing that track publicly.

## License

The source repository currently includes the **GNU General Public License v3.0 (GPL-3.0)**. See `LICENSE` for the complete license text.

Music, voice recordings, artwork, and other media assets may have separate rights or attribution requirements and are not automatically relicensed merely because the source code repository uses GPL-3.0.

---

**OMEGA PRODUCTIONS 2026**
