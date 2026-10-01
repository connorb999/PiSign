#!/bin/bash
# =============================================================================
# install_fonts.sh — Copy BDF fonts from the rpi-rgb-led-matrix library
#
# Run this AFTER cloning rpi-rgb-led-matrix into the parent directory,
# or adjust RPI_LIB_PATH to wherever you cloned it.
# =============================================================================

set -e

RPI_LIB_PATH="${1:-$HOME/rpi-rgb-led-matrix}"
FONT_DST="$(dirname "$0")/assets/fonts"

if [ ! -d "$RPI_LIB_PATH/fonts" ]; then
    echo "ERROR: Could not find fonts at $RPI_LIB_PATH/fonts"
    echo "Usage: $0 /path/to/rpi-rgb-led-matrix"
    exit 1
fi

mkdir -p "$FONT_DST"

FONTS=(
    "5x8.bdf"
    "6x13.bdf"
    "9x18.bdf"
    "9x18B.bdf"
    "10x20.bdf"
)

for f in "${FONTS[@]}"; do
    src="$RPI_LIB_PATH/fonts/$f"
    if [ -f "$src" ]; then
        cp "$src" "$FONT_DST/$f"
        echo "  Copied $f"
    else
        echo "  WARN: $f not found at $src"
    fi
done

echo ""
echo "Fonts installed to $FONT_DST"
