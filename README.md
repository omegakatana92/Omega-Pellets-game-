# Omega Pellets: Experiment Zero

**Omega Pellets: Experiment Zero** is a retro-inspired arcade game developed in Python using Pygame.

Inspired by the classic Snake formula, Omega Pellets begins with a familiar idea: control an organism, consume pellets, increase your score, and avoid colliding with yourself.

Experiment Zero expands that formula with multiple pellet types, growth and reduction mechanics, speed manipulation, timed experiments, local two-player gameplay, containment rules, persistent high scores, unlockable sound effects, and unlockable retro visual modes.

More importantly, **Experiment Zero represents the beginning of the larger Omega Pellets project.**

It is intentionally primitive.

---

# What Is Experiment Zero?

Experiment Zero is the earliest playable version of Omega Pellets.

Within the concept of the larger project, Experiment Zero can be viewed as an **archived behavioral computer simulation** used before the more advanced experiments that would eventually lead toward **Project Omega**.

The simple grid, basic organisms, geometric pellets, minimal sound, and primitive interface are therefore part of its identity.

Rather than replacing Experiment Zero as Omega Pellets develops, the goal is to preserve it as the playable origin of the project.

---

# Objective

You control an experimental organism inside a contained testing environment.

Your objective is to:

**Consume pellets, increase your score, survive the experiment, and avoid containment failure.**

Each experiment lasts:

**120 seconds**

Every pellet consumed awards:

**+1 Point**

Different pellets modify the specimen in different ways.

---

# Pellet Types

## Green — Growth

**Symbol: ●**

Consuming a green pellet:

- Awards +1 point
- Adds one body segment
- Increases the length of the specimen

Growth can be useful for building a larger organism, but additional length also makes navigating the containment area increasingly difficult.

---

## Yellow — Reduction

**Symbol: ⊖**

Consuming a yellow pellet:

- Awards +1 point
- Removes an additional body segment
- Never reduces the organism below its minimum length of 3 segments

This allows players to deliberately reduce their size when their organism becomes difficult to maneuver.

---

## Red — Speed Up

**Symbol: ⊕**

Consuming a red pellet:

- Awards +1 point
- Does not change organism length
- Increases movement speed

Movement delay decreases by approximately **10 milliseconds** per pellet until reaching the maximum speed limit.

Greater speed can help collect pellets faster, but it also makes controlling the organism more difficult.

---

## Blue — Slow Down

**Symbol: ↓**

Consuming a blue pellet:

- Awards +1 point
- Does not change organism length
- Decreases movement speed

Movement delay increases by approximately **10 milliseconds** until reaching the slowest allowed movement speed.

Slowing down can give the player additional time to react when navigating a large organism.

---

# Pellet Spawning

Pellets are not placed completely blindly.

The Experiment Zero simulation includes spawn-safety rules.

Pellets avoid:

- Existing organism segments
- Other pellets
- The upper HUD area
- The lower information and legend area
- Outer containment boundaries
- The immediate area surrounding a newly spawned specimen

This reduces unfair pellet placement while keeping each experiment unpredictable.

---

# Single Player

Single Player places one specimen inside the containment field.

The goal is to collect as many pellets as possible while surviving until the experiment timer expires.

## Controls

| Key | Action |
|---|---|
| W | Move Up |
| A | Move Left |
| S | Move Down |
| D | Move Right |
| P | Pause |
| ESC | Return to Menu |
| R | Restart after Experiment Ends |

---

# Two Player

Experiment Zero also includes local two-player gameplay.

Both organisms occupy the same containment environment and interact with the same pellet system.

## Player 1

**Color: White / Gray**

| Key | Action |
|---|---|
| W | Move Up |
| A | Move Left |
| S | Move Down |
| D | Move Right |

## Player 2

**Color: Red**

| Key | Action |
|---|---|
| ↑ | Move Up |
| ← | Move Left |
| ↓ | Move Down |
| → | Move Right |

## Shared Controls

| Key | Action |
|---|---|
| P | Pause |
| ESC | Return to Menu |
| R | Restart after Experiment Ends |

---

# Competitive and Cooperative Multiplayer

Two-player Omega Pellets is simultaneously **competitive and cooperative**.

Players compete for the highest score.

However, both specimens must also respect the same containment environment.

Each organism has:

- Its own score
- Its own body length
- Its own movement speed
- Its own pellet effects

If Player 1 consumes a speed pellet, for example, only Player 1 becomes faster.

The same applies to growth, reduction, and slowing.

This means the two players may be experiencing very different movement conditions during the same experiment.

---

# Specimen Contact

The two organisms cannot safely contact one another.

If either organism collides with the other:

**CONTAINMENT FAILURE**

Both specimens fail the experiment.

This happens regardless of which player had the higher score.

This creates an unusual multiplayer relationship:

**You are competing for points, but reckless movement can destroy the experiment for both players.**

---

# Collision Rules

An experiment can terminate because of several conditions.

## Self Collision

If a specimen collides with its own body:

**SPECIMEN TERMINATED**

## Containment Boundary

The HUD and lower information area are outside the playable containment field.

Attempting to cross these boundaries terminates the specimen.

## Specimen Contact

Contact between Player 1 and Player 2 results in:

**CONTAINMENT FAILURE**

## Time Expired

If the specimen survives until the 120-second timer reaches zero:

**EXPERIMENT COMPLETE**

---

# Winning a Two-Player Experiment

If the experiment ends normally, the player with the highest score wins.

If Player 1 has the highest score:

**PLAYER 1 WINS**

If Player 2 has the highest score:

**PLAYER 2 WINS**

If both players have equal scores:

**DRAW**

A player's score remains important even when an experiment terminates through a normal collision.

However, direct contact between the two specimens causes both specimens to fail regardless of score.

---

# Experiment Countdown

Every experiment begins with:

**3**

**2**

**1**

**BEGIN**

The specimens cannot move during the countdown.

The 120-second experiment timer does not begin until the experiment actually starts.

---

# Pause System

Press:

**P**

to pause an active experiment.

While paused:

- Specimen movement stops
- Movement timers stop
- The experiment timer freezes
- Temporary pellet feedback freezes with the experiment
- Pressing P resumes the experiment
- ESC returns to the main menu

The Game Boy visual mode also uses its own LCD-inspired pause presentation to preserve visibility instead of darkening the entire display.

---

# Score Progression and Unlockables

Experiment Zero contains a persistent high-score progression system.

Playing well unlocks additional features.

| High Score | Reward |
|---:|---|
| 25 | Sound Mode |
| 50 | Classic Black & White Mode |
| 75 | Classic Game Boy Mode |

Reaching **75 points or higher** unlocks all currently available Experiment Zero rewards.

Unlocks remain available between game sessions.

The Options menu displays the player's recorded high score along with the current status of each unlockable feature.

---

# Sound Mode

**Unlocked at Score 25**

Sound Mode adds retro sound effects to Experiment Zero.

Sounds are used when:

- A pellet is consumed
- A specimen crashes
- An experiment ends

The prototype generates these retro sounds programmatically.

No external music or copyrighted sound assets are required for the current sound system.

---

# Visual Modes

Experiment Zero contains three visual presentations.

The additional visual modes do not alter the underlying rules of the simulation.

They change how Experiment Zero is presented.

---

## Experiment Zero

The default presentation.

Experiment Zero uses:

- Dark laboratory-style background
- Grid-based containment field
- Colored pellet types
- White/gray Player 1
- Red Player 2
- Colored pellet feedback
- Minimal prototype presentation

This is the canonical visual representation of the original Experiment Zero simulation.

---

## Classic Black & White

**Unlocked at Score 50**

Classic Black & White transforms the simulation into a minimalist early-video-game presentation.

It features:

- Black background
- White monochrome graphics
- Monochrome pellets
- Monochrome pellet feedback
- Early arcade-inspired bitmap typography
- Minimal visual presentation
- No modern color coding

The underlying gameplay remains unchanged.

---

## Classic Game Boy

**Unlocked at Score 75**

Classic Game Boy recreates the appearance of an early monochrome handheld game.

It features:

- Green LCD-style background
- Dark green/black specimen graphics
- Pixelated organism segments
- Game Boy-inspired bitmap typography
- Monochrome LCD pellet presentation
- LCD-style pause interface

The underlying Experiment Zero rules remain unchanged.

---

# Retro Modes Are Visual Simulations

Classic Black & White and Classic Game Boy do not change the fundamental game rules.

The same experiment can therefore be experienced through three different visual interpretations:

**Experiment Zero**

**Classic Black & White**

**Classic Game Boy**

Each visual mode represents a different way of presenting the same underlying simulation.

---

# Experiment Zero as an Archive

Experiment Zero is intended to remain available even as the larger Omega Pellets project evolves.

Future versions may contain more advanced:

- Graphics
- Organism designs
- Laboratory environments
- Animation
- Sound
- Story elements
- Experimental systems
- Specimen research
- Project Omega lore

Experiment Zero represents what came before those developments.

It is the project's **archived simulation**.

Future concept sketches, research notes, specimen records, and development material may also become part of the larger archive presentation.

---

# Technical Information

Omega Pellets: Experiment Zero is currently developed using:

- Python
- Pygame

The prototype was developed and tested primarily with:

**Python 3.12**

and

**Pygame 2.6.1**

---

# Installation

Install Python and Pygame before running the game.

Using Python 3.12:

```bash
py -3.12 -m pip install pygame
```

Clone or download the repository and enter the project directory.

Then run:

```bash
py -3.12 main.py
```

To perform a Python syntax check before launching:

```bash
py -3.12 -m py_compile main.py
```

---

# Current Version

## Experiment Zero v0.4.0

Major implemented systems include:

- Single Player
- Local Two Player
- Four pellet types
- Growth mechanics
- Reduction mechanics
- Minimum organism length
- Independent speed manipulation
- Independent multiplayer movement speeds
- Score tracking
- Persistent high score
- 120-second experiments
- Experiment countdown
- Pause system
- Frozen timer while paused
- Containment boundaries
- Pellet spawn safety
- Self-collision detection
- Multiplayer specimen collision
- Containment failure
- Winner detection
- Draw detection
- Temporary pellet feedback
- Main menu
- Options menu
- Dynamic window titles
- Persistent unlock system
- Unlockable Sound Mode
- Programmatically generated retro sound effects
- Unlockable Classic Black & White Mode
- Unlockable Classic Game Boy Mode
- Custom bitmap typography
- Game Boy LCD-style presentation

---

# Development Status

**Omega Pellets: Experiment Zero v0.4.0 is considered the feature-complete baseline of the original prototype.**

A backup of this version should be preserved as development continues.

Future development can build upon Experiment Zero without erasing the original simulation that started the project.

---

# Project Philosophy

Omega Pellets began with a deliberately simple question:

**What can be built from the basic idea of Snake if the pellets themselves become part of the strategy?**

Experiment Zero answers that question in its simplest form.

Growth can help or hurt.

Shrinking can become useful.

Speed can become an advantage or a liability.

Slowing down can provide control.

Two players can compete while simultaneously being responsible for keeping the experiment alive.

The primitive presentation is intentional.

Experiment Zero is not intended to hide where Omega Pellets started.

It is intended to preserve it.

---

# License

A license has not yet been selected for Omega Pellets.

Unless a license is added to the repository, the presence of publicly viewable source code should not be interpreted as permission to redistribute, modify, or commercially use the project.

---

# Credits

## Omega Pellets

Created and developed by **Omega Katana**

Built using **Python** and **Pygame**.

---

**WELCOME TO EXPERIMENT ZERO**
