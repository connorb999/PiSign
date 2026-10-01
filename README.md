# Garage LED Panel

Raspberry Pi + HUB75 LED matrix panel showing live clock, weather, and sports scores.

---

## Hardware

| Part | Notes |
|---|---|
| Raspberry Pi 4 or 5 | Pi 5 needs higher `GPIO_SLOWDOWN` (see config) |
| Adafruit RGB Matrix HAT or Bonnet | Bridges Pi GPIO → HUB75 |
| HUB75 LED panel | 64×64 is the default config |
| 5V DC power supply | Size for your panel's max draw (see below) |

### Power Supply Sizing

| Panel size | Max current (all white) |
|---|---|
| 32×32 | ~2A |
| 64×32 | ~4A |
| 64×64 | ~8A |

Connect the fork/spade terminals on your panel's power cable directly to the PSU's +5V and GND terminals. The 4-pin JST connector is a secondary power input — connect it to the same PSU.

---

## Software Setup

### 1. Clone and build rpi-rgb-led-matrix

```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

### 2. Clone this project

```bash
cd ~
git clone <your-repo-url> garage_panel
cd garage_panel
```

### 3. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Install fonts

```bash
chmod +x install_fonts.sh
./install_fonts.sh ~/rpi-rgb-led-matrix
```

### 5. Configure

Edit `config.py`:

```python
PANEL_ROWS   = 64        # your panel height
PANEL_COLS   = 64        # your panel width
LATITUDE     = 39.7294   # your latitude
LONGITUDE    = -104.8319 # your longitude
TIMEZONE     = "America/Denver"
UNIT_SYSTEM  = "imperial"

TRACKED_TEAMS = [
    {"name": "Broncos",   "abbr": "DEN", "sport": "football",   "league": "nfl"},
    {"name": "Nuggets",   "abbr": "DEN", "sport": "basketball", "league": "nba"},
    # Add/remove teams here
]
```

### 6. Disable onboard audio (required)

```bash
sudo nano /boot/config.txt
# Change: dtparam=audio=on
# To:     dtparam=audio=off
sudo reboot
```

### 7. Run

```bash
sudo python3 main.py
```

---

## Raspberry Pi 5 Notes

The Pi 5 uses a different GPIO chip. Add these flags if you see flickering:

```python
# In config.py:
GPIO_SLOWDOWN = 4
```

Or when running manually:
```bash
sudo python3 main.py --led-slowdown-gpio=4
```

---

## Auto-start on Boot

```bash
# Edit the service file WorkingDirectory and ExecStart paths if needed
sudo cp garage-panel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable garage-panel
sudo systemctl start garage-panel

# Check status
sudo systemctl status garage-panel

# View live logs
sudo journalctl -u garage-panel -f
```

---

## Display Layout

**No games today:**
```
┌────────────────────────────────┐
│  12:45 PM  Thu Jan 16          │
│  72°F  ☀ Sunny  Feels 69°     │
│────────────────────────────────│
│  Today  Fri  Sat  Sun  Mon     │
│  85°    79°  72°  68°  74°    │
│  62°    55°  50°  48°  52°    │
└────────────────────────────────┘
```

**Games active:**
```
┌────────────────────────────────┐
│  12:45 PM  72°  ☀ Sunny       │  ← compressed strip
│────────────────────────────────│
│  KC 14-7 LV   Q3 8:42         │  ← live game
│────────────────────────────────│
│  COL vs NYY   7:10PM T-2h15m  │  ← upcoming
│────────────────────────────────│
│  DEN 3-1 CHI  Final            │  ← finished
└────────────────────────────────┘
```

---

## Adding More Teams

Just append to `TRACKED_TEAMS` in `config.py`:

```python
{"name": "Chiefs", "abbr": "KC", "sport": "football", "league": "nfl"},
```

Valid sport/league pairs:
- `"football"` / `"nfl"`
- `"basketball"` / `"nba"`
- `"baseball"` / `"mlb"`
- `"hockey"` / `"nhl"`

---

## Adding Team Colors

Edit `utils/colors.py` and add an entry to `TEAM_COLORS`:

```python
"PHX": ((29, 17, 96), (229, 95, 32)),   # Suns: purple, orange
```

---

## Project Structure

```
garage_panel/
├── main.py                  # Main loop
├── config.py                # All settings
├── display/
│   └── panel.py             # Matrix init
├── scenes/
│   ├── base_scene.py        # Abstract base
│   ├── clock_weather.py     # Always-on display
│   └── sports.py            # Conditional sports
├── data/
│   ├── weather.py           # Open-Meteo fetcher
│   └── sports.py            # ESPN API fetcher
├── utils/
│   ├── colors.py            # Color constants + team colors
│   └── fonts.py             # Font loader/cache
└── assets/fonts/            # BDF fonts (copied by install_fonts.sh)
```
