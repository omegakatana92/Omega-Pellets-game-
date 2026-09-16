import pygame
import sys
import random
import json
from pathlib import Path

pygame.init()

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    SOUND_AVAILABLE = True
except pygame.error:
    SOUND_AVAILABLE = False

def make_tone(frequency, duration_ms, volume=0.22):
    if not SOUND_AVAILABLE:
        return None
    import math
    import array
    sample_rate = 22050
    count = int(sample_rate * duration_ms / 1000)
    samples = array.array("h")
    amplitude = int(32767 * volume)
    for i in range(count):
        # Square wave gives the unlockable sound mode a deliberately retro feel.
        phase = (i * frequency / sample_rate) % 1.0
        samples.append(amplitude if phase < 0.5 else -amplitude)
    return pygame.mixer.Sound(buffer=samples.tobytes())

SFX_PELLET = make_tone(660, 65)
SFX_CRASH = make_tone(120, 220)
SFX_END = make_tone(330, 300)
SFX_MENU_CURSOR = make_tone(880, 45, 0.14)

def play_sfx(sound):
    if sound is not None:
        sound.play()

# ============================================================
# OMEGA LABS VOICE SYSTEM - v0.7.7
# ============================================================
VOICE_DIR = Path(__file__).resolve().parent / "assets" / "audio" / "voice"
VOICE_FILES = {
    "MENU_1P": "single player mode.wav",
    "MENU_2P": "2 player mode.wav",
    "MENU_OPTIONS": "options.wav",
    "MENU_CREDITS": "game credits.wav",
    "COUNT_3": "3.wav",
    "COUNT_2": "2.wav",
    "COUNT_1": "1.wav",
    "COUNT_BEGIN": "begin.wav",
    "BIOMASS_UP": "biomass increased.wav",
    "BIOMASS_DOWN": "biomass reduced.wav",
    "VELOCITY_UP": "velocity increased.wav",
    "VELOCITY_DOWN": "velocity reduced.wav",
}
VOICE_SOUNDS = {}
VOICE_CHANNEL = None

if SOUND_AVAILABLE:
    try:
        VOICE_CHANNEL = pygame.mixer.Channel(1)
        for voice_key, filename in VOICE_FILES.items():
            path = VOICE_DIR / filename
            if path.exists():
                VOICE_SOUNDS[voice_key] = pygame.mixer.Sound(str(path))
            else:
                print(f"[OMEGA] VOICE FILE MISSING // {path}")
    except pygame.error as exc:
        print(f"[OMEGA] VOICE SYSTEM ERROR // {exc}")

def play_voice(voice_key):
    """Play one Omega Labs announcement without disturbing streamed music."""
    sound = VOICE_SOUNDS.get(voice_key)
    if sound is None or VOICE_CHANNEL is None:
        return
    VOICE_CHANNEL.stop()
    VOICE_CHANNEL.play(sound)

def announce_menu_selection(selection):
    voice_key = ("MENU_1P", "MENU_2P", "MENU_OPTIONS", "MENU_CREDITS")[selection]
    play_voice(voice_key)

_last_countdown_voice = None

def update_countdown_voice():
    """Synchronize recorded 3-2-1-BEGIN clips to the visible countdown."""
    global _last_countdown_voice
    if screen_state != "COUNTDOWN":
        _last_countdown_voice = None
        return

    elapsed = pygame.time.get_ticks() - countdown_start_time
    # Modern mode has a four-second lab initialization before the visible count.
    phase_elapsed = elapsed if visual_mode == "PROTOTYPE" else elapsed - 4000
    if phase_elapsed < 0 or phase_elapsed >= 4000:
        return

    if phase_elapsed < 1000:
        token = "COUNT_3"
    elif phase_elapsed < 2000:
        token = "COUNT_2"
    elif phase_elapsed < 3000:
        token = "COUNT_1"
    else:
        token = "COUNT_BEGIN"

    if token != _last_countdown_voice:
        _last_countdown_voice = token
        play_voice(token)

# ============================================================
# OMEGA PELLETS SOUNDTRACK SYSTEM - v0.7.6
# ============================================================
# Keep music files in assets/audio beside main.py. The game changes tracks
# automatically as the player moves between the lab terminal and experiments.
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.70
MUSIC_COUNTDOWN_VOLUME = 0.28
MUSIC_PAUSED_VOLUME = 0.24
AUDIO_DIR = Path(__file__).resolve().parent / "assets" / "audio"
MUSIC_TRACKS = {
    "MENU": AUDIO_DIR / "80s Mysterywave music.mp3",
    "OPTIONS": AUDIO_DIR / "assembly_not_required.ogg",
    "1P": AUDIO_DIR / "Karl Casey - Scanner.mp3",
    "2P": AUDIO_DIR / "Karl Casey - Deadly Force.mp3",
    "CREDITS": AUDIO_DIR / "Alexander Ehlers - Warped.mp3",
    "LORE": AUDIO_DIR / "Alexander Ehlers - Flags.mp3",
}
_current_music_key = None
_music_state_signature = None

def _start_music(key, volume=MUSIC_VOLUME, fade_ms=650):
    global _current_music_key
    if not SOUND_AVAILABLE or not MUSIC_ENABLED or key not in MUSIC_TRACKS:
        return
    path = MUSIC_TRACKS[key]
    if not path.exists():
        print(f"[OMEGA] MUSIC FILE MISSING // {path}")
        return
    try:
        if _current_music_key != key:
            pygame.mixer.music.fadeout(250)
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            _current_music_key = key
            print(f"[OMEGA] MUSIC // {key} // ONLINE")
        else:
            pygame.mixer.music.set_volume(volume)
    except pygame.error as exc:
        print(f"[OMEGA] MUSIC ERROR // {exc}")

def sync_music():
    """Synchronize soundtrack with the scientist-terminal/session state."""
    global _music_state_signature, _current_music_key
    signature = (screen_state, game_mode, paused, visual_mode)
    if signature == _music_state_signature:
        return
    _music_state_signature = signature

    if screen_state == "INTRO":
        # Omega Katana production card is intentionally silent.
        if SOUND_AVAILABLE and MUSIC_ENABLED:
            pygame.mixer.music.stop()
        _current_music_key = None
    elif screen_state == "LORE":
        _start_music("LORE", MUSIC_VOLUME, 1000)
    elif screen_state in ("LORE_OUTRO", "TERMINAL_BOOT", "CODE_BOOT"):
        # Story score has ended. Workstation/OS boot uses beeps only.
        if SOUND_AVAILABLE and MUSIC_ENABLED and pygame.mixer.music.get_busy():
            if screen_state == "LORE_OUTRO":
                pygame.mixer.music.fadeout(900)
            else:
                pygame.mixer.music.stop()
        _current_music_key = None
    elif screen_state == "MENU":
        _start_music("MENU", MUSIC_VOLUME, 800)
    elif screen_state in ("OPTIONS", "CONCEPT_ART"):
        _start_music("OPTIONS", MUSIC_VOLUME, 600)
    elif screen_state == "CREDITS":
        _start_music("CREDITS", MUSIC_VOLUME, 800)
    elif screen_state == "COUNTDOWN":
        # The experiment track enters quietly underneath initialization and
        # the 3-2-1 countdown, then reaches full level at BEGIN.
        _start_music("2P" if game_mode == 2 else "1P", MUSIC_COUNTDOWN_VOLUME, 1000)
    elif screen_state == "PLAYING":
        _start_music("2P" if game_mode == 2 else "1P",
                     MUSIC_PAUSED_VOLUME if paused else MUSIC_VOLUME, 250)
    elif screen_state == "EXITING_TO_MENU":
        # Shutdown owns the silence; the menu theme returns with its fade-in.
        if SOUND_AVAILABLE and MUSIC_ENABLED:
            pygame.mixer.music.fadeout(1800)
        _current_music_key = None

# ============================================================
# OMEGA PELLETS
# EXPERIMENT ZERO
# v0.8.2 - Lore / Scientist Terminal / System Boot Transition
# ============================================================

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20

GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Colors
BACKGROUND = (10, 10, 10)
GRID_COLOR = (25, 25, 25)

# Player 1 - white/gray
SNAKE_COLOR = (210, 210, 210)
HEAD_COLOR = (255, 255, 255)

# Player 2 - red
PLAYER2_COLOR = (220, 60, 60)
PLAYER2_HEAD_COLOR = (255, 100, 100)

TEXT_COLOR = (220, 220, 220)
PELLET_COLOR = (80, 255, 100)
REDUCTION_COLOR = (255, 220, 80)
SPEED_COLOR = (255, 80, 80)
SLOW_COLOR = (80, 180, 255)
DEATH_COLOR = (255, 70, 70)

# Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Omega Pellets - Experiment Zero - Two Player")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 23)
large_font = pygame.font.Font(None, 56)

# Authentic-looking built-in bitmap fonts for the retro themes.
# These are rendered from tiny pixel glyph maps, so no external TTF/font file
# is required and Windows cannot substitute a serif/system font.

BITMAP_5X7 = {
    "A":["01110","10001","10001","11111","10001","10001","10001"],
    "B":["11110","10001","10001","11110","10001","10001","11110"],
    "C":["01111","10000","10000","10000","10000","10000","01111"],
    "D":["11110","10001","10001","10001","10001","10001","11110"],
    "E":["11111","10000","10000","11110","10000","10000","11111"],
    "F":["11111","10000","10000","11110","10000","10000","10000"],
    "G":["01111","10000","10000","10111","10001","10001","01111"],
    "H":["10001","10001","10001","11111","10001","10001","10001"],
    "I":["11111","00100","00100","00100","00100","00100","11111"],
    "J":["00111","00010","00010","00010","10010","10010","01100"],
    "K":["10001","10010","10100","11000","10100","10010","10001"],
    "L":["10000","10000","10000","10000","10000","10000","11111"],
    "M":["10001","11011","10101","10101","10001","10001","10001"],
    "N":["10001","11001","10101","10011","10001","10001","10001"],
    "O":["01110","10001","10001","10001","10001","10001","01110"],
    "P":["11110","10001","10001","11110","10000","10000","10000"],
    "Q":["01110","10001","10001","10001","10101","10010","01101"],
    "R":["11110","10001","10001","11110","10100","10010","10001"],
    "S":["01111","10000","10000","01110","00001","00001","11110"],
    "T":["11111","00100","00100","00100","00100","00100","00100"],
    "U":["10001","10001","10001","10001","10001","10001","01110"],
    "V":["10001","10001","10001","10001","10001","01010","00100"],
    "W":["10001","10001","10001","10101","10101","10101","01010"],
    "X":["10001","10001","01010","00100","01010","10001","10001"],
    "Y":["10001","10001","01010","00100","00100","00100","00100"],
    "Z":["11111","00001","00010","00100","01000","10000","11111"],
    "0":["01110","10001","10011","10101","11001","10001","01110"],
    "1":["00100","01100","00100","00100","00100","00100","01110"],
    "2":["01110","10001","00001","00010","00100","01000","11111"],
    "3":["11110","00001","00001","01110","00001","00001","11110"],
    "4":["00010","00110","01010","10010","11111","00010","00010"],
    "5":["11111","10000","10000","11110","00001","00001","11110"],
    "6":["01110","10000","10000","11110","10001","10001","01110"],
    "7":["11111","00001","00010","00100","01000","01000","01000"],
    "8":["01110","10001","10001","01110","10001","10001","01110"],
    "9":["01110","10001","10001","01111","00001","00001","01110"],
    " ":["00000"]*7,
    ":":["00000","00100","00100","00000","00100","00100","00000"],
    "/":["00001","00010","00010","00100","01000","01000","10000"],
    "[":["01110","01000","01000","01000","01000","01000","01110"],
    "]":["01110","00010","00010","00010","00010","00010","01110"],
    "-":["00000","00000","00000","11111","00000","00000","00000"],
    "+":["00000","00100","00100","11111","00100","00100","00000"],
    "=":["00000","11111","00000","11111","00000","00000","00000"],
    ".":["00000","00000","00000","00000","00000","00110","00110"],
    "&":["01100","10010","10100","01000","10101","10010","01101"],
}

class BitmapFont:
    def __init__(self, scale=3, style="classic"):
        self.scale = scale
        self.style = style

    def _glyph(self, ch):
        return BITMAP_5X7.get(ch.upper(), BITMAP_5X7[" "])

    def size(self, message):
        width = 0
        for ch in str(message):
            glyph = self._glyph(ch)
            glyph_w = len(glyph[0])
            width += (glyph_w + 1) * self.scale
        if width:
            width -= self.scale
        return width, 7 * self.scale

    def render(self, message, antialias, color, background=None):
        message = str(message)
        w, h = self.size(message)
        surf = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        if background is not None:
            surf.fill(background)

        xoff = 0
        for ch in message:
            glyph = self._glyph(ch)
            gw = len(glyph[0])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        # Game Boy uses chunky square LCD pixels.
                        # Classic uses a slightly narrower Atari-era cell.
                        if self.style == "gameboy":
                            rect = (xoff + col*self.scale, row*self.scale,
                                    self.scale, self.scale)
                        else:
                            rect = (xoff + col*self.scale, row*self.scale,
                                    max(1, self.scale-1), self.scale)
                        pygame.draw.rect(surf, color, rect)
            xoff += (gw + 1) * self.scale
        return surf

classic_font = BitmapFont(3, "classic")
classic_small_font = BitmapFont(2, "classic")
classic_large_font = BitmapFont(6, "classic")

gameboy_font = BitmapFont(3, "gameboy")
gameboy_small_font = BitmapFont(2, "gameboy")
gameboy_large_font = BitmapFont(6, "gameboy")

# Finished-game laboratory typography. Prefer Windows Bahnschrift for its
# squared technical forms; fall back cleanly when unavailable.
def _make_scifi_font(size, bold=False):
    # Use technical/angular fonts commonly available on Windows.
    # No external font asset is required.
    candidates = ("bahnschrift", "agencyfb", "bankgothic", "eurostile", "consolas")
    path = None
    for name in candidates:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            break
    f = pygame.font.Font(path, size) if path else pygame.font.Font(None, size)
    f.set_bold(bold)
    return f

scifi_font = _make_scifi_font(27, True)
scifi_small_font = _make_scifi_font(18, False)
scifi_large_font = _make_scifi_font(56, True)

def active_fonts():
    if visual_mode == "CLASSIC":
        return classic_font, classic_small_font, classic_large_font
    if visual_mode == "GAMEBOY":
        return gameboy_font, gameboy_small_font, gameboy_large_font
    return scifi_font, scifi_small_font, scifi_large_font


# Independent movement timers
MOVE_EVENT_P1 = pygame.USEREVENT + 1
MOVE_EVENT_P2 = pygame.USEREVENT + 2

MOVE_DELAY = 120
ROUND_TIME = 120

UNLOCK_FILE = Path.home() / ".omega_pellets_unlocks.json"

def load_unlocks():
    data = {
        "high_score": 0,
        "concept_art_unlocked": False,
        "prototype_unlocked": False,
        "classic_unlocked": False,
        "gameboy_unlocked": False,
    }
    try:
        if UNLOCK_FILE.exists():
            saved = json.loads(UNLOCK_FILE.read_text(encoding="utf-8"))
            for key in data:
                if key in saved:
                    data[key] = saved[key]
    except Exception:
        pass
    return data

def save_unlocks():
    try:
        UNLOCK_FILE.write_text(json.dumps(unlocks, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"[OMEGA] Could not save unlock progress: {exc}")

def refresh_unlocks(score):
    changed = False
    if score > unlocks["high_score"]:
        unlocks["high_score"] = score
        changed = True
    unlock_table = (
        (5, "concept_art_unlocked", "CONCEPT ART ARCHIVE"),
        (25, "prototype_unlocked", "EXPERIMENT ZERO PROTOTYPE"),
        (50, "classic_unlocked", "CLASSIC BLACK & WHITE"),
        (75, "gameboy_unlocked", "CLASSIC GAME BOY"),
    )
    for threshold, key, label in unlock_table:
        if score >= threshold and not unlocks[key]:
            unlocks[key] = True
            changed = True
            print(f"[OMEGA] UNLOCKED: {label}")
    if changed:
        save_unlocks()

# Migrate older save files automatically from their persistent high score.
# This call must happen after `unlocks = load_unlocks()` below.

def current_best_score():
    if game_mode == 2:
        return max(score_p1, score_p2)
    return score_p1

unlocks = load_unlocks()
refresh_unlocks(unlocks["high_score"])

# Dedicated HUD / legend containment zones.
# The organism may only move between these rows.
PLAYFIELD_TOP_ROW = 5
PLAYFIELD_BOTTOM_ROW = GRID_HEIGHT - 3


# ============================================================
# PELLET SPAWNING
# ============================================================

def spawn_pellet(blocked_positions=None):
    if blocked_positions is None:
        blocked_positions = []

    # Keep pellets away from the HUD, bottom legend,
    # outer walls, and the specimens' immediate starting areas.
    min_x = 2
    max_x = GRID_WIDTH - 3
    min_y = PLAYFIELD_TOP_ROW
    max_y = PLAYFIELD_BOTTOM_ROW

    if game_mode == 1:
        occupied = snake_p1
        heads = [snake_p1[0]]
    else:
        occupied = snake_p1 + snake_p2
        heads = [snake_p1[0], snake_p2[0]]

    while True:
        position = (
            random.randint(min_x, max_x),
            random.randint(min_y, max_y)
        )

        # Give each head a small safety zone so a pellet does
        # not begin directly beside a newly spawned specimen.
        too_close_to_head = any(
            abs(position[0] - head[0])
            + abs(position[1] - head[1])
            <= 3
            for head in heads
        )

        if (
            position not in occupied
            and position not in blocked_positions
            and not too_close_to_head
        ):
            return position


# ============================================================
# RESET EXPERIMENT
# ============================================================

def theme():
    if visual_mode == "CLASSIC":
        return {"bg":(0,0,0),"grid":(0,0,0),"text":(255,255,255),
                "p1":(255,255,255),"h1":(255,255,255),"p2":(170,170,170),"h2":(255,255,255),
                "grow":(255,255,255),"shrink":(255,255,255),"speed":(255,255,255),"slow":(255,255,255)}
    if visual_mode == "GAMEBOY":
        return {"bg":(155,188,15),"grid":(139,172,15),"text":(15,56,15),
                "p1":(15,56,15),"h1":(8,40,8),"p2":(15,56,15),"h2":(8,40,8),
                "grow":(15,56,15),"shrink":(48,98,48),"speed":(15,56,15),"slow":(48,98,48)}
    return {"bg":BACKGROUND,"grid":GRID_COLOR,"text":TEXT_COLOR,
            "p1":SNAKE_COLOR,"h1":HEAD_COLOR,"p2":PLAYER2_COLOR,"h2":PLAYER2_HEAD_COLOR,
            "grow":PELLET_COLOR,"shrink":REDUCTION_COLOR,"speed":SPEED_COLOR,"slow":SLOW_COLOR}


def set_visual_mode(mode):
    global visual_mode
    visual_mode = mode
    print(f"[OMEGA] Visual mode: {mode}")


def draw_options():
    """Omega Labs configuration/archive terminal, styled to match the main menu."""
    import math
    font, small_font, large_font = active_fonts()
    c = theme()

    # Preserve simple archival presentation when a retro visual mode is active.
    if visual_mode in ("CLASSIC", "GAMEBOY"):
        screen.fill(c["bg"])
        draw_grid()
        title = large_font.render("OPTIONS // ARCHIVE", True, c["text"])
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))
        high = small_font.render(f"HIGH SCORE // {unlocks['high_score']:03d}", True, c["text"])
        screen.blit(high, high.get_rect(center=(WIDTH // 2, 100)))
        labels = ["CONCEPT ART", "EXPERIMENT ZERO PROTOTYPE", "MODERN OMEGA PELLETS", "CLASSIC BLACK & WHITE", "CLASSIC GAME BOY"]
        for i, label in enumerate(labels):
            prefix = "> " if i == options_selection else "  "
            surf = font.render(prefix + label, True, c["text"])
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 175 + i * 58)))
        controls = small_font.render("UP/DOWN // NAVIGATE     ENTER // SELECT     ESC // RETURN", True, c["text"])
        screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 535)))
        return

    now = pygame.time.get_ticks()
    screen.fill((3, 17, 22))
    cyan_dim = (43, 105, 116)
    cyan = (104, 221, 232)
    pale = (190, 231, 235)
    dim = (76, 164, 176)
    locked_col = (82, 116, 122)
    blink = "_" if (now // 500) % 2 == 0 else " "

    # Same restrained aquatic terminal environment as the main menu.
    for y in range(0, HEIGHT, 40):
        shade = 13 + ((y // 40) % 2) * 3
        pygame.draw.line(screen, (3, shade + 8, shade + 11), (0, y), (WIDTH, y), 1)
    for i in range(14):
        x = 35 + ((i * 101) % (WIDTH - 70))
        travel = (now // (32 + (i % 4) * 8) + i * 47) % (HEIGHT + 80)
        y = HEIGHT + 30 - travel
        pygame.draw.circle(screen, (16, 63, 72), (x, y), 1 + (i % 2), 1)

    # Extremely faint Large Serpent shadow; interface remains dominant.
    shadow = pygame.Surface((280, 165), pygame.SRCALPHA)
    swim = int(7 * math.sin(now / 1900.0))
    body = [(18,76),(40,55),(88,48),(138,50),(194,57),(232,65),(254,79),(236,92),(194,99),(140,102),(88,99),(42,95),(18,87)]
    body = [(x, y + swim//3) for x, y in body]
    pygame.draw.polygon(shadow, (4, 28, 33, 82), body)
    for x,h in ((67,18),(91,23),(116,20),(143,25),(169,21),(195,18),(220,16)):
        pygame.draw.polygon(shadow, (4, 28, 33, 82), [(x,55+swim//3),(x+7,55-h+swim//3),(x+14,58+swim//3)])
    pygame.draw.lines(shadow, (4, 28, 33, 82), False, [(235,76+swim//3),(258,60+swim//3),(270,35+swim//3),(268,15+swim//3)], 18)
    screen.blit(shadow, (515 + int(6*math.sin(now/2700.0)), 112))

    pygame.draw.rect(screen, cyan_dim, (10, 10, WIDTH - 20, HEIGHT - 20), 1)
    pygame.draw.line(screen, cyan_dim, (20, 91), (780, 91), 1)

    # Laboratory header / live access data.
    packet = (now // 420) % 1000000
    left = ["OMEGA LABS // SYSTEM CONFIGURATION", "ARCHIVE DATABASE // ONLINE" + blink, f"DATA PACKET // {packet:06d}"]
    right = ["SPECIMEN RESEARCH ARCHIVE", f"HIGH SCORE // {unlocks['high_score']:03d}", "ACCESS CONTROL // ACTIVE"]
    for i, text in enumerate(left):
        surf = scifi_small_font.render(text, True, (79, 155, 166)); screen.blit(surf, (24, 18 + i * 20))
    for i, text in enumerate(right):
        surf = scifi_small_font.render(text, True, (79, 155, 166)); screen.blit(surf, (WIDTH - 24 - surf.get_width(), 18 + i * 20))

    heading = _make_scifi_font(35, True).render("SYSTEM CONFIGURATION", True, pale)
    subheading = scifi_small_font.render("OPTIONS // ARCHIVE", True, dim)
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 116)))
    screen.blit(subheading, subheading.get_rect(center=(WIDTH // 2, 147)))

    # Sound is standard equipment now, not an unlockable.
    sys_box = pygame.Rect(175, 163, 450, 43)
    pygame.draw.rect(screen, (2, 15, 19), sys_box)
    pygame.draw.rect(screen, (36, 82, 90), sys_box, 1)
    screen.blit(scifi_small_font.render("SYSTEM // SOUND EFFECTS", True, pale), (190, 169))
    sound_status = "ACTIVE FROM START" if SOUND_AVAILABLE else "AUDIO DEVICE UNAVAILABLE"
    ss = scifi_small_font.render(sound_status, True, dim)
    screen.blit(ss, (sys_box.right - ss.get_width() - 15, 181))

    entries = [
        ("CONCEPT ART ARCHIVE", unlocks["concept_art_unlocked"], 5, "CONCEPT"),
        ("EXPERIMENT ZERO PROTOTYPE", unlocks["prototype_unlocked"], 25, "PROTOTYPE"),
        ("MODERN OMEGA PELLETS", True, 0, "EXPERIMENT"),
        ("CLASSIC BLACK & WHITE", unlocks["classic_unlocked"], 50, "CLASSIC"),
        ("CLASSIC GAME BOY", unlocks["gameboy_unlocked"], 75, "GAMEBOY"),
    ]
    box_x, box_w, box_h, first_y, gap = 150, 500, 51, 218, 56
    for i, (label, available, requirement, mode) in enumerate(entries):
        y = first_y + i * gap
        selected = i == options_selection
        active = mode in ("EXPERIMENT", "CLASSIC", "GAMEBOY") and visual_mode == mode
        border = cyan if selected else (42, 84, 92)
        fill = (3, 25, 30) if selected else (2, 13, 17)
        pygame.draw.rect(screen, fill, (box_x, y, box_w, box_h))
        pygame.draw.rect(screen, border, (box_x, y, box_w, box_h), 2 if selected else 1)
        if selected:
            ax, ay = box_x + 17, y + box_h // 2
            pygame.draw.polygon(screen, cyan, [(ax, ay-7),(ax+11, ay),(ax, ay+7),(ax+3, ay)])
        label_col = cyan if selected else (pale if available else locked_col)

        # Keep archive names and state badges in separate columns.  Long names
        # (especially EXPERIMENT ZERO PROTOTYPE) are reduced only as much as
        # necessary so they can never run underneath [LOCKED]/[AVAILABLE].
        status_right = box_x + box_w - 12
        status_left = box_x + box_w - 118
        label_left = box_x + 48
        label_right = status_left - 14
        label_font = scifi_font
        label_surface = label_font.render(label, True, label_col)
        if label_surface.get_width() > label_right - label_left:
            label_font = _make_scifi_font(19, True)
            label_surface = label_font.render(label, True, label_col)
        screen.blit(label_surface, (label_left, y + 3))

        if active:
            status = "[ ACTIVE ]"
        elif available:
            status = "[ AVAILABLE ]"
        else:
            status = "[ LOCKED ]"
        st = scifi_small_font.render(status, True, cyan if (selected and available) else (dim if available else locked_col))
        screen.blit(st, (status_right - st.get_width(), y + 7))
        if available:
            detail = "ACCESS // GRANTED" if mode in ("CONCEPT", "PROTOTYPE") else "VISUAL PROFILE // READY"
        else:
            detail = f"ACCESS REQUIREMENT // SCORE {requirement:03d}"
        screen.blit(scifi_small_font.render(detail, True, dim if available else locked_col), (box_x + 48, y + 29))

    # Dedicated control strip, event log, and footer to mirror the main menu hierarchy.
    nav_y = 510
    pygame.draw.line(screen, (26, 69, 77), (20, nav_y - 10), (780, nav_y - 10), 1)
    controls = scifi_small_font.render("↑↓ // NAVIGATE     ENTER // SELECT     ESC // RETURN", True, (77, 151, 161))
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, nav_y)))

    selected_entry = entries[options_selection]
    if selected_entry[1]:
        log_text = "ARCHIVE ACCESS // READY" if selected_entry[3] in ("CONCEPT", "PROTOTYPE") else "VISUAL PROFILE // READY"
    else:
        log_text = f"ACCESS DENIED // SCORE {selected_entry[2]:03d} REQUIRED"
    log_box = pygame.Rect(18, 530, WIDTH - 36, 31)
    pygame.draw.rect(screen, (3, 14, 18), log_box)
    pygame.draw.rect(screen, (31, 78, 87), log_box, 1)
    screen.blit(scifi_small_font.render("SYSTEM LOG // " + log_text + blink, True, (65, 143, 154)), (28, 537))

    footer = scifi_small_font.render("OMEGA PRODUCTIONS 2026", True, (113, 181, 190))
    screen.blit(footer, footer.get_rect(center=(WIDTH // 2, 576)))

CONCEPT_ART = [
    ("ORIGINAL MENU CONCEPT", "01_original_menu_concept.png"),
    ("PELLET + TANK CONCEPT", "02_pellet_tank_concept.png"),
    ("SERPENT FORM STUDY", "03_serpent_forms_sketch.png"),
    ("SERPENT SPRITE SHEET", "04_serpent_sprite_sheet.png"),
    ("INTERFACE + FONT STUDY", "05_interface_font_study.png"),
    ("EXPERIMENT ZERO PROTOTYPE", "06_experiment_zero_pause.png"),
    ("MAIN MENU STUDY A", "07_menu_study_a.png"),
    ("MAIN MENU STUDY B", "08_menu_study_b.png"),
    ("MAIN MENU STUDY C", "09_menu_study_c.png"),
    ("MAIN MENU STUDY D", "10_menu_study_d.png"),
]
concept_art_index = 0

def _concept_asset_path(filename):
    return Path(__file__).resolve().parent / "assets" / "concept_art" / filename

def draw_concept_art():
    screen.fill((3, 13, 17))
    cyan = (100, 205, 218)
    pale = (190, 231, 235)
    dim = (72, 145, 156)
    title, filename = CONCEPT_ART[concept_art_index]
    pygame.draw.rect(screen, dim, (10, 10, WIDTH - 20, HEIGHT - 20), 1)
    head = scifi_font.render("CONCEPT ART ARCHIVE // UNLOCKED", True, pale)
    screen.blit(head, head.get_rect(center=(WIDTH // 2, 30)))
    label = scifi_small_font.render(f"{concept_art_index+1:02d} / {len(CONCEPT_ART):02d} // {title}", True, cyan)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 62)))
    image_box = pygame.Rect(42, 86, WIDTH - 84, 430)
    pygame.draw.rect(screen, (2, 8, 11), image_box)
    pygame.draw.rect(screen, dim, image_box, 1)
    try:
        art = pygame.image.load(str(_concept_asset_path(filename))).convert_alpha()
        max_w, max_h = image_box.width - 20, image_box.height - 20
        scale = min(max_w / art.get_width(), max_h / art.get_height())
        size = (max(1, int(art.get_width()*scale)), max(1, int(art.get_height()*scale)))
        art = pygame.transform.smoothscale(art, size)
        screen.blit(art, art.get_rect(center=image_box.center))
    except Exception:
        missing = scifi_small_font.render("ARCHIVE IMAGE NOT FOUND // KEEP ASSETS FOLDER BESIDE main.py", True, pale)
        screen.blit(missing, missing.get_rect(center=image_box.center))
    controls = scifi_small_font.render("LEFT / RIGHT // BROWSE     ESC // RETURN", True, dim)
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 552)))

def update_window_title():
    """Keep the Windows title bar synchronized with the active mode."""
    if screen_state == "MENU":
        title = "Omega Pellets"
    elif visual_mode == "PROTOTYPE" and game_mode == 1:
        title = "Omega Pellets - Experiment Zero - Single Player"
    elif visual_mode == "PROTOTYPE" and game_mode == 2:
        title = "Omega Pellets - Experiment Zero - Two Player"
    elif game_mode == 1:
        title = "Omega Pellets - Single Player"
    else:
        title = "Omega Pellets - Two Player"

    pygame.display.set_caption(title)


def reset_game(mode):
    global snake_p1
    global snake_p2
    global direction_p1
    global direction_p2
    global game_over
    global game_over_reason
    global loser
    global score_p1
    global score_p2
    global move_delay_p1
    global move_delay_p2
    global round_start_time
    global pellet
    global reduction_pellet
    global speed_pellet
    global slow_pellet
    global game_mode
    global screen_state
    global countdown_start_time
    global feedback_messages
    global paused
    global pause_started_time
    global game_over_time
    global resume_notice_until
    global _last_countdown_voice

    game_mode = mode
    screen_state = "COUNTDOWN"
    countdown_start_time = pygame.time.get_ticks()
    update_window_title()
    feedback_messages = []
    paused = False
    pause_started_time = None
    game_over_time = None
    resume_notice_until = 0
    _last_countdown_voice = None

    # P1 begins on the left, moving right.
    snake_p1 = [
        (10, 15),
        (9, 15),
        (8, 15)
    ]

    # P2 begins on the right, moving left.
    snake_p2 = [
        (29, 15),
        (30, 15),
        (31, 15)
    ]

    direction_p1 = (1, 0)
    direction_p2 = (-1, 0)

    game_over = False
    game_over_reason = None
    loser = None

    score_p1 = 0
    score_p2 = 0

    move_delay_p1 = MOVE_DELAY
    move_delay_p2 = MOVE_DELAY

    round_start_time = None

    # Movement remains paused during the countdown.
    pygame.time.set_timer(MOVE_EVENT_P1, 0)
    pygame.time.set_timer(MOVE_EVENT_P2, 0)

    pellet = spawn_pellet()
    reduction_pellet = spawn_pellet([pellet])
    speed_pellet = spawn_pellet([pellet, reduction_pellet])
    slow_pellet = spawn_pellet(
        [pellet, reduction_pellet, speed_pellet]
    )

    if game_mode == 1:
        print("[OMEGA] Single-specimen experiment started.")
    else:
        print("[OMEGA] Two-specimen experiment started.")


# ============================================================
# ROUND / WINNER HELPERS
# ============================================================

def get_time_remaining():
    if round_start_time is None:
        return ROUND_TIME

    # While paused, calculate elapsed time from the exact moment
    # the pause began. This freezes the visible countdown too.
    if game_over and game_over_time is not None:
        # Freeze the experiment clock at the exact instant the round ends.
        current_time = game_over_time
    elif paused and pause_started_time is not None:
        current_time = pause_started_time
    else:
        current_time = pygame.time.get_ticks()

    elapsed_ms = current_time - round_start_time
    elapsed_seconds = elapsed_ms // 1000

    return max(
        0,
        ROUND_TIME - elapsed_seconds
    )


def get_result_message():
    if game_mode == 1:
        return f"FINAL SCORE: {score_p1}"

    if game_over_reason == "CONTAINMENT":
        return "BOTH SPECIMENS FAILED"

    if score_p1 > score_p2:
        return "PLAYER 1 WINS"
    elif score_p2 > score_p1:
        return "PLAYER 2 WINS"
    else:
        return "DRAW"


def end_round(reason, player=None):
    global game_over
    global game_over_reason
    global loser
    global game_over_time

    if game_over:
        return

    game_over_time = pygame.time.get_ticks()
    game_over = True
    game_over_reason = reason
    loser = player

    pygame.time.set_timer(MOVE_EVENT_P1, 0)
    pygame.time.set_timer(MOVE_EVENT_P2, 0)

    refresh_unlocks(current_best_score())
    if reason in ("SELF", "WALL", "HUD_BOUNDARY", "CONTAINMENT"):
        play_sfx(SFX_CRASH)
    else:
        play_sfx(SFX_END)

    print(
        f"[OMEGA] ROUND ENDED - Reason: {reason} | "
        f"P1: {score_p1} | P2: {score_p2}"
    )


# ============================================================
# PELLET FEEDBACK
# ============================================================

def add_feedback(player, message, color):
    if visual_mode == "EXPERIMENT":
        message = {
            "GROW": "BIOMASS +",
            "SHRINK": "BIOMASS -",
            "SPEED +": "VELOCITY +",
            "SPEED -": "VELOCITY -",
        }.get(message, message)

    if player == 1:
        head = snake_p1[0]
    else:
        head = snake_p2[0]

    # Experiment Zero keeps pellet-specific colors.
    # Classic and Game Boy modes use their monochrome LCD/text color.
    feedback_color = color if visual_mode == "EXPERIMENT" else theme()["text"]

    feedback_messages.append(
        {
            "message": message,
            "color": feedback_color,
            "position": head,
            "start_time": pygame.time.get_ticks()
        }
    )


def draw_feedback():
    font, small_font, large_font = active_fonts()
    current_time = pygame.time.get_ticks()

    # Keep each message visible for about 0.8 seconds.
    feedback_messages[:] = [
        item
        for item in feedback_messages
        if current_time - item["start_time"] < 800
    ]

    for item in feedback_messages:
        age = current_time - item["start_time"]

        x = item["position"][0] * CELL_SIZE + CELL_SIZE // 2
        y = item["position"][1] * CELL_SIZE - 10 - age // 35

        feedback_text = small_font.render(
            item["message"],
            True,
            item["color"]
        )

        screen.blit(
            feedback_text,
            feedback_text.get_rect(
                center=(x, y)
            )
        )


# ============================================================
# PELLET EFFECTS
# ============================================================

def respawn_growth():
    global pellet
    pellet = spawn_pellet(
        [reduction_pellet, speed_pellet, slow_pellet]
    )


def respawn_reduction():
    global reduction_pellet
    reduction_pellet = spawn_pellet(
        [pellet, speed_pellet, slow_pellet]
    )


def respawn_speed():
    global speed_pellet
    speed_pellet = spawn_pellet(
        [pellet, reduction_pellet, slow_pellet]
    )


def respawn_slow():
    global slow_pellet
    slow_pellet = spawn_pellet(
        [pellet, reduction_pellet, speed_pellet]
    )


# ============================================================
# MOVE SPECIMEN
# ============================================================

def move_snake(player):
    global score_p1
    global score_p2
    global move_delay_p1
    global move_delay_p2

    if game_over:
        return

    if player == 1:
        snake = snake_p1
        other_snake = snake_p2 if game_mode == 2 else []
        direction = direction_p1
    else:
        snake = snake_p2
        other_snake = snake_p1
        direction = direction_p2

    head_x, head_y = snake[0]

    new_head = (
        head_x + direction[0],
        head_y + direction[1]
    )

    # --------------------------------------------------------
    # WALL COLLISION
    # --------------------------------------------------------

    if (
        new_head[0] < 0
        or new_head[0] >= GRID_WIDTH
        or new_head[1] < PLAYFIELD_TOP_ROW
        or new_head[1] > PLAYFIELD_BOTTOM_ROW
    ):
        end_round("HUD_BOUNDARY", player)
        return

    eating_growth = new_head == pellet
    eating_reduction = new_head == reduction_pellet
    eating_speed = new_head == speed_pellet
    eating_slow = new_head == slow_pellet

    # --------------------------------------------------------
    # SELF COLLISION
    # --------------------------------------------------------

    if eating_growth:
        body_to_check = snake
    else:
        body_to_check = snake[:-1]

    if new_head in body_to_check:
        end_round("SELF", player)
        return

    # --------------------------------------------------------
    # OTHER SPECIMEN COLLISION
    # Any contact with the other specimen fails both.
    # --------------------------------------------------------

    if new_head in other_snake:
        end_round("CONTAINMENT")
        return

    snake.insert(0, new_head)

    # --------------------------------------------------------
    # GROWTH PELLET
    # --------------------------------------------------------

    if eating_growth:
        if player == 1:
            score_p1 += 1
            refresh_unlocks(score_p1)
            current_score = score_p1
        else:
            score_p2 += 1
            refresh_unlocks(score_p2)
            current_score = score_p2

        play_sfx(SFX_PELLET)
        play_voice("BIOMASS_UP")
        add_feedback(
            player,
            "GROW",
            PELLET_COLOR
        )

        print(
            f"[OMEGA] P{player} growth pellet. "
            f"Score: {current_score}"
        )

        respawn_growth()

    # --------------------------------------------------------
    # REDUCTION PELLET
    # --------------------------------------------------------

    elif eating_reduction:
        if player == 1:
            score_p1 += 1
            refresh_unlocks(score_p1)
            current_score = score_p1
        else:
            score_p2 += 1
            refresh_unlocks(score_p2)
            current_score = score_p2

        # Normal movement removes the tail.
        snake.pop()

        # Remove one extra segment, never below 3.
        if len(snake) > 3:
            snake.pop()

        play_sfx(SFX_PELLET)
        play_voice("BIOMASS_DOWN")
        add_feedback(
            player,
            "SHRINK",
            REDUCTION_COLOR
        )

        print(
            f"[OMEGA] P{player} reduction pellet. "
            f"Score: {current_score}"
        )

        respawn_reduction()

    # --------------------------------------------------------
    # SPEED-UP PELLET
    # --------------------------------------------------------

    elif eating_speed:
        snake.pop()

        if player == 1:
            score_p1 += 1
            refresh_unlocks(score_p1)
            move_delay_p1 = max(50, move_delay_p1 - 10)
            pygame.time.set_timer(
                MOVE_EVENT_P1,
                move_delay_p1
            )
            current_score = score_p1
            current_delay = move_delay_p1
        else:
            score_p2 += 1
            refresh_unlocks(score_p2)
            move_delay_p2 = max(50, move_delay_p2 - 10)
            pygame.time.set_timer(
                MOVE_EVENT_P2,
                move_delay_p2
            )
            current_score = score_p2
            current_delay = move_delay_p2

        play_sfx(SFX_PELLET)
        play_voice("VELOCITY_UP")
        add_feedback(
            player,
            "SPEED +",
            SPEED_COLOR
        )

        print(
            f"[OMEGA] P{player} speed pellet. "
            f"Score: {current_score} | "
            f"Delay: {current_delay} ms"
        )

        respawn_speed()

    # --------------------------------------------------------
    # SLOW-DOWN PELLET
    # --------------------------------------------------------

    elif eating_slow:
        snake.pop()

        if player == 1:
            score_p1 += 1
            refresh_unlocks(score_p1)
            move_delay_p1 = min(200, move_delay_p1 + 10)
            pygame.time.set_timer(
                MOVE_EVENT_P1,
                move_delay_p1
            )
            current_score = score_p1
            current_delay = move_delay_p1
        else:
            score_p2 += 1
            refresh_unlocks(score_p2)
            move_delay_p2 = min(200, move_delay_p2 + 10)
            pygame.time.set_timer(
                MOVE_EVENT_P2,
                move_delay_p2
            )
            current_score = score_p2
            current_delay = move_delay_p2

        play_sfx(SFX_PELLET)
        play_voice("VELOCITY_DOWN")
        add_feedback(
            player,
            "SPEED -",
            SLOW_COLOR
        )

        print(
            f"[OMEGA] P{player} slow pellet. "
            f"Score: {current_score} | "
            f"Delay: {current_delay} ms"
        )

        respawn_slow()

    else:
        snake.pop()


# ============================================================
# DRAWING
# ============================================================

def draw_containment_boundaries():
    """Physical reinforced frame of the aquatic laboratory tank."""
    c = theme()
    top_y = PLAYFIELD_TOP_ROW * CELL_SIZE
    bottom_y = (PLAYFIELD_BOTTOM_ROW + 1) * CELL_SIZE

    if visual_mode != "EXPERIMENT":
        pygame.draw.line(screen, c["text"], (0, top_y), (WIDTH, top_y), 2)
        pygame.draw.line(screen, c["text"], (0, bottom_y), (WIDTH, bottom_y), 2)
        return

    metal = (36, 48, 54)
    metal_hi = (82, 104, 112)
    cyan = (88, 205, 220)
    dark = (10, 19, 24)

    # Top and bottom reinforced tank rails.
    for y in (top_y, bottom_y - 8):
        pygame.draw.rect(screen, metal, (0, y, WIDTH, 8))
        pygame.draw.line(screen, metal_hi, (0, y), (WIDTH, y), 1)
        pygame.draw.line(screen, dark, (0, y + 7), (WIDTH, y + 7), 1)
        for x in range(18, WIDTH, 80):
            pygame.draw.rect(screen, (20, 29, 34), (x, y + 2, 10, 4), border_radius=1)
            pygame.draw.rect(screen, cyan, (x + 2, y + 3, 6, 2), border_radius=1)

    # Reinforced side containment columns.  Keep them narrow so the hardware
    # reads as a physical lab-tank wall without covering useful play space.
    side_w = 12
    tank_h = bottom_y - top_y
    pygame.draw.rect(screen, metal, (0, top_y, side_w, tank_h))
    pygame.draw.rect(screen, metal, (WIDTH - side_w, top_y, side_w, tank_h))

    # Glass-facing inner lips / metallic seams.
    pygame.draw.line(screen, metal_hi, (side_w, top_y), (side_w, bottom_y), 2)
    pygame.draw.line(screen, metal_hi, (WIDTH - side_w - 1, top_y),
                     (WIDTH - side_w - 1, bottom_y), 2)
    pygame.draw.line(screen, dark, (3, top_y), (3, bottom_y), 1)
    pygame.draw.line(screen, dark, (WIDTH - 4, top_y), (WIDTH - 4, bottom_y), 1)

    # Simple armored joints and restrained cyan status lamps.
    joint_h = 26
    for y in range(top_y + 24, bottom_y - joint_h, 78):
        pygame.draw.rect(screen, (22, 31, 36), (1, y, side_w - 2, joint_h), border_radius=2)
        pygame.draw.rect(screen, (22, 31, 36),
                         (WIDTH - side_w + 1, y, side_w - 2, joint_h), border_radius=2)
        pygame.draw.line(screen, metal_hi, (2, y + 2), (side_w - 2, y + 2), 1)
        pygame.draw.line(screen, metal_hi,
                         (WIDTH - side_w + 2, y + 2), (WIDTH - 2, y + 2), 1)
        pygame.draw.rect(screen, cyan, (4, y + 10, 4, 6), border_radius=1)
        pygame.draw.rect(screen, cyan, (WIDTH - 8, y + 10, 4, 6), border_radius=1)

    # Heavier corner mounting blocks tie the side columns into the top/bottom rails.
    corner_h = 18
    for x in (0, WIDTH - side_w):
        pygame.draw.rect(screen, metal_hi, (x, top_y, side_w, corner_h), 1)
        pygame.draw.rect(screen, metal_hi, (x, bottom_y - corner_h, side_w, corner_h), 1)


def draw_grid():
    """Retro modes keep their old grid. Modern mode uses a tank-floor grid."""
    if visual_mode != "EXPERIMENT":
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, theme()["grid"], (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, theme()["grid"], (0, y), (WIDTH, y))
        return

    top_y = PLAYFIELD_TOP_ROW * CELL_SIZE
    bottom_y = (PLAYFIELD_BOTTOM_ROW + 1) * CELL_SIZE
    floor_top = bottom_y - 150
    grid = (22, 48, 55)
    grid_hi = (28, 61, 68)

    # Very restrained dark aquatic water.
    pygame.draw.rect(screen, (5, 17, 23), (0, top_y, WIDTH, bottom_y - top_y))

    # Horizontal floor rows become closer together toward the horizon.
    for i in range(7):
        t = i / 6
        y = int(floor_top + (t * t) * (bottom_y - floor_top))
        pygame.draw.line(screen, grid_hi if i == 6 else grid, (6, y), (WIDTH - 6, y), 1)

    # Perspective floor grid converging toward the center/horizon.
    vanishing = (WIDTH // 2, floor_top)
    for x in range(0, WIDTH + 1, 40):
        pygame.draw.line(screen, grid, vanishing, (x, bottom_y), 1)

    # A few fixed, dim bubbles/particles. No busy animation.
    for bx, by, r in ((92,180,2),(704,245,2),(625,350,1),(165,305,1),(748,420,2)):
        pygame.draw.circle(screen, (28, 66, 74), (bx, by), r, 1)

def _serpent_stage(length):
    if length <= 7:
        return "SMALL"
    if length <= 15:
        return "MID"
    return "LARGE"


def _dir_between(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _rot_points(points, direction, cx, cy):
    """Rotate points authored facing right into the current grid direction."""
    out = []
    for px, py in points:
        dx, dy = px - cx, py - cy
        if direction == (1, 0):       rx, ry = dx, dy
        elif direction == (-1, 0):    rx, ry = -dx, -dy
        elif direction == (0, -1):    rx, ry = dy, -dx
        else:                          rx, ry = -dy, dx
        out.append((int(cx + rx), int(cy + ry)))
    return out


def _draw_serpent_head(segment, direction, body_color, outline):
    """Locked serpent head. The complete face rotates as one sprite."""
    x, y = segment[0] * CELL_SIZE, segment[1] * CELL_SIZE
    cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2

    # Authored facing RIGHT. Slight overhang makes the head read as a creature
    # instead of a vertical/horizontal rectangular grid tile.
    base = [
        (cx-11, cy-8), (cx+5, cy-8), (cx+11, cy-5),
        (cx+13, cy+1), (cx+10, cy+8), (cx+3, cy+11),
        (cx-8, cy+10), (cx-12, cy+5), (cx-12, cy-3)
    ]
    pts = _rot_points(base, direction, cx, cy)
    pygame.draw.polygon(screen, body_color, pts)
    pygame.draw.lines(screen, outline, True, pts, 2)

    # Locked species feature: a large solid-white vicious triangular eye.
    eye = _rot_points([
        (cx+1, cy-6), (cx+10, cy-2), (cx+1, cy+1)
    ], direction, cx, cy)
    pygame.draw.polygon(screen, (255, 255, 255), eye)
    pygame.draw.lines(screen, outline, True, eye, 1)

    # Compact jagged lower jaw/teeth, rotated with the whole head.
    teeth = _rot_points([
        (cx-4,cy+7),(cx-1,cy+10),(cx+1,cy+7),
        (cx+3,cy+10),(cx+5,cy+7),(cx+7,cy+9),(cx+9,cy+6)
    ], direction, cx, cy)
    pygame.draw.lines(screen, outline, False, teeth, 2)


def _draw_serpent_body(segment, prev_seg, next_seg, body_color, outline, stage):
    x, y = segment[0]*CELL_SIZE, segment[1]*CELL_SIZE
    cx, cy = x+CELL_SIZE//2, y+CELL_SIZE//2
    diamond=[(cx,y+1),(x+19,cy),(cx,y+19),(x+1,cy)]
    pygame.draw.polygon(screen, body_color, diamond)
    pygame.draw.lines(screen, outline, True, diamond, 2)
    pygame.draw.circle(screen, outline, (cx,cy), 2)

    # Dorsal spike follows the direction from this segment toward the head.
    local_dir = _dir_between(prev_seg, segment) if prev_seg else (1,0)
    if local_dir == (0,0):
        local_dir=(1,0)
    spike_h = 4 if stage == "SMALL" else 5 if stage == "MID" else 6
    authored=[(cx-3,y+3),(cx,y+3-spike_h),(cx+3,y+3)]
    spike=_rot_points(authored, local_dir, cx, cy)
    pygame.draw.polygon(screen, body_color, spike)
    pygame.draw.lines(screen, outline, True, spike, 1)


def _draw_serpent_tail(segment, toward_body, body_color, outline, stage):
    x,y=segment[0]*CELL_SIZE,segment[1]*CELL_SIZE
    cx,cy=x+CELL_SIZE//2,y+CELL_SIZE//2
    hook = 5 if stage=="SMALL" else 7 if stage=="MID" else 9
    base=[(x,y+6),(x+8,y+5),(x+14,y+1),(x+18,y+1-hook//3),(x+18,y+12),(x+13,y+18),(x+5,y+16),(x,y+14)]
    direction=(-toward_body[0],-toward_body[1])
    pts=_rot_points(base,direction,cx,cy)
    pygame.draw.polygon(screen,body_color,pts)
    pygame.draw.lines(screen,outline,True,pts,2)


def _segment_center(seg):
    return (seg[0]*CELL_SIZE + CELL_SIZE//2, seg[1]*CELL_SIZE + CELL_SIZE//2)


def draw_organism(snake, body_color, head_color):
    c=theme()
    is_p1 = body_color == SNAKE_COLOR
    if is_p1:
        body_color, head_color = c["p1"], c["h1"]
    else:
        body_color, head_color = c["p2"], c["h2"]

    # Preserve the intentionally blocky archived retro modes.
    if visual_mode != "EXPERIMENT":
        for index, segment in enumerate(snake):
            x,y=segment[0]*CELL_SIZE,segment[1]*CELL_SIZE
            color=head_color if index==0 else body_color
            pygame.draw.rect(screen,color,(x,y,CELL_SIZE,CELL_SIZE))
            if visual_mode=="GAMEBOY" and index!=0:
                pygame.draw.rect(screen,(48,98,48),(x+5,y+5,CELL_SIZE-10,CELL_SIZE-10))
        return

    stage=_serpent_stage(len(snake))
    outline=(38,42,43) if is_p1 else (92,18,18)

    # Continuous hidden 'neck/body' ribbon. This is drawn first and fixes the
    # disconnected rectangular look when the head turns 90 degrees.
    if len(snake) > 1:
        centers=[_segment_center(seg) for seg in snake]
        pygame.draw.lines(screen, body_color, False, centers, 10)
        pygame.draw.lines(screen, outline, False, centers, 2)

    # Tail and armor segments sit on top of the connector ribbon.
    if len(snake) >= 2:
        tail_dir=_dir_between(snake[-2],snake[-1])
        _draw_serpent_tail(snake[-1],tail_dir,body_color,outline,stage)

    for i in range(len(snake)-2,0,-1):
        _draw_serpent_body(snake[i],snake[i-1],snake[i+1],body_color,outline,stage)

    # Direction is head minus the first body cell. The COMPLETE head rotates.
    head_dir=_dir_between(snake[0],snake[1]) if len(snake)>1 else (1,0)
    _draw_serpent_head(snake[0],head_dir,head_color,outline)

def pellet_center(position):
    return (
        position[0] * CELL_SIZE + CELL_SIZE // 2,
        position[1] * CELL_SIZE + CELL_SIZE // 2
    )


def _draw_scifi_pellet(position, color, symbol):
    """Compact sci-fi energy capsule for the main Omega Pellets presentation."""
    cx, cy = pellet_center(position)

    # Preserve the deliberately primitive retro pellet graphics in archive modes.
    if visual_mode != "EXPERIMENT":
        radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(screen, color, (cx, cy), radius)
        ink = theme()["bg"]
        if symbol == "+":
            pygame.draw.line(screen, ink, (cx - 5, cy), (cx + 5, cy), 3)
            pygame.draw.line(screen, ink, (cx, cy - 5), (cx, cy + 5), 3)
        elif symbol == "-":
            pygame.draw.line(screen, ink, (cx - 5, cy), (cx + 5, cy), 3)
        elif symbol == "v":
            pygame.draw.line(screen, ink, (cx, cy - 5), (cx, cy + 4), 3)
            pygame.draw.line(screen, ink, (cx, cy + 4), (cx - 4, cy), 3)
            pygame.draw.line(screen, ink, (cx, cy + 4), (cx + 4, cy), 3)
        return

    # Sleek laboratory capsule: dark shell, colored energy ring, bright core.
    shell = (18, 24, 30)
    rim = (118, 136, 148)
    core = (232, 246, 250)
    pygame.draw.circle(screen, shell, (cx, cy), 9)
    pygame.draw.circle(screen, rim, (cx, cy), 8, 1)
    pygame.draw.circle(screen, color, (cx, cy), 6, 2)
    pygame.draw.circle(screen, core, (cx, cy), 2)

    # Small side notches make the pellet read as a manufactured sci-fi device.
    pygame.draw.line(screen, rim, (cx - 9, cy), (cx - 7, cy), 2)
    pygame.draw.line(screen, rim, (cx + 7, cy), (cx + 9, cy), 2)

    # Minimal high-contrast glyph.
    if symbol == "+":
        pygame.draw.line(screen, core, (cx - 3, cy), (cx + 3, cy), 2)
        pygame.draw.line(screen, core, (cx, cy - 3), (cx, cy + 3), 2)
    elif symbol == "-":
        pygame.draw.line(screen, core, (cx - 3, cy), (cx + 3, cy), 2)
    elif symbol == "v":
        pygame.draw.line(screen, core, (cx, cy - 3), (cx, cy + 2), 2)
        pygame.draw.line(screen, core, (cx, cy + 2), (cx - 3, cy - 1), 2)
        pygame.draw.line(screen, core, (cx, cy + 2), (cx + 3, cy - 1), 2)


def draw_pellet():
    # Growth / positive pellet.
    _draw_scifi_pellet(pellet, theme()["grow"], "+")


def draw_reduction_pellet():
    _draw_scifi_pellet(reduction_pellet, theme()["shrink"], "-")


def draw_speed_pellet():
    # Speed-up retains the established plus symbol and red energy signature.
    _draw_scifi_pellet(speed_pellet, theme()["speed"], "+")


def draw_slow_pellet():
    _draw_scifi_pellet(slow_pellet, theme()["slow"], "v")


# ============================================================
# EXPERIMENT COUNTDOWN
# ============================================================

def draw_session_initialization():
    """Modern Omega Labs boot sequence before the experiment becomes interactive."""
    elapsed = pygame.time.get_ticks() - countdown_start_time
    total = 4000
    cyan = (105, 213, 226)
    pale = (194, 232, 236)
    dim = (65, 139, 151)

    # First half is a true black terminal boot. During the second half the
    # containment view fades in underneath the terminal data.
    if elapsed < 1900:
        screen.fill((0, 0, 0))
    else:
        # Gameplay has already been drawn by the main loop. Fade a black veil
        # away from opaque to transparent, revealing the frozen tank beneath.
        t = min(1.0, (elapsed - 1900) / 1500.0)
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, int(255 * (1.0 - t))))
        screen.blit(veil, (0, 0))

    blink = "_" if (pygame.time.get_ticks() // 300) % 2 == 0 else " "

    # Progressive data records: deliberately short, purpose-built lab output.
    if elapsed < 1900:
        lines = [
            (180, "> SESSION REQUEST RECEIVED"),
            (520, "> INITIALIZING AQUATIC CONTAINMENT"),
            (850, "> LOADING SPECIMEN PROFILE"),
            (1180, "CONTAINMENT TANK // ONLINE"),
            (1380, "PELLET DISPENSER // ONLINE"),
            (1580, "MOTION TRACKING // ONLINE"),
            (1750, "DATA ACQUISITION // ONLINE"),
        ]
        y = 155
        header = scifi_small_font.render("OMEGA LAB SYSTEM // SESSION INITIALIZATION", True, dim)
        screen.blit(header, (72, 90))
        pygame.draw.line(screen, (28, 75, 84), (72, 120), (728, 120), 1)
        visible = [(at, text) for at, text in lines if elapsed >= at]
        for i, (_, text) in enumerate(visible):
            suffix = blink if i == len(visible) - 1 else ""
            surf = scifi_small_font.render(text + suffix, True, pale if text.startswith(">") else cyan)
            screen.blit(surf, (92, y))
            y += 36
    else:
        if game_mode == 1:
            specimen = "SPECIMEN 01 // READY"
            protocol = "SINGLE SPECIMEN PROTOCOL // ACTIVE"
        else:
            specimen = "SPECIMEN 01 // READY     SPECIMEN 02 // READY"
            protocol = "DUAL SPECIMEN PROTOCOL // ACTIVE"

        staged = [
            (1900, specimen),
            (2150, protocol),
            (2450, "> ESTABLISHING CONTROL LINK..."),
            (2750, "> CALIBRATING MOTION TRACKING..."),
            (3050, "> SYNCHRONIZING SESSION TIMER..."),
            (3300, "> OPENING CONTAINMENT VIEW..."),
            (3500, "DATA ACQUISITION // ONLINE"),
            (3650, "EXPERIMENT // ACTIVE"),
        ]
        panel = pygame.Surface((700, 230), pygame.SRCALPHA)
        panel.fill((0, 8, 11, 185))
        pygame.draw.rect(panel, (45, 115, 126, 220), panel.get_rect(), 1)
        screen.blit(panel, (50, 185))
        y = 205
        visible = [(at, text) for at, text in staged if elapsed >= at]
        for i, (_, text) in enumerate(visible):
            suffix = blink if i == len(visible) - 1 else ""
            col = cyan if "ONLINE" in text or "ACTIVE" in text or "READY" in text else pale
            surf = scifi_small_font.render(text + suffix, True, col)
            screen.blit(surf, (72, y))
            y += 25

def draw_countdown():
    font, small_font, large_font = active_fonts()
    elapsed = pygame.time.get_ticks() - countdown_start_time

    if elapsed < 1000:
        message = "3"
    elif elapsed < 2000:
        message = "2"
    elif elapsed < 3000:
        message = "1"
    else:
        message = "BEGIN"

    if visual_mode == "CLASSIC":
        countdown_font = BitmapFont(12, "classic")
    elif visual_mode == "GAMEBOY":
        countdown_font = BitmapFont(12, "gameboy")
    else:
        countdown_font = _make_scifi_font(118 if message != "BEGIN" else 92)

    countdown_text = countdown_font.render(message, True, theme()["text"])
    rect = countdown_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    if visual_mode == "EXPERIMENT":
        # Clean laboratory HUD brackets and a restrained cyan-white glow.
        glow = countdown_font.render(message, True, (90, 180, 220))
        glow.set_alpha(55)
        for ox, oy in ((-2,0),(2,0),(0,-2),(0,2)):
            screen.blit(glow, rect.move(ox, oy))

        pad_x, pad_y = 34, 22
        box = rect.inflate(pad_x * 2, pad_y * 2)
        c = (125, 205, 230)
        L = 18
        # four angular HUD corners
        pygame.draw.line(screen, c, box.topleft, (box.left + L, box.top), 2)
        pygame.draw.line(screen, c, box.topleft, (box.left, box.top + L), 2)
        pygame.draw.line(screen, c, box.topright, (box.right - L, box.top), 2)
        pygame.draw.line(screen, c, box.topright, (box.right, box.top + L), 2)
        pygame.draw.line(screen, c, box.bottomleft, (box.left + L, box.bottom), 2)
        pygame.draw.line(screen, c, box.bottomleft, (box.left, box.bottom - L), 2)
        pygame.draw.line(screen, c, box.bottomright, (box.right - L, box.bottom), 2)
        pygame.draw.line(screen, c, box.bottomright, (box.right, box.bottom - L), 2)

    screen.blit(countdown_text, rect)


# ============================================================
# PELLET LEGEND
# ============================================================

def draw_pellet_legend():
    font, small_font, large_font = active_fonts()
    c = theme()
    legend_y = HEIGHT - 35
    if visual_mode == "CLASSIC":
        text = small_font.render("CLASSIC MODE // BLACK & WHITE", True, c["text"])
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT - 28)))
        return
    if visual_mode == "GAMEBOY":
        text = small_font.render("CLASSIC GAME BOY MODE", True, c["text"])
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT - 28)))
        return

    # Scientist computer pellet database panel.
    panel = pygame.Rect(8, 565, WIDTH - 16, 30)
    pygame.draw.rect(screen, (7, 15, 19), panel)
    pygame.draw.rect(screen, (50, 103, 113), panel, 1)
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
    header = small_font.render("PELLET DATABASE // ONLINE" + cursor, True, (118, 201, 214))
    screen.blit(header, (16, 567))

    entries = [
        ("[+] GROWTH // BIOMASS +", PELLET_COLOR, 245),
        ("[-] REDUCTION // BIOMASS -", REDUCTION_COLOR, 385),
        ("[^] ACCEL // VELOCITY +", SPEED_COLOR, 555),
        ("[V] DECEL // VELOCITY -", SLOW_COLOR, 690),
    ]
    # Compact one-line program readout. Fit from left-to-right with smaller sci-fi font.
    # Clean database readout: the effect sign belongs at the end of each
    # data label, so there is no extra symbol crowded behind ONLINE_.
    labels = [
        ("BIOMASS+", PELLET_COLOR, 275),
        ("BIOMASS-", REDUCTION_COLOR, 395),
        ("VELOCITY+", SPEED_COLOR, 515),
        ("VELOCITY-", SLOW_COLOR, 655),
    ]
    # Fixed columns keep the four records evenly separated and prevent
    # one label from visually running into the next.
    for label, color, x in labels:
        surf = small_font.render(label, True, color)
        screen.blit(surf, (x, 567))


def draw_hud():
    font, small_font, large_font = active_fonts()
    time_remaining = get_time_remaining()
    c = theme()

    if visual_mode != "EXPERIMENT":
        title = font.render("OMEGA PELLETS // AQUATIC CONTAINMENT", True, c["text"])
        screen.blit(title, (15, 15))
        timer_text = font.render(f"TIME // {time_remaining:03d}", True, c["text"])
        screen.blit(timer_text, timer_text.get_rect(center=(WIDTH // 2, 80)))
        if game_mode == 1:
            score_text = font.render(f"SCORE // {score_p1:03d}", True, c["text"])
            screen.blit(score_text, score_text.get_rect(topright=(WIDTH - 15, 15)))
        else:
            score_text = font.render(f"P1 {score_p1:03d} // P2 {score_p2:03d}", True, c["text"])
            screen.blit(score_text, score_text.get_rect(topright=(WIDTH - 15, 15)))
        return

    # Scientist workstation terminal.  The HUD is intentionally compact:
    # it is the laboratory computer observing the tank, not decoration inside it.
    bg = (4, 10, 13)
    panel = (7, 16, 20)
    line = (48, 103, 113)
    bright = (139, 220, 230)
    dim = (93, 171, 181)
    neutral = (165, 190, 194)
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "

    pygame.draw.rect(screen, bg, (0, 0, WIDTH, PLAYFIELD_TOP_ROW * CELL_SIZE))

    # Terminal title bar.
    pygame.draw.rect(screen, panel, (7, 5, WIDTH - 14, 25))
    pygame.draw.rect(screen, line, (7, 5, WIDTH - 14, 25), 1)
    title = small_font.render("OMEGA LAB SYSTEM // AQUATIC CONTAINMENT", True, bright)
    screen.blit(title, (14, 8))
    live = small_font.render("LIVE_", True, dim)
    screen.blit(live, live.get_rect(topright=(WIDTH - 14, 8)))

    # Purpose-built data fields beneath the title bar.
    left_box = pygame.Rect(7, 34, 310, 38)
    mid_box = pygame.Rect(323, 34, 225, 38)
    right_box = pygame.Rect(554, 34, 239, 38)
    for box in (left_box, mid_box, right_box):
        pygame.draw.rect(screen, panel, box)
        pygame.draw.rect(screen, line, box, 1)

    specimen_id = "01" if game_mode == 1 else "01 + 02"
    control = "WASD" if game_mode == 1 else "WASD + ARROWS"
    left1 = small_font.render(f"SPECIMEN // {specimen_id}", True, neutral)
    left2 = small_font.render(f"CONTROL // {control}", True, dim)
    screen.blit(left1, (14, 36))
    screen.blit(left2, (14, 53))

    mid1 = small_font.render("SESSION // ACTIVE" + cursor, True, bright)
    mid2 = small_font.render("DATA // ONLINE", True, dim)
    screen.blit(mid1, (330, 36))
    screen.blit(mid2, (330, 53))

    if game_mode == 1:
        score_line = f"SCORE // {score_p1:03d}"
    else:
        score_line = f"P1 {score_p1:03d} // P2 {score_p2:03d}"
    right1 = small_font.render(score_line, True, HEAD_COLOR)
    right2 = small_font.render(f"TIMER // {time_remaining:03d}", True, bright)
    screen.blit(right1, (561, 36))
    screen.blit(right2, (561, 53))

    # One restrained live event-log line.  Recent pellet telemetry temporarily
    # replaces the idle monitoring message, making the HUD feel like software
    # recording the experiment without filling the screen with fake code.
    event_text = "MONITORING SPECIMEN"
    if feedback_messages:
        recent = max(feedback_messages, key=lambda item: item["start_time"])
        age = pygame.time.get_ticks() - recent["start_time"]
        if age < 1200:
            msg = recent["message"]
            event_map = {
                "BIOMASS +": "PELLET CONTACT > BIOMASS INCREASE",
                "BIOMASS -": "PELLET CONTACT > BIOMASS REDUCTION",
                "VELOCITY +": "PELLET CONTACT > VELOCITY INCREASE",
                "VELOCITY -": "PELLET CONTACT > VELOCITY REDUCTION",
            }
            event_text = event_map.get(msg, msg)

    log_box = pygame.Rect(7, 76, WIDTH - 14, 20)
    pygame.draw.rect(screen, panel, log_box)
    pygame.draw.rect(screen, line, log_box, 1)
    log = small_font.render("EVENT LOG // " + event_text + cursor, True, dim)
    screen.blit(log, (14, 77))

    # The lower edge is the computer/tank interface boundary.
    pygame.draw.line(screen, line, (0, 99), (WIDTH, 99), 1)


# ============================================================
# GAME OVER SCREEN
# ============================================================

def draw_game_over():
    font, small_font, large_font = active_fonts()
    c = theme()

    if visual_mode != "EXPERIMENT":
        main = "CONTAINMENT FAILURE" if game_over_reason == "CONTAINMENT" else "SPECIMEN TERMINATED"
        surf = large_font.render(main, True, c["text"])
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 250)))
        result = font.render(get_result_message(), True, c["text"])
        screen.blit(result, result.get_rect(center=(WIDTH // 2, 320)))
        return

    overlay = pygame.Surface((WIDTH, 460), pygame.SRCALPHA)
    overlay.fill((2, 8, 11, 232))
    screen.blit(overlay, (0, 100))
    pygame.draw.line(screen, (71, 155, 166), (25, 125), (775, 125), 1)
    pygame.draw.line(screen, (71, 155, 166), (25, 535), (775, 535), 1)

    elapsed = pygame.time.get_ticks() - (game_over_time or pygame.time.get_ticks())
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
    x = 62
    y = 150

    def log_line(text, yy, color=(129, 204, 214)):
        surf = small_font.render("> " + text, True, color)
        screen.blit(surf, (x, yy))

    # Computer records the event before presenting the final incident record.
    if elapsed < 1400:
        lines = []
        if elapsed >= 100: lines.append("CONTACT EVENT DETECTED")
        if elapsed >= 420:
            lines.append("MULTIPLE SPECIMENS INVOLVED" if game_over_reason == "CONTAINMENT" else "SPECIMEN TELEMETRY // CAPTURED")
        if elapsed >= 740: lines.append("SESSION TIMER // HALTED")
        if elapsed >= 1040: lines.append("INCIDENT RECORD // GENERATING" + cursor)
        for i, line in enumerate(lines):
            log_line(line, y + i * 36)
        return

    if game_over_reason == "CONTAINMENT" and game_mode == 2:
        main = large_font.render("CONTAINMENT FAILURE", True, DEATH_COLOR)
        screen.blit(main, main.get_rect(center=(WIDTH // 2, 170)))
        report = [
            "CONTACT EVENT DETECTED",
            "SPECIMEN 01 // TERMINATED",
            "SPECIMEN 02 // TERMINATED",
            "EXPERIMENT STATUS // FAILED" + cursor,
            "",
            f"SCORE DATA // P1 {score_p1:03d} // P2 {score_p2:03d}",
            f"TIME REMAINING // {get_time_remaining():03d}",
            "RECORD STATUS // CLOSED" + cursor,
        ]
    else:
        cause_map = {
            "HUD_BOUNDARY": "CONTAINMENT BOUNDARY",
            "WALL": "CONTAINMENT WALL",
            "SELF": "SELF COLLISION",
            "TIME": "SESSION COMPLETE",
        }
        main_label = "EXPERIMENT COMPLETE" if game_over_reason == "TIME" else "SPECIMEN TERMINATED"
        main = large_font.render(main_label, True, c["text"] if game_over_reason == "TIME" else DEATH_COLOR)
        screen.blit(main, main.get_rect(center=(WIDTH // 2, 170)))
        specimen_id = loser if loser is not None else 1
        score_value = score_p1 if specimen_id == 1 else score_p2
        report = [
            f"CAUSE // {cause_map.get(game_over_reason, 'UNKNOWN CONDITION')}",
            f"SPECIMEN // {specimen_id:02d}",
            f"SCORE // {score_value:03d}",
            f"TIME REMAINING // {get_time_remaining():03d}",
            "",
            "RECORD STATUS // CLOSED" + cursor,
        ]

    for i, line in enumerate(report):
        if not line:
            continue
        surf = font.render(line, True, (157, 214, 221))
        screen.blit(surf, (90, 220 + i * 34))

    controls = small_font.render("PRESS R TO RESTART" + cursor + "    ESC TO MENU" + cursor, True, (139, 220, 230))
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 510)))


# ============================================================
# PAUSE SCREEN
# ============================================================

def draw_pause():
    font, small_font, large_font = active_fonts()
    c = theme()

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    if visual_mode == "GAMEBOY":
        overlay.fill((155, 188, 15, 105))
    else:
        overlay.fill((0, 6, 9, 205))
    screen.blit(overlay, (0, 0))

    if visual_mode != "EXPERIMENT":
        pause_text = large_font.render("EXPERIMENT PAUSED", True, c["text"])
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35)))
        resume = font.render("PRESS P TO RESUME", True, c["text"])
        screen.blit(resume, resume.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
        return

    elapsed = pygame.time.get_ticks() - (pause_started_time or pygame.time.get_ticks())
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "

    # Brief terminal recording phase after the pause command.
    if elapsed < 750:
        lines = ["PAUSE COMMAND RECEIVED"]
        if elapsed > 220: lines.append("SUSPENDING DATA ACQUISITION")
        if elapsed > 460: lines.append("SESSION TIMER // HOLD" + cursor)
        for i, line in enumerate(lines):
            surf = font.render("> " + line, True, (128, 210, 220))
            screen.blit(surf, (90, 235 + i * 42))
        return

    title = large_font.render("EXPERIMENT PAUSED", True, (150, 225, 233))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 220)))
    lines = [
        "DATA ACQUISITION // SUSPENDED",
        "SESSION TIMER // HOLD",
        "",
        "PRESS P TO RESUME" + cursor,
        "ESC // RETURN TO MENU" + cursor,
    ]
    for i, line in enumerate(lines):
        if not line:
            continue
        surf = font.render(line, True, (139, 210, 219))
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 285 + i * 38)))



def draw_session_shutdown():
    """Fade a paused Modern session to black while Omega Labs closes the record."""
    elapsed = pygame.time.get_ticks() - exit_transition_start
    cyan = (105, 213, 226)
    pale = (194, 232, 236)
    dim = (65, 139, 151)
    cursor = "_" if (pygame.time.get_ticks() // 300) % 2 == 0 else " "

    # The paused tank is still drawn underneath. The shutdown veil steadily
    # closes the observation window until the display is completely black.
    fade_t = min(1.0, elapsed / 1850.0)
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, int(255 * fade_t)))
    screen.blit(veil, (0, 0))

    staged = [
        (0, "> EXIT COMMAND RECEIVED"),
        (280, "> TERMINATING ACTIVE SESSION"),
        (560, "> CLOSING DATA ACQUISITION"),
        (840, "SESSION RECORD // SAVED"),
        (1120, "> DISENGAGING SPECIMEN CONTROL"),
        (1400, "> SECURING CONTAINMENT SYSTEM"),
        (1700, "> RETURNING TO PRIMARY TERMINAL..."),
        (2050, "SESSION // CLOSED"),
        (2250, "CONTAINMENT // SECURED"),
        (2450, "DATA ACQUISITION // OFFLINE"),
        (2650, "RETURNING TO MAIN TERMINAL"),
    ]

    # Once the tank is mostly gone, use a clean black terminal presentation.
    if elapsed >= 1850:
        screen.fill((0, 0, 0))

    header = scifi_small_font.render("OMEGA LAB SYSTEM // SESSION TERMINATION", True, dim)
    screen.blit(header, (72, 92))
    pygame.draw.line(screen, (28, 75, 84), (72, 122), (728, 122), 1)

    visible = [(at, text) for at, text in staged if elapsed >= at]
    y = 160
    for i, (_, text) in enumerate(visible):
        suffix = cursor if i == len(visible) - 1 else ""
        col = cyan if any(k in text for k in ("SAVED", "CLOSED", "SECURED", "OFFLINE")) else pale
        surf = scifi_small_font.render(text + suffix, True, col)
        screen.blit(surf, (92, y))
        y += 34


def draw_menu_fade_in():
    """Brief black-to-menu fade after a controlled Modern session shutdown."""
    if menu_fade_start is None:
        return
    elapsed = pygame.time.get_ticks() - menu_fade_start
    duration = 700
    if elapsed >= duration:
        return
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, int(255 * (1.0 - elapsed / duration))))
    screen.blit(veil, (0, 0))

def draw_resume_notice():
    """Short scientist-terminal acknowledgement while gameplay resumes."""
    if visual_mode != "EXPERIMENT" or pygame.time.get_ticks() >= resume_notice_until:
        return
    font, small_font, large_font = active_fonts()
    panel = pygame.Surface((500, 92), pygame.SRCALPHA)
    panel.fill((2, 10, 14, 220))
    pygame.draw.rect(panel, (67, 145, 156), panel.get_rect(), 1)
    screen.blit(panel, (150, 120))
    lines = ["RESUME COMMAND RECEIVED", "DATA ACQUISITION // ONLINE", "EXPERIMENT // ACTIVE_"]
    for i, line in enumerate(lines):
        surf = small_font.render("> " + line, True, (139, 220, 230))
        screen.blit(surf, (175, 135 + i * 24))


# ============================================================
# CREDITS MODE - v0.7.8
# ============================================================

CREDITS_SCROLL_SPEED = 34.0
CREDITS_FINAL_HOLD_MS = 5000
credits_start_time = None

CREDITS_LINES = [
    ("title", "ΩMEGA PELLETS"),
    ("space", ""),
    ("section", "CREATOR / GAME DEVELOPMENT"),
    ("body", "OmegaKatanaXIII"),
    ("body", "Omega Productions"),
    ("space", ""),
    ("section", "VOICE ACTOR"),
    ("body", "OmegaKatanaXIII"),
    ("body", "Omega Labs System Voice"),
    ("space", ""),
    ("section", "CONCEPT ARTWORK"),
    ("body", "OmegaKatanaXIII"),
    ("space", ""),
    ("section", "MUSIC"),
    ("body", "80s Mysterywave Music"),
    ("body", "DesertDev"),
    ("small", "Main Menu"),
    ("space", ""),
    ("body", "Scanner"),
    ("body", "Karl Casey @ White Bat Audio"),
    ("small", "Single Player Experiment"),
    ("space", ""),
    ("body", "Deadly Force"),
    ("body", "Karl Casey @ White Bat Audio"),
    ("small", "Two Player Experiment"),
    ("space", ""),
    ("body", "assembly_not_required"),
    ("small", "Options / System Configuration"),
    ("small", "Artist credit pending verification"),
    ("space", ""),
    ("body", "Warped"),
    ("body", "Alexander Ehlers"),
    ("small", "Credits"),
    ("space", ""),
    ("body", "Flags"),
    ("body", "Alexander Ehlers"),
    ("small", "Opening Lore Sequence"),
    ("space", ""),
    ("section", "CREATED WITH"),
    ("body", "Python"),
    ("body", "Pygame"),
    ("space", ""),
    ("title", "THANK YOU FOR PLAYING_"),
    ("body", "OMEGA PRODUCTIONS 2026"),
]

def start_credits():
    global screen_state, credits_start_time
    credits_start_time = pygame.time.get_ticks()
    screen_state = "CREDITS"
    update_window_title()
    print("[OMEGA] CREDITS // PRESENTATION STARTED")


def credits_layout_height():
    total = 0
    for kind, _ in CREDITS_LINES:
        total += 48 if kind == "title" else 38 if kind == "section" else 30 if kind == "body" else 24 if kind == "small" else 30
    return total


def draw_credits():
    """Scrolling laboratory credits. Final card holds five seconds, then returns."""
    global screen_state, credits_start_time, menu_fade_start
    now = pygame.time.get_ticks()
    if credits_start_time is None:
        credits_start_time = now
    elapsed = now - credits_start_time

    screen.fill((2, 12, 16))
    cyan = (104, 221, 232)
    pale = (190, 231, 235)
    dim = (76, 164, 176)
    border = (43, 105, 116)
    pygame.draw.rect(screen, border, (10, 10, WIDTH - 20, HEIGHT - 20), 1)
    pygame.draw.line(screen, border, (20, 72), (780, 72), 1)
    head = scifi_small_font.render("OMEGA LABS // PERSONNEL & PRODUCTION ARCHIVE", True, dim)
    screen.blit(head, head.get_rect(center=(WIDTH // 2, 36)))

    total_h = credits_layout_height()
    start_y = HEIGHT + 40
    end_y = 118
    travel = start_y + total_h - end_y
    scroll_ms = int((travel / CREDITS_SCROLL_SPEED) * 1000)

    if elapsed < scroll_ms:
        y = start_y - int(CREDITS_SCROLL_SPEED * (elapsed / 1000.0))
        for kind, text in CREDITS_LINES:
            step = 48 if kind == "title" else 38 if kind == "section" else 30 if kind == "body" else 24 if kind == "small" else 30
            if text and -50 < y < HEIGHT + 30:
                if kind == "title":
                    f, col = _make_scifi_font(34, True), pale
                elif kind == "section":
                    f, col = scifi_font, cyan
                elif kind == "small":
                    f, col = scifi_small_font, dim
                else:
                    f, col = scifi_small_font, pale
                surf = f.render(text, True, col)
                screen.blit(surf, surf.get_rect(center=(WIDTH // 2, int(y))))
            y += step
        esc = scifi_small_font.render("ESC // RETURN TO MAIN TERMINAL", True, dim)
        screen.blit(esc, esc.get_rect(center=(WIDTH // 2, 566)))
    else:
        # Final card is deliberately static for exactly five seconds.
        final_elapsed = elapsed - scroll_ms
        title = _make_scifi_font(48, True).render("ΩMEGA PELLETS", True, pale)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 210)))
        created = scifi_small_font.render("CREATED BY", True, dim)
        screen.blit(created, created.get_rect(center=(WIDTH // 2, 275)))
        creator = scifi_font.render("OmegaKatanaXIII", True, cyan)
        screen.blit(creator, creator.get_rect(center=(WIDTH // 2, 310)))
        prod = scifi_small_font.render("OMEGA PRODUCTIONS 2026", True, pale)
        screen.blit(prod, prod.get_rect(center=(WIDTH // 2, 360)))
        thanks = scifi_font.render("THANK YOU FOR PLAYING_", True, pale)
        screen.blit(thanks, thanks.get_rect(center=(WIDTH // 2, 420)))
        if final_elapsed >= CREDITS_FINAL_HOLD_MS:
            credits_start_time = None
            screen_state = "MENU"
            menu_fade_start = now
            update_window_title()
            print("[OMEGA] CREDITS // COMPLETE // RETURNING TO MENU")

# ============================================================
# MODE SELECTION MENU
# ============================================================

# ============================================================
# MODE SELECTION MENU
# ============================================================

def draw_menu():
    """Animated scientist-terminal main menu with a clean fixed hierarchy."""
    font, small_font, large_font = active_fonts()
    c = theme()

    # Preserve the archived retro menus.
    if visual_mode != "EXPERIMENT":
        screen.fill(c["bg"])
        draw_grid()
        title_text = large_font.render("OMEGA PELLETS", True, c["text"])
        subtitle_text = font.render("EXPERIMENT ZERO", True, c["text"])
        items = ["1 PLAYER", "2 PLAYER", "OPTIONS", "CREDITS"]
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 160)))
        screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, 210)))
        for i, label in enumerate(items):
            prefix = "> " if i == menu_selection else "  "
            surf = font.render(prefix + label, True, c["text"])
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 285 + i * 45)))
        exit_text = small_font.render("UP/DOWN // ENTER     ESC // EXIT", True, c["text"])
        screen.blit(exit_text, exit_text.get_rect(center=(WIDTH // 2, 480)))
        return

    import math
    now = pygame.time.get_ticks()
    screen.fill((3, 17, 22))

    # Restrained animated laboratory background.
    for y in range(0, HEIGHT, 40):
        shade = 13 + ((y // 40) % 2) * 3
        pygame.draw.line(screen, (3, shade + 8, shade + 11), (0, y), (WIDTH, y), 1)
    for i in range(18):
        x = 35 + ((i * 97) % (WIDTH - 70))
        travel = (now // (28 + (i % 5) * 7) + i * 43) % (HEIGHT + 80)
        y = HEIGHT + 30 - travel
        pygame.draw.circle(screen, (16, 63, 72), (x, y), 1 + (i % 3), 1)

    # Large Serpent shadow only: recognizable outline, no interior facial/body detail.
    shadow = pygame.Surface((300, 180), pygame.SRCALPHA)
    swim = int(8 * math.sin(now / 1800.0))
    body = [(20,78),(42,55),(92,48),(145,51),(205,58),(246,67),(270,82),
            (250,95),(205,102),(150,105),(92,102),(45,98),(20,88)]
    body = [(x, y + swim//3) for x,y in body]
    pygame.draw.polygon(shadow, (4, 28, 33, 115), body)
    # Dorsal spikes from the user's large-form drawing.
    for x,h in ((72,20),(98,25),(126,22),(154,27),(183,23),(212,20),(238,17)):
        pygame.draw.polygon(shadow, (4, 28, 33, 115), [(x,55+swim//3),(x+8,55-h+swim//3),(x+16,58+swim//3)])
    # Large upward hooked tail silhouette.
    pygame.draw.lines(shadow, (4, 28, 33, 115), False,
                      [(250,78+swim//3),(276,62+swim//3),(287,35+swim//3),(284,15+swim//3)], 20)
    pygame.draw.arc(shadow, (4, 28, 33, 115), (258,2+swim//3,38,62), 4.4, 7.2, 12)
    # Blunt armored head/jaw profile, still shadow-only.
    pygame.draw.polygon(shadow, (4, 28, 33, 115), [(18,65+swim//3),(3,74+swim//3),(2,94+swim//3),(22,101+swim//3)])
    screen.blit(shadow, (500 + int(7*math.sin(now/2600.0)), 122))

    cyan_dim = (43, 105, 116)
    cyan = (104, 221, 232)
    pale = (190, 231, 235)
    pygame.draw.rect(screen, cyan_dim, (10, 10, WIDTH - 20, HEIGHT - 20), 1)
    pygame.draw.line(screen, cyan_dim, (20, 112), (780, 112), 1)

    packet = (now // 420) % 1000000
    motion = 350 + ((now // 170) % 180)
    pressure = 98 + ((now // 2100) % 3)
    blink = "_" if (now // 500) % 2 == 0 else " "
    left_data = ["AQUATIC CONTAINMENT SYSTEM", "OMEGA LABS // RESEARCH DIVISION", f"DATA PACKET // {packet:06d}{blink}"]
    right_data = ["SPECIMEN BEHAVIOR MONITORING", f"MOTION INDEX // {motion/100:.2f}", f"TANK PRESSURE // {pressure}% // STABLE"]
    for i, text in enumerate(left_data):
        surf = scifi_small_font.render(text, True, (79, 155, 166)); screen.blit(surf, (24, 20 + i * 21))
    for i, text in enumerate(right_data):
        surf = scifi_small_font.render(text, True, (79, 155, 166)); screen.blit(surf, (WIDTH - 24 - surf.get_width(), 20 + i * 21))

    # Unified ΩMEGA logo: Omega is the O, not a separate emblem.
    logo_font = _make_scifi_font(57, False)
    omega_font = _make_scifi_font(70, False)
    omega = omega_font.render("Ω", True, pale)
    mega = logo_font.render("MEGA", True, pale)
    pellets = _make_scifi_font(44, False).render("PELLETS", True, pale)
    logo_w = omega.get_width() + mega.get_width() - 8
    logo_x = WIDTH // 2 - logo_w // 2
    screen.blit(omega, (logo_x, 116))
    screen.blit(mega, (logo_x + omega.get_width() - 8, 126))
    screen.blit(pellets, pellets.get_rect(center=(WIDTH // 2, 205)))

    # Fixed menu zone; all three cards stay clear of navigation/footer strips.
    menu_items = [("1 PLAYER", "SINGLE SPECIMEN SESSION", "01"), ("2 PLAYER", "DUAL SPECIMEN SESSION", "02"), ("OPTIONS", "SYSTEM CONFIGURATION", "03"), ("CREDITS", "PERSONNEL / PRODUCTION ARCHIVE", "04")]
    box_x, box_w, box_h, first_y, gap = 190, 420, 52, 236, 57
    for i, (primary, secondary, code) in enumerate(menu_items):
        y = first_y + i * gap
        selected = i == menu_selection
        border = cyan if selected else (42, 84, 92)
        fill = (3, 25, 30) if selected else (2, 13, 17)
        pygame.draw.rect(screen, fill, (box_x, y, box_w, box_h))
        pygame.draw.rect(screen, border, (box_x, y, box_w, box_h), 2 if selected else 1)
        if selected:
            # Larger geometric selection arrow.
            ax, ay = box_x + 17, y + box_h // 2
            pygame.draw.polygon(screen, cyan, [(ax,ay-8),(ax+12,ay),(ax,ay+8),(ax+3,ay)])
        primary_s = scifi_font.render(primary, True, cyan if selected else pale)
        secondary_s = scifi_small_font.render(secondary, True, (76, 164, 176))
        code_s = scifi_small_font.render("[ " + code + " ]", True, (55, 122, 133))
        screen.blit(primary_s, (box_x + 52, y + 6))
        screen.blit(secondary_s, (box_x + 52, y + 30))
        screen.blit(code_s, (box_x + box_w - code_s.get_width() - 14, y + 30))

    # Dedicated navigation, event-log, and production footer zones.
    nav_y = 474
    pygame.draw.line(screen, (26, 69, 77), (20, nav_y - 8), (780, nav_y - 8), 1)
    controls = scifi_small_font.render("↑↓ // NAVIGATE     ENTER // SELECT     ESC // EXIT", True, (77, 151, 161))
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, nav_y)))

    observations = ["BIOLOGICAL DATA // RECORDING", "SPECIMEN ACTIVITY // MONITORING", "PELLET RESPONSE // STANDBY", "CONTAINMENT INTEGRITY // NOMINAL"]
    obs = observations[(now // 2400) % len(observations)]
    log_box = pygame.Rect(18, 492, WIDTH - 36, 35)
    pygame.draw.rect(screen, (3, 14, 18), log_box)
    pygame.draw.rect(screen, (31, 78, 87), log_box, 1)
    log = scifi_small_font.render("EVENT LOG // " + obs + blink, True, (65, 143, 154))
    screen.blit(log, (28, 500))

    footer = scifi_small_font.render("OMEGA PRODUCTIONS 2026", True, (113, 181, 190))
    screen.blit(footer, footer.get_rect(center=(WIDTH // 2, 556)))


# ============================================================
# OMEGA KATANA INTRO SEQUENCE - v0.7.9
# ============================================================
INTRO_FADE_IN_MS = 1000
INTRO_HOLD_MS = 5000
INTRO_FADE_OUT_MS = 1000
INTRO_TOTAL_MS = INTRO_FADE_IN_MS + INTRO_HOLD_MS + INTRO_FADE_OUT_MS
INTRO_LOGO_PATH = Path(__file__).resolve().parent / "assets" / "images" / "omega_katana_intro.png"

try:
    _intro_logo_raw = pygame.image.load(str(INTRO_LOGO_PATH)).convert_alpha()
    _intro_scale = min((WIDTH - 30) / _intro_logo_raw.get_width(),
                       (HEIGHT - 20) / _intro_logo_raw.get_height())
    _intro_size = (max(1, int(_intro_logo_raw.get_width() * _intro_scale)),
                   max(1, int(_intro_logo_raw.get_height() * _intro_scale)))
    INTRO_LOGO = pygame.transform.smoothscale(_intro_logo_raw, _intro_size)
except Exception as exc:
    INTRO_LOGO = None
    print(f"[OMEGA] INTRO LOGO ERROR // {exc}")

intro_start_time = pygame.time.get_ticks()

def draw_intro():
    """Fade the Omega Katana production card in, hold 5 seconds, then fade out."""
    global screen_state, intro_start_time, menu_fade_start
    now = pygame.time.get_ticks()
    elapsed = now - intro_start_time
    screen.fill((0, 0, 0))

    if elapsed < INTRO_FADE_IN_MS:
        alpha = int(255 * (elapsed / INTRO_FADE_IN_MS))
    elif elapsed < INTRO_FADE_IN_MS + INTRO_HOLD_MS:
        alpha = 255
    elif elapsed < INTRO_TOTAL_MS:
        fade_elapsed = elapsed - INTRO_FADE_IN_MS - INTRO_HOLD_MS
        alpha = int(255 * (1.0 - fade_elapsed / INTRO_FADE_OUT_MS))
    else:
        start_lore()
        print("[OMEGA] INTRO // COMPLETE // LORE ARCHIVE ONLINE")
        return

    if INTRO_LOGO is not None:
        logo = INTRO_LOGO.copy()
        logo.set_alpha(max(0, min(255, alpha)))
        screen.blit(logo, logo.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

# ============================================================
# OMEGA LABS LORE SEQUENCE - v0.8.0
# ============================================================
# A short in-universe briefing: the player is an Omega Labs scientist
# evaluating bioengineered aquatic serpents for the Intergalactic Alliance.
LORE_FADE_MS = 650
LORE_PAGE_MS = 4300
LORE_TOTAL_MS = LORE_PAGE_MS * 5
lore_start_time = None

LORE_PAGES = [
    (
        "INTERGALACTIC ALLIANCE // ENVIRONMENTAL INITIATIVE",
        [
            "Across countless colonies and artificial planets known as Artnets,",
            "pollution and waste contaminate vital water systems.",
        ],
    ),
    (
        "ALLIANCE DEVELOPMENT COMPETITION",
        [
            "The Intergalactic Alliance called upon laboratories across the stars:",
            "develop a new solution for cleaning polluted environments.",
        ],
    ),
    (
        "OMEGA LABS // PROJECT OMEGA",
        [
            "Omega Labs answered with an unusual proposal:",
            "a bioengineered aquatic serpent designed to consume garbage,",
            "pollution, and waste.",
        ],
    ),
    (
        "PROPOSED APPLICATION",
        [
            "If successful, the organisms could unclog sewage systems,",
            "help purify contaminated water, and maintain environments",
            "throughout Artnets and space colonies.",
        ],
    ),
    (
        "PRE-DEPLOYMENT TESTING",
        [
            "Before deployment, every specimen must be tested.",
            "Control. Adaptability. Biological response. Containment safety.",
        ],
    ),
]

def start_lore():
    global screen_state, lore_start_time, _music_state_signature
    lore_start_time = pygame.time.get_ticks()
    screen_state = "LORE"
    _music_state_signature = None
    update_window_title()


def _lore_alpha(page_elapsed):
    if page_elapsed < LORE_FADE_MS:
        return max(0, min(255, int(255 * page_elapsed / LORE_FADE_MS)))
    fade_start = LORE_PAGE_MS - LORE_FADE_MS
    if page_elapsed >= fade_start:
        return max(0, min(255, int(255 * (LORE_PAGE_MS - page_elapsed) / LORE_FADE_MS)))
    return 255


def draw_lore():
    """Cinematic lore briefing between the production logo and main terminal."""
    global screen_state, lore_start_time, menu_fade_start, _current_music_key, _music_state_signature
    now = pygame.time.get_ticks()
    if lore_start_time is None:
        lore_start_time = now
    elapsed = now - lore_start_time

    if elapsed >= LORE_TOTAL_MS:
        # The cinematic score belongs only to the story. Fade it completely
        # before the scientist workstation begins.
        if SOUND_AVAILABLE and MUSIC_ENABLED:
            pygame.mixer.music.fadeout(900)
        _current_music_key = None
        _music_state_signature = None
        lore_start_time = None
        start_lore_outro()
        print("[OMEGA] LORE // COMPLETE // AUDIO CLOSING")
        return

    page_index = min(len(LORE_PAGES) - 1, elapsed // LORE_PAGE_MS)
    page_elapsed = elapsed % LORE_PAGE_MS
    alpha = _lore_alpha(page_elapsed)
    heading, lines = LORE_PAGES[page_index]

    screen.fill((0, 5, 8))
    # Restrained laboratory frame; story text remains the focus.
    frame = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(frame, (42, 104, 114, 105), (18, 18, WIDTH - 36, HEIGHT - 36), 1)
    pygame.draw.line(frame, (42, 104, 114, 85), (36, 78), (WIDTH - 36, 78), 1)
    frame.set_alpha(alpha)
    screen.blit(frame, (0, 0))

    head = scifi_small_font.render(heading, True, (105, 211, 222))
    head.set_alpha(alpha)
    screen.blit(head, head.get_rect(center=(WIDTH // 2, 112)))

    body_font = _make_scifi_font(22, False)
    line_gap = 36
    block_h = max(1, len(lines)) * line_gap
    y = HEIGHT // 2 - block_h // 2 + 25
    for line in lines:
        if line:
            col = (205, 235, 238)
            if line == "EXPERIMENT READY_":
                col = (111, 229, 236)
            surf = body_font.render(line, True, col)
            surf.set_alpha(alpha)
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))
        y += line_gap

    page = scifi_small_font.render(f"OMEGA LABS // BRIEFING {page_index + 1:02d}/{len(LORE_PAGES):02d}", True, (63, 139, 150))
    page.set_alpha(alpha)
    screen.blit(page, page.get_rect(center=(WIDTH // 2, 548)))

# ============================================================
# SCIENTIST ACCESS + OMEGA CONTROL BOOT - v0.8.2
# ============================================================
# Story music is gone before this starts. These screens use only short
# electronic acknowledgements so the menu feels like software being launched.
LORE_OUTRO_MS = 1200
TERMINAL_LINE_MS = 520
TERMINAL_HOLD_MS = 900
BOOT_LINE_MS = 220
BOOT_HOLD_MS = 800

lore_outro_start_time = None
terminal_boot_start_time = None
code_boot_start_time = None
_terminal_last_beep = -1
_code_last_beep = -1
SFX_TERMINAL_BEEP = make_tone(1040, 28, 0.10)
SFX_BOOT_BEEP = make_tone(760, 18, 0.07)

TERMINAL_LINES = [
    "OMEGA LABS // AQUATIC RESEARCH DIVISION",
    "",
    "SCIENTIST ACCESS // GRANTED_",
    "SPECIMEN CONTROL // ONLINE_",
    "DATA ACQUISITION // READY_",
    "",
    "OBJECTIVE:",
    "GUIDE THE SPECIMEN.",
    "ANALYZE ITS RESPONSE.",
    "RECORD THE RESULTS.",
    "",
    "EXPERIMENT READY_",
]

BOOT_LINES = [
    "> INITIALIZING OMEGA CONTROL SYSTEM_",
    "> LOADING AQUATIC CONTAINMENT MODULE...",
    "> SPECIMEN DATABASE // CONNECTED",
    "> BIOMETRIC MONITOR // ONLINE",
    "> BEHAVIORAL ANALYSIS // ONLINE",
    "> ENVIRONMENTAL SIMULATION // READY",
    "> CONTROL INTERFACE // LOADED",
    "> SESSION TERMINAL READY_",
    "",
    "> LAUNCHING OMEGA PELLETS_",
]

def start_lore_outro():
    global screen_state, lore_outro_start_time, _music_state_signature
    lore_outro_start_time = pygame.time.get_ticks()
    screen_state = "LORE_OUTRO"
    _music_state_signature = None


def start_terminal_boot():
    global screen_state, terminal_boot_start_time, _terminal_last_beep, _music_state_signature
    terminal_boot_start_time = pygame.time.get_ticks()
    _terminal_last_beep = -1
    screen_state = "TERMINAL_BOOT"
    _music_state_signature = None
    print("[OMEGA] SCIENTIST TERMINAL // BOOT")


def start_code_boot():
    global screen_state, code_boot_start_time, _code_last_beep, _music_state_signature
    code_boot_start_time = pygame.time.get_ticks()
    _code_last_beep = -1
    screen_state = "CODE_BOOT"
    _music_state_signature = None
    print("[OMEGA] CONTROL SYSTEM // INITIALIZING")


def finish_opening_to_menu():
    global screen_state, menu_fade_start, _music_state_signature
    menu_fade_start = pygame.time.get_ticks()
    screen_state = "MENU"
    _music_state_signature = None
    update_window_title()
    print("[OMEGA] MAIN TERMINAL // ONLINE")


def draw_lore_outro():
    global lore_outro_start_time
    screen.fill((0, 0, 0))
    if lore_outro_start_time is None:
        lore_outro_start_time = pygame.time.get_ticks()
    if pygame.time.get_ticks() - lore_outro_start_time >= LORE_OUTRO_MS:
        lore_outro_start_time = None
        start_terminal_boot()


def _draw_terminal_lines(lines, visible_count, title=None):
    screen.fill((0, 0, 0))
    cyan = (101, 224, 232)
    pale = (201, 239, 241)
    dim = (55, 137, 146)
    pygame.draw.rect(screen, (28, 78, 84), (16, 16, WIDTH - 32, HEIGHT - 32), 1)
    if title:
        t = scifi_small_font.render(title, True, dim)
        screen.blit(t, (30, 27))
        pygame.draw.line(screen, (24, 67, 73), (30, 54), (WIDTH - 30, 54), 1)
    y = 80
    line_font = _make_scifi_font(21, False)
    for i, line in enumerate(lines[:visible_count]):
        if line:
            col = cyan if ("GRANTED" in line or "ONLINE" in line or "READY" in line or "LAUNCHING" in line) else pale
            surf = line_font.render(line, True, col)
            screen.blit(surf, (55, y))
        y += 36


def draw_terminal_boot():
    global terminal_boot_start_time, _terminal_last_beep
    now = pygame.time.get_ticks()
    if terminal_boot_start_time is None:
        terminal_boot_start_time = now
    elapsed = now - terminal_boot_start_time
    visible = min(len(TERMINAL_LINES), 1 + elapsed // TERMINAL_LINE_MS)

    # Beep once when each nonblank workstation line is committed.
    current_index = min(len(TERMINAL_LINES) - 1, int(elapsed // TERMINAL_LINE_MS))
    if current_index != _terminal_last_beep:
        _terminal_last_beep = current_index
        if TERMINAL_LINES[current_index]:
            play_sfx(SFX_TERMINAL_BEEP)

    _draw_terminal_lines(TERMINAL_LINES, visible, "SECURE WORKSTATION // LOCAL ACCESS")
    total = len(TERMINAL_LINES) * TERMINAL_LINE_MS + TERMINAL_HOLD_MS
    if elapsed >= total:
        terminal_boot_start_time = None
        start_code_boot()


def draw_code_boot():
    global code_boot_start_time, _code_last_beep
    now = pygame.time.get_ticks()
    if code_boot_start_time is None:
        code_boot_start_time = now
    elapsed = now - code_boot_start_time
    visible = min(len(BOOT_LINES), 1 + elapsed // BOOT_LINE_MS)
    current_index = min(len(BOOT_LINES) - 1, int(elapsed // BOOT_LINE_MS))
    if current_index != _code_last_beep:
        _code_last_beep = current_index
        if BOOT_LINES[current_index]:
            play_sfx(SFX_BOOT_BEEP)

    _draw_terminal_lines(BOOT_LINES, visible, "OMEGA CONTROL OS // INITIALIZATION")

    # Small changing diagnostics make this read as a real boot rather than lore text.
    packet = (now // 17) % 0xFFFFFF
    diag = scifi_small_font.render(f"MEM // 0x{packet:06X}     BUS // ACTIVE     LINK // LOCAL", True, (45, 118, 127))
    screen.blit(diag, (55, 515))

    total = len(BOOT_LINES) * BOOT_LINE_MS + BOOT_HOLD_MS
    if elapsed >= total:
        code_boot_start_time = None
        finish_opening_to_menu()

# ============================================================
# BEGIN EXPERIMENT
# ============================================================

screen_state = "INTRO"
visual_mode = "EXPERIMENT"
game_mode = None
menu_selection = 0
options_selection = 0
# Initialize session state before the soundtrack system reads it on frame one.
paused = False
pause_started_time = None
game_over = False
resume_notice_until = 0
exit_transition_start = None
menu_fade_start = None
update_window_title()

running = True


# ============================================================
# MAIN GAME LOOP
# ============================================================

while running:
    # Music follows the active terminal/session state. State changes made by
    # input are picked up on the next frame (normally within 16 ms).
    sync_music()
    update_countdown_voice()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # OPENING LORE CONTROLS
            # ------------------------------------------------
            if screen_state == "LORE":
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if SOUND_AVAILABLE and MUSIC_ENABLED:
                        pygame.mixer.music.fadeout(700)
                    _current_music_key = None
                    _music_state_signature = None
                    lore_start_time = None
                    start_lore_outro()

            # ------------------------------------------------
            # MENU CONTROLS
            # ------------------------------------------------
            elif screen_state in ("LORE_OUTRO", "TERMINAL_BOOT", "CODE_BOOT"):
                # ENTER/SPACE advances the boot presentation; ESC jumps to menu.
                if event.key == pygame.K_ESCAPE:
                    finish_opening_to_menu()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    if screen_state == "LORE_OUTRO":
                        start_terminal_boot()
                    elif screen_state == "TERMINAL_BOOT":
                        start_code_boot()
                    else:
                        finish_opening_to_menu()

            elif screen_state == "MENU":

                if event.key in (pygame.K_UP, pygame.K_w):
                    menu_selection = (menu_selection - 1) % 4
                    play_sfx(SFX_MENU_CURSOR)
                    announce_menu_selection(menu_selection)
                    print(f"[OMEGA] SYSTEM INPUT // MENU INDEX {menu_selection + 1:02d}")

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    menu_selection = (menu_selection + 1) % 4
                    play_sfx(SFX_MENU_CURSOR)
                    announce_menu_selection(menu_selection)
                    print(f"[OMEGA] SYSTEM INPUT // MENU INDEX {menu_selection + 1:02d}")

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if menu_selection == 0:
                        reset_game(1)
                    elif menu_selection == 1:
                        reset_game(2)
                    elif menu_selection == 2:
                        screen_state = "OPTIONS"
                    else:
                        start_credits()

                elif event.key == pygame.K_ESCAPE:
                    running = False

            # ------------------------------------------------
            # COUNTDOWN CONTROLS
            # ------------------------------------------------
            elif screen_state == "OPTIONS":
                if event.key in (pygame.K_UP, pygame.K_w):
                    options_selection = (options_selection - 1) % 5
                    print(f"[OMEGA] ARCHIVE INPUT // INDEX {options_selection + 1:02d}")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    options_selection = (options_selection + 1) % 5
                    print(f"[OMEGA] ARCHIVE INPUT // INDEX {options_selection + 1:02d}")
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options_selection == 0:
                        if unlocks["concept_art_unlocked"]:
                            screen_state = "CONCEPT_ART"
                        else:
                            print("[OMEGA] Concept Art locked. Reach score 5.")
                    elif options_selection == 1:
                        if unlocks["prototype_unlocked"]:
                            set_visual_mode("PROTOTYPE")
                        else:
                            print("[OMEGA] Experiment Zero Prototype locked. Reach score 25.")
                    elif options_selection == 2:
                        set_visual_mode("EXPERIMENT")
                    elif options_selection == 3:
                        if unlocks["classic_unlocked"]:
                            set_visual_mode("CLASSIC")
                        else:
                            print("[OMEGA] Classic mode locked. Reach score 50.")
                    elif options_selection == 4:
                        if unlocks["gameboy_unlocked"]:
                            set_visual_mode("GAMEBOY")
                        else:
                            print("[OMEGA] Game Boy mode locked. Reach score 75.")
                elif event.key == pygame.K_ESCAPE:
                    screen_state = "MENU"
                    update_window_title()

            elif screen_state == "CONCEPT_ART":
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    concept_art_index = (concept_art_index - 1) % len(CONCEPT_ART)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    concept_art_index = (concept_art_index + 1) % len(CONCEPT_ART)
                elif event.key == pygame.K_ESCAPE:
                    screen_state = "OPTIONS"

            elif screen_state == "CREDITS":
                if event.key == pygame.K_ESCAPE:
                    credits_start_time = None
                    menu_fade_start = pygame.time.get_ticks()
                    screen_state = "MENU"
                    update_window_title()

            elif screen_state == "COUNTDOWN":

                if event.key == pygame.K_ESCAPE:
                    pygame.time.set_timer(MOVE_EVENT_P1, 0)
                    pygame.time.set_timer(MOVE_EVENT_P2, 0)
                    screen_state = "MENU"
                    update_window_title()

            # ------------------------------------------------
            # PAUSE CONTROLS
            # ------------------------------------------------
            elif screen_state == "PLAYING" and event.key == pygame.K_p:

                if not game_over:
                    if not paused:
                        paused = True
                        pause_started_time = pygame.time.get_ticks()

                        pygame.time.set_timer(MOVE_EVENT_P1, 0)
                        pygame.time.set_timer(MOVE_EVENT_P2, 0)

                        print("[OMEGA] Experiment paused.")

                    else:
                        paused = False

                        pause_duration = (
                            pygame.time.get_ticks()
                            - pause_started_time
                        )

                        # Shift the round start forward so time spent
                        # paused does not reduce the round timer.
                        round_start_time += pause_duration

                        # Shift feedback timestamps too, preventing
                        # floating messages from expiring while paused.
                        for item in feedback_messages:
                            item["start_time"] += pause_duration

                        pygame.time.set_timer(
                            MOVE_EVENT_P1,
                            move_delay_p1
                        )

                        if game_mode == 2:
                            pygame.time.set_timer(
                                MOVE_EVENT_P2,
                                move_delay_p2
                            )

                        pause_started_time = None
                        resume_notice_until = pygame.time.get_ticks() + 900
                        print("[OMEGA] Experiment resumed.")

            # ------------------------------------------------
            # PAUSED MENU CONTROL
            # ------------------------------------------------
            elif screen_state == "PLAYING" and paused:

                if event.key == pygame.K_ESCAPE:
                    pygame.time.set_timer(MOVE_EVENT_P1, 0)
                    pygame.time.set_timer(MOVE_EVENT_P2, 0)

                    # Modern Omega Pellets closes a paused experiment like a
                    # controlled laboratory session. Archived visual modes keep
                    # their original immediate return behavior.
                    if visual_mode == "EXPERIMENT":
                        exit_transition_start = pygame.time.get_ticks()
                        screen_state = "EXITING_TO_MENU"
                        print("[OMEGA] EXIT COMMAND RECEIVED // SESSION TERMINATION")
                    else:
                        paused = False
                        screen_state = "MENU"
                        update_window_title()

            # ------------------------------------------------
            # GAME-OVER CONTROLS
            # ------------------------------------------------
            elif game_over:

                if event.key == pygame.K_r:
                    reset_game(game_mode)

                elif event.key == pygame.K_ESCAPE:
                    pygame.time.set_timer(MOVE_EVENT_P1, 0)
                    pygame.time.set_timer(MOVE_EVENT_P2, 0)
                    screen_state = "MENU"
                    update_window_title()

            # ------------------------------------------------
            # GAMEPLAY CONTROLS
            # ------------------------------------------------
            else:
                if event.key == pygame.K_ESCAPE:
                    pygame.time.set_timer(MOVE_EVENT_P1, 0)
                    pygame.time.set_timer(MOVE_EVENT_P2, 0)
                    screen_state = "MENU"
                    update_window_title()

                # Player 1 - WASD
                elif (
                    event.key == pygame.K_w
                    and direction_p1 != (0, 1)
                ):
                    direction_p1 = (0, -1)

                elif (
                    event.key == pygame.K_s
                    and direction_p1 != (0, -1)
                ):
                    direction_p1 = (0, 1)

                elif (
                    event.key == pygame.K_a
                    and direction_p1 != (1, 0)
                ):
                    direction_p1 = (-1, 0)

                elif (
                    event.key == pygame.K_d
                    and direction_p1 != (-1, 0)
                ):
                    direction_p1 = (1, 0)

                # Player 2 - Arrow keys, multiplayer only
                elif (
                    game_mode == 2
                    and event.key == pygame.K_UP
                    and direction_p2 != (0, 1)
                ):
                    direction_p2 = (0, -1)

                elif (
                    game_mode == 2
                    and event.key == pygame.K_DOWN
                    and direction_p2 != (0, -1)
                ):
                    direction_p2 = (0, 1)

                elif (
                    game_mode == 2
                    and event.key == pygame.K_LEFT
                    and direction_p2 != (1, 0)
                ):
                    direction_p2 = (-1, 0)

                elif (
                    game_mode == 2
                    and event.key == pygame.K_RIGHT
                    and direction_p2 != (-1, 0)
                ):
                    direction_p2 = (1, 0)

        elif (
            screen_state == "PLAYING"
            and event.type == MOVE_EVENT_P1
        ):
            if not game_over and not paused:
                move_snake(1)

        elif (
            screen_state == "PLAYING"
            and game_mode == 2
            and event.type == MOVE_EVENT_P2
        ):
            if not game_over and not paused:
                move_snake(2)

    # --------------------------------------------------------
    # UPDATE / DRAW
    # --------------------------------------------------------

    if screen_state == "INTRO":
        draw_intro()

    elif screen_state == "LORE":
        draw_lore()

    elif screen_state == "LORE_OUTRO":
        draw_lore_outro()

    elif screen_state == "TERMINAL_BOOT":
        draw_terminal_boot()

    elif screen_state == "CODE_BOOT":
        draw_code_boot()

    elif screen_state == "MENU":
        draw_menu()
        draw_menu_fade_in()
        if menu_fade_start is not None and pygame.time.get_ticks() - menu_fade_start >= 700:
            menu_fade_start = None

    elif screen_state == "OPTIONS":
        draw_options()
    elif screen_state == "CONCEPT_ART":
        draw_concept_art()
    elif screen_state == "CREDITS":
        draw_credits()

    elif screen_state == "EXITING_TO_MENU":
        # Keep drawing the exact frozen experiment frame underneath the
        # terminal shutdown so the containment view visibly powers down.
        screen.fill(theme()["bg"])
        draw_grid()
        draw_containment_boundaries()
        draw_pellet()
        draw_reduction_pellet()
        draw_speed_pellet()
        draw_slow_pellet()
        draw_organism(snake_p1, SNAKE_COLOR, HEAD_COLOR)
        if game_mode == 2:
            draw_organism(snake_p2, PLAYER2_COLOR, PLAYER2_HEAD_COLOR)
        draw_pellet_legend()
        draw_hud()
        draw_feedback()
        draw_session_shutdown()

        # Hold the completed black terminal record briefly, then reveal the
        # primary terminal with a short fade-in. No gameplay time advances.
        if pygame.time.get_ticks() - exit_transition_start >= 3150:
            paused = False
            pause_started_time = None
            exit_transition_start = None
            menu_fade_start = pygame.time.get_ticks()
            screen_state = "MENU"
            update_window_title()

    else:
        # Keep the specimens, movement events, and 120-second timer frozen
        # until the selected presentation finishes its startup sequence.
        if screen_state == "COUNTDOWN":
            countdown_elapsed = (
                pygame.time.get_ticks()
                - countdown_start_time
            )

            # Modern Omega Pellets runs a 4-second laboratory boot first,
            # then a 3-2-1-BEGIN test countdown. Prototype mode keeps its
            # original standalone countdown timing.
            startup_duration = 4000 if visual_mode == "PROTOTYPE" else 8000
            if countdown_elapsed >= startup_duration:
                screen_state = "PLAYING"
                round_start_time = pygame.time.get_ticks()

                pygame.time.set_timer(
                    MOVE_EVENT_P1,
                    move_delay_p1
                )

                if game_mode == 2:
                    pygame.time.set_timer(
                        MOVE_EVENT_P2,
                        move_delay_p2
                    )

                if visual_mode == "PROTOTYPE":
                    print("[OMEGA] BEGIN.")
                else:
                    print("[OMEGA] EXPERIMENT // ACTIVE")

        if (
            screen_state == "PLAYING"
            and not game_over
            and not paused
            and get_time_remaining() <= 0
        ):
            end_round("TIME")

        screen.fill(theme()["bg"])

        draw_grid()
        draw_containment_boundaries()
        draw_pellet()
        draw_reduction_pellet()
        draw_speed_pellet()
        draw_slow_pellet()

        draw_organism(
            snake_p1,
            SNAKE_COLOR,
            HEAD_COLOR
        )

        if game_mode == 2:
            draw_organism(
                snake_p2,
                PLAYER2_COLOR,
                PLAYER2_HEAD_COLOR
            )

        draw_pellet_legend()
        draw_hud()
        draw_feedback()
        draw_resume_notice()

        if screen_state == "COUNTDOWN":
            if visual_mode == "PROTOTYPE":
                draw_countdown()
            else:
                # Phase 1: Omega Labs initializes the controlled test.
                # Phase 2: with the tank fully visible, hold every specimen
                # still and run the final 3-2-1-BEGIN laboratory countdown.
                countdown_elapsed = pygame.time.get_ticks() - countdown_start_time
                if countdown_elapsed < 4000:
                    draw_session_initialization()
                else:
                    original_countdown_start = countdown_start_time
                    countdown_start_time = original_countdown_start + 4000
                    draw_countdown()
                    countdown_start_time = original_countdown_start

        if game_over:
            draw_game_over()

        if paused and not game_over:
            draw_pause()

    pygame.display.flip()
    clock.tick(60)


# ============================================================
# SHUTDOWN
# ============================================================

pygame.quit()
sys.exit()
