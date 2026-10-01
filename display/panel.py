# =============================================================================
# display/panel.py — RGBMatrix initialization wrapper
# =============================================================================

from rgbmatrix import RGBMatrix, RGBMatrixOptions
import config


def create_matrix() -> RGBMatrix:
    """Build and return a configured RGBMatrix instance."""
    options = RGBMatrixOptions()

    options.rows                 = config.PANEL_ROWS
    options.cols                 = config.PANEL_COLS
    options.chain_length         = config.PANEL_CHAIN
    options.parallel             = config.PANEL_PARALLEL
    options.hardware_mapping     = config.GPIO_MAPPING
    options.gpio_slowdown        = config.GPIO_SLOWDOWN
    options.pwm_bits             = config.PWM_BITS
    options.brightness           = config.BRIGHTNESS

    # Disable PWM dithering for smoother refresh (optional, experiment)
    options.pwm_lsb_nanoseconds  = 130

    # Drop privileges after setting up GPIO
    options.drop_privileges      = True

    return RGBMatrix(options=options)
