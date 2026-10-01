# =============================================================================
# utils/colors.py — Color constants and team color lookup
# =============================================================================

# Basic colors (R, G, B)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (220, 30,  30)
GREEN      = (30,  200, 30)
BLUE       = (30,  80,  220)
YELLOW     = (220, 200, 0)
ORANGE     = (220, 120, 0)
CYAN       = (0,   200, 220)
MAGENTA    = (180, 0,   180)
GRAY       = (120, 120, 120)
DARK_GRAY  = (50,  50,  50)
DIM_WHITE  = (180, 180, 180)

# Weather condition colors
WEATHER_COLORS = {
    "sunny":       (220, 180, 0),
    "clear":       (220, 180, 0),
    "cloudy":      (140, 140, 160),
    "rain":        (60,  120, 200),
    "snow":        (200, 220, 255),
    "storm":       (160, 80,  200),
    "fog":         (160, 160, 160),
    "default":     (180, 180, 180),
}

# Team colors: keyed by abbreviation, (primary, secondary)
TEAM_COLORS = {
    # NFL
    "DEN": ((251, 79,  20),  (0,   34,  68)),   # Broncos: orange, navy
    "KC":  ((227, 24,  55),  (255, 184, 28)),    # Chiefs: red, gold
    "LV":  ((165, 172, 175), (0,   0,   0)),     # Raiders: silver, black
    "LAC": ((0,   128, 198), (255, 194, 14)),    # Chargers: blue, gold
    "DAL": ((0,   53,  148), (255, 255, 255)),   # Cowboys: blue, white
    "GB":  ((24,  48,  40),  (255, 184, 28)),    # Packers: green, gold
    "NE":  ((0,   34,  68),  (198, 12,  48)),    # Patriots: navy, red
    "SF":  ((170, 0,   0),   (173, 153, 93)),    # 49ers: red, gold
    "SEA": ((0,   34,  68),  (105, 190, 40)),    # Seahawks: navy, green

    # NBA
    "GSW": ((29,  66,  138), (255, 199, 44)),    # Warriors: blue, gold
    "LAL": ((85,  37,  130), (253, 185, 39)),    # Lakers: purple, gold
    "BOS": ((0,   122, 51),  (139, 111, 78)),    # Celtics: green, gold
    "MIA": ((152, 0,   46),  (249, 160, 27)),    # Heat: red, gold
    "CHI": ((206, 17,  65),  (6,   25,  34)),    # Bulls: red, black

    # MLB
    "COL": ((51,  0,   111), (196, 206, 211)),   # Rockies: purple, silver
    "NYY": ((12,  35,  64),  (255, 255, 255)),   # Yankees: navy, white
    "BOS": ((189, 48,  57),  (12,  35,  64)),    # Red Sox: red, navy
    "LAD": ((0,   90,  156), (239, 179, 0)),     # Dodgers: blue, gold
    "CHC": ((14,  51,  134), (204, 52,  51)),    # Cubs: blue, red
    "HOU": ((0,   45,  98),  (235, 110, 31)),    # Astros: navy, orange
    "ATL": ((19,  39,  79),  (206, 17,  65)),    # Braves: navy, red

    # NHL
    "COL": ((111, 38,  61),  (35,  97,  146)),   # Avalanche: burgundy, blue
    "VGK": ((180, 151, 90),  (51,  63,  72)),    # Golden Knights: gold, gray
    "TBL": ((0,   40,  104), (255, 255, 255)),   # Lightning: blue, white
    "BOS": ((252, 181, 20),  (17,  17,  17)),    # Bruins: gold, black
    "PIT": ((252, 181, 20),  (0,   0,   0)),     # Penguins: gold, black

    # Default fallback
    "DEFAULT": (GRAY, DIM_WHITE),
}


def get_team_colors(abbr: str):
    """Return (primary_color, secondary_color) for a team abbreviation."""
    return TEAM_COLORS.get(abbr.upper(), TEAM_COLORS["DEFAULT"])


def dim(color: tuple, factor: float = 0.5) -> tuple:
    """Dim a color by a factor (0.0–1.0)."""
    return tuple(int(c * factor) for c in color)


def blend(color_a: tuple, color_b: tuple, t: float = 0.5) -> tuple:
    """Linear blend between two colors. t=0 → a, t=1 → b."""
    return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))
