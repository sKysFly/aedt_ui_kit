"""Tests of the shared UI kit: decimal separators, in-place theme switch, minimum contrasts.

Skipped when Qt cannot be imported (e.g. a CI image without libGL).
"""

from __future__ import annotations

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from PyQt6 import QtWidgets  # noqa: E402
    import ui_kit as ui  # noqa: E402
    QT_OK = True
except ImportError:
    QT_OK = False


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


@unittest.skipUnless(QT_OK, "PyQt6 indisponible")
class TestUiKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def tearDown(self):
        ui.set_theme("dark")

    def test_decimal_separators(self):
        sp = ui.DecimalSpinBox()
        sp.setRange(0.0, 2000.0)
        sp.setDecimals(2)
        sp.setSuffix(" ns")
        for text, value in (("3,2", 3.2), ("3.2", 3.2), ("12,25 ns", 12.25), ("0,5", 0.5)):
            sp.lineEdit().setText(text)
            sp.interpretText()
            self.assertAlmostEqual(sp.value(), value, places=6, msg=text)
        sp.setValue(1234.5)
        self.assertNotIn(",", sp.text())
        self.assertIn(".", sp.text())

    def test_theme_switch_in_place(self):
        tokens = ui.TOKENS
        self.assertEqual(set(ui.DARK), set(ui.LIGHT))
        ui.set_theme("light")
        self.assertIs(ui.TOKENS, tokens)
        self.assertEqual(tokens["bg"], ui.LIGHT["bg"])
        self.assertEqual(ui.current_theme(), "light")
        ui.set_theme("dark")
        self.assertEqual(tokens["bg"], ui.DARK["bg"])
        with self.assertRaises(ValueError):
            ui.set_theme("sepia")

    def test_stylesheet_has_no_unfilled_field(self):
        for name in ui.THEMES:
            ui.set_theme(name)
            qss = ui.stylesheet()
            self.assertNotIn("{bg}", qss)
            self.assertIn(ui.TOKENS["bg"], qss)
            self.assertIn(ui.TOKENS["hover"], qss)

    def test_minimum_contrast(self):
        for name, pal in ui.THEMES.items():
            for fg in ("fg", "dim", "pass", "warn", "fail", "accent"):
                self.assertGreaterEqual(contrast(pal[fg], pal["bg"]), 4.5, f"{name}:{fg} sur bg")
            for ch in ui.CHANNELS:
                self.assertGreaterEqual(contrast(pal[ch], pal["bg"]), 3.0, f"{name}:{ch} sur bg")
            self.assertGreaterEqual(contrast(pal["on_accent"], pal["accent"]), 4.5, f"{name}: texte sur accent")


if __name__ == "__main__":
    unittest.main()
