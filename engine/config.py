"""
BioSim v2.0 - Configuration & Layout Constants
Defines CAD interface dimensions, color palette, and default settings.
"""

# Window Dimensions
WIDTH = 1280
HEIGHT = 720
TITLE = "BioSim v2.0 - CAD & Soft Robotics Workspace"
FPS = 60

# Layout Dimensions
TOP_MENU_HEIGHT = 28
TOOLBAR_WIDTH = 50
PROPERTIES_WIDTH = 280
STATUS_BAR_HEIGHT = 26

VIEWPORT_X = TOOLBAR_WIDTH
VIEWPORT_Y = TOP_MENU_HEIGHT
VIEWPORT_WIDTH = WIDTH - TOOLBAR_WIDTH - PROPERTIES_WIDTH
VIEWPORT_HEIGHT = HEIGHT - TOP_MENU_HEIGHT - STATUS_BAR_HEIGHT

GRID_SIZE = 40

# Color Palette (Dark Theme Professional CAD UI)
COLOR_TOP_BAR = (28, 30, 35)
COLOR_SIDEBAR = (33, 37, 43)
COLOR_PANEL = (38, 42, 50)
COLOR_STATUS_BAR = (24, 26, 30)
COLOR_VIEWPORT_BG = (18, 20, 24)
COLOR_GRID = (32, 36, 44)
COLOR_AXIS_X = (220, 70, 70)
COLOR_AXIS_Y = (70, 180, 70)

COLOR_TEXT = (220, 225, 230)
COLOR_TEXT_DIM = (140, 145, 155)
COLOR_ACCENT = (0, 122, 204)
COLOR_ACCENT_HOVER = (28, 151, 234)
COLOR_SELECTION = (255, 190, 40)
COLOR_BORDER = (55, 60, 70)

# Material Library Presets (Stiffness, Density, Damping, Color)
MATERIALS = {
    "Silicone": {
        "stiffness": 0.35,
        "density": 1050.0,
        "damping": 0.98,
        "color": (120, 200, 255)
    },
    "Rubber": {
        "stiffness": 0.70,
        "density": 1200.0,
        "damping": 0.95,
        "color": (230, 120, 80)
    },
    "TPU": {
        "stiffness": 0.92,
        "density": 1150.0,
        "damping": 0.92,
        "color": (180, 220, 100)
    },
    "Custom": {
        "stiffness": 0.50,
        "density": 1000.0,
        "damping": 0.97,
        "color": (200, 100, 220)
    }
}


