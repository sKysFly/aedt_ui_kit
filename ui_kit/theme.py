"""
Shared visual identity for the AEDT toolkits (aedt_tdr, aedt_eye, aedt_port_checker).

Colour roles are kept separate:
- interaction: `accent` only (buttons, selection, focus)
- data: `ch1`..`ch4`, oscilloscope channel colours (CH1 yellow, CH2 cyan, CH3 magenta, CH4 green)
- status: `pass`, `warn`, `fail`
Neutrals are slightly blue-biased greys. Numbers use IBM Plex Mono with tabular figures.

Two palettes, `dark` (night) and `light` (day). `TOKENS` is mutated in place by `set_theme()`, so code that
reads `ui.TOKENS[...]` at paint time follows the active theme; widgets that bake colours into a stylesheet
must be refreshed after a switch (see `Pill.refresh`, `KpiTile.refresh`).
"""

from __future__ import annotations

import os

from PyQt6 import QtGui, QtWidgets

DARK = {
    "bg": "#0F1216",
    "s1": "#161A20",
    "s2": "#1D222A",
    "line": "#2A313B",
    "fg": "#E6E9EE",
    "dim": "#8B95A3",
    "accent": "#5B8DEF",
    "accent_hover": "#76A0F2",
    "on_accent": "#0B0E12",
    "ch1": "#F2C94C",
    "ch2": "#3FC1D9",
    "ch3": "#D67AD8",
    "ch4": "#6FCF7F",
    "pass": "#3FB950",
    "warn": "#D29922",
    "fail": "#F85149",
    "cursor": "#C9D1D9",
    "hover": "rgba(255, 255, 255, 0.04)",
    "sel": "rgba(91, 141, 239, 0.18)",
}

# Light data colours are darkened so that traces keep a contrast of at least 3:1 on the light background.
LIGHT = {
    "bg": "#F4F6F9",
    "s1": "#FFFFFF",
    "s2": "#E9EDF2",
    "line": "#D3D9E1",
    "fg": "#161A20",
    "dim": "#566170",
    "accent": "#2F63C8",
    "accent_hover": "#2556B0",
    "on_accent": "#FFFFFF",
    "ch1": "#B07F00",
    "ch2": "#0B8CA6",
    "ch3": "#A33FA6",
    "ch4": "#2A8A3C",
    "pass": "#1A7F37",
    "warn": "#9A6200",
    "fail": "#C4312B",
    "cursor": "#3B4350",
    "hover": "rgba(0, 0, 0, 0.04)",
    "sel": "rgba(47, 99, 200, 0.14)",
}

THEMES = {"dark": DARK, "light": LIGHT}
TOKENS = dict(DARK)
_state = {"theme": "dark", "fonts": False}

CHANNELS = ("ch1", "ch2", "ch3", "ch4")

SANS = "IBM Plex Sans"
MONO = "IBM Plex Mono"
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def current_theme() -> str:
    return _state["theme"]


def set_theme(name: str) -> None:
    """Switch the active palette in place. Call `apply(app)` afterwards to restyle the application."""
    if name not in THEMES:
        raise ValueError(f"thème inconnu : {name!r} (attendu : {', '.join(THEMES)})")
    _state["theme"] = name
    TOKENS.clear()
    TOKENS.update(THEMES[name])


def color(name: str, alpha: int = 255) -> QtGui.QColor:
    c = QtGui.QColor(TOKENS[name])
    c.setAlpha(alpha)
    return c


def status_token(verdict: str) -> str:
    return {"PASS": "pass", "MARGINAL": "warn", "FAIL": "fail"}.get(verdict, "dim")


def load_fonts() -> None:
    """Register the bundled Plex faces; Qt falls back to the system sans/mono if they are missing."""
    if _state["fonts"] or not os.path.isdir(_FONT_DIR):
        return
    _state["fonts"] = True
    for fname in sorted(os.listdir(_FONT_DIR)):
        if fname.lower().endswith(".ttf"):
            QtGui.QFontDatabase.addApplicationFont(os.path.join(_FONT_DIR, fname))


def mono_font(point_size: float = 9.5, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Normal) -> QtGui.QFont:
    f = QtGui.QFont(MONO)
    f.setStyleHint(QtGui.QFont.StyleHint.Monospace)
    f.setPointSizeF(point_size)
    f.setWeight(weight)
    return f


QSS = """
QWidget {{
    background: {bg}; color: {fg};
    font-family: "{sans}", "Segoe UI", "DejaVu Sans", sans-serif; font-size: 12.5px;
}}
QToolTip {{ background: {s2}; color: {fg}; border: 1px solid {line}; padding: 4px 6px; }}
QFrame#Panel, QWidget#Panel {{ background: {s1}; }}
QFrame#TopBar {{ background: {s1}; border-bottom: 1px solid {line}; }}
QFrame#SidePanel {{ background: {s1}; border-right: 1px solid {line}; }}
QFrame#KpiStrip {{ background: {bg}; border-bottom: 1px solid {line}; }}
QFrame#VSep {{ background: {line}; max-width: 1px; min-width: 1px; }}
QLabel {{ background: transparent; }}
QLabel[role="caption"] {{
    color: {dim}; font-family: "{mono}"; font-size: 10.5px; font-weight: 500; letter-spacing: 0.6px;
}}
QLabel[role="hint"] {{ color: {dim}; font-family: "{mono}"; font-size: 11px; }}
QLabel[role="hint"][alert="true"] {{ color: {warn}; }}
QLabel[role="conv"] {{
    color: {dim}; background: {bg}; border: 1px dashed {line}; border-radius: 4px; padding: 6px 8px; font-size: 11.5px;
}}

QPushButton, QToolButton {{
    background: {s2}; color: {fg}; border: 1px solid {line}; border-radius: 4px; padding: 5px 10px;
}}
QPushButton:hover, QToolButton:hover {{ border-color: {dim}; }}
QPushButton:pressed, QToolButton:pressed {{ background: {bg}; }}
QPushButton:disabled, QToolButton:disabled {{ color: {dim}; }}
QPushButton[primary="true"] {{ background: {accent}; border-color: {accent}; color: {on_accent}; font-weight: 600; }}
QPushButton[primary="true"]:hover {{ background: {accent_hover}; }}
QToolButton::menu-indicator {{ image: none; width: 0; }}

QToolButton[seg="true"] {{
    font-family: "{mono}"; color: {dim}; border-radius: 0; border-right-width: 0; padding: 5px 8px;
}}
QToolButton[seg="true"][first="true"] {{ border-top-left-radius: 4px; border-bottom-left-radius: 4px; }}
QToolButton[seg="true"][last="true"] {{
    border-top-right-radius: 4px; border-bottom-right-radius: 4px; border-right-width: 1px;
}}
QToolButton[seg="true"]:checked {{ background: {accent}; border-color: {accent}; color: {on_accent}; font-weight: 500; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {bg}; color: {fg}; border: 1px solid {line}; border-radius: 4px; padding: 3px 6px;
    selection-background-color: {accent}; selection-color: {on_accent};
}}
QSpinBox, QDoubleSpinBox {{ font-family: "{mono}"; }}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{ border-color: {accent}; }}
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 0; }}
QComboBox::drop-down {{ border: none; width: 16px; }}
QComboBox QAbstractItemView {{ background: {s2}; border: 1px solid {line}; selection-background-color: {accent}; }}
QCheckBox {{ spacing: 6px; background: transparent; }}
QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid {dim}; border-radius: 3px; background: {bg}; }}
QCheckBox::indicator:checked {{ background: {accent}; border-color: {accent}; }}

QMenu {{ background: {s2}; border: 1px solid {line}; padding: 4px; }}
QMenu::item {{ padding: 5px 18px 5px 10px; border-radius: 3px; }}
QMenu::item:selected {{ background: {accent}; color: {on_accent}; }}
QMenu::separator {{ height: 1px; background: {line}; margin: 4px 6px; }}

QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ border: 1px solid transparent; border-radius: 4px; }}
QListWidget::item:selected {{ background: {s2}; border-color: {line}; }}
QListWidget::item:hover:!selected {{ background: {hover}; }}

QTableWidget {{
    background: {bg}; border: none; gridline-color: {line}; font-family: "{mono}"; font-size: 12px;
    selection-background-color: {sel}; selection-color: {fg};
}}
QHeaderView::section {{
    background: {s1}; color: {dim}; border: none; border-bottom: 1px solid {line}; padding: 6px 10px;
    font-family: "{mono}"; font-size: 10.5px; font-weight: 500; text-align: left;
}}
QTableCornerButton::section {{ background: {s1}; border: none; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 9px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {line}; min-height: 24px; border-radius: 4px; }}
QScrollBar::handle:vertical:hover {{ background: {dim}; }}
QScrollBar:horizontal {{ background: transparent; height: 9px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {line}; min-width: 24px; border-radius: 4px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QStatusBar {{ background: {s1}; border-top: 1px solid {line}; color: {dim}; font-family: "{mono}"; font-size: 11px; }}
QStatusBar::item {{ border: none; }}
QStatusBar QLabel {{ color: {dim}; padding: 0 8px; }}
QSplitter::handle {{ background: {line}; }}
QDialog {{ background: {bg}; }}
"""


def stylesheet() -> str:
    return QSS.format(sans=SANS, mono=MONO, **TOKENS)


def apply(app: QtWidgets.QApplication, theme: str = None) -> None:
    """Load fonts, set the application stylesheet and the pyqtgraph defaults (optionally switching theme first)."""
    if theme is not None:
        set_theme(theme)
    load_fonts()
    f = QtGui.QFont(SANS)
    f.setPointSizeF(9.5)
    app.setFont(f)
    app.setStyleSheet(stylesheet())
    try:
        import pyqtgraph as pg

        pg.setConfigOptions(background=TOKENS["bg"], foreground=TOKENS["dim"], antialias=True)
    except ImportError:
        pass
