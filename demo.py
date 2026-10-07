"""Fenêtre de démonstration : widgets du kit, rôles de couleur, thèmes Jour et Nuit.

python demo.py                    ouvre la fenêtre (Jour / Nuit en haut à droite)
python demo.py light out.png      enregistre une capture du thème choisi (dark ou light) et quitte
                                  (hors écran : QT_QPA_PLATFORM=offscreen)
"""

import sys

from PyQt6 import QtCore, QtWidgets

import ui_kit as ui


def build(on_theme) -> QtWidgets.QWidget:
    root = QtWidgets.QWidget()
    root.setWindowTitle("aedt_ui_kit")
    lay = QtWidgets.QVBoxLayout(root)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)

    bar = QtWidgets.QFrame()
    bar.setObjectName("TopBar")
    h = QtWidgets.QHBoxLayout(bar)
    h.setContentsMargins(12, 8, 12, 8)
    h.setSpacing(8)
    h.addWidget(QtWidgets.QPushButton("Ouvrir…"))
    h.addWidget(ui.vsep())
    seg = ui.Segmented([("a", "Sdd11", ""), ("b", "Scc11", ""), ("c", "Sdd21", "")])
    seg.set_key("a")
    h.addWidget(seg)
    h.addWidget(ui.vsep())
    h.addWidget(ui.caption("tr", upper=False))
    sp = ui.DecimalSpinBox()  # accepte "." et ","
    sp.setSuffix(" ps")
    sp.setValue(25.0)
    sp.setFixedWidth(92)
    h.addWidget(sp)
    h.addStretch(1)
    theme = ui.Segmented([("light", "Jour", "Thème clair"), ("dark", "Nuit", "Thème sombre")])
    theme.set_key(ui.current_theme())
    theme.changed.connect(on_theme)
    h.addWidget(theme)
    primary = QtWidgets.QPushButton("Calculer")
    primary.setProperty("primary", True)
    h.addWidget(primary)
    lay.addWidget(bar)

    kpis = ui.KpiStrip(["Verdict", "Z min", "Z max", "Z moyen"])
    kpis.tiles[0].set("FAIL", "gabarit 90–110 Ω", tone="fail", display=True)
    kpis.tiles[1].set("88.7 Ω", "-11.3 % @ 793.8 ps", tone="fail")
    kpis.tiles[2].set("103.2 Ω", "+3.2 % @ 739.3 ps")
    kpis.tiles[3].set("93.5 Ω", "dans la fenêtre")
    lay.addWidget(kpis)

    body = QtWidgets.QWidget()
    g = QtWidgets.QGridLayout(body)
    g.setContentsMargins(16, 16, 16, 16)
    g.setHorizontalSpacing(16)
    g.setVerticalSpacing(10)
    g.addWidget(ui.caption("Statuts"), 0, 0)
    row = QtWidgets.QHBoxLayout()
    row.setSpacing(8)
    for v in ("PASS", "MARGINAL", "FAIL", "N/A"):
        row.addWidget(ui.Pill(v))
    row.addStretch(1)
    g.addLayout(row, 1, 0)
    g.addWidget(ui.caption("Canaux de données"), 2, 0)
    row = QtWidgets.QHBoxLayout()
    for tok in ui.CHANNELS:
        sw = QtWidgets.QFrame()
        sw.setFixedSize(46, 4)
        sw.setStyleSheet(f"background:{ui.TOKENS[tok]};")
        lbl = QtWidgets.QLabel(tok.upper())
        lbl.setProperty("role", "hint")
        row.addWidget(sw)
        row.addWidget(lbl)
        row.addSpacing(10)
    row.addStretch(1)
    g.addLayout(row, 3, 0)
    g.addWidget(ui.caption("Champs"), 4, 0)
    le = QtWidgets.QLineEdit()
    le.setPlaceholderText("Filtrer : TX0, RX, 13…")
    g.addWidget(le, 5, 0)
    cb = QtWidgets.QComboBox()
    cb.addItems(["100 Ω ±10 %", "85 Ω ±10 %", "90 Ω ±10 %"])
    g.addWidget(cb, 6, 0)
    g.setRowStretch(7, 1)
    lay.addWidget(body, 1)
    return root


class Demo:
    """Rebuilds the window on a theme change: the swatches bake tokens into inline styles."""

    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        self.win = build(self.set_theme)

    def set_theme(self, name: str) -> None:
        old = self.win
        ui.apply(self.app, theme=name)
        self.win = build(self.set_theme)
        self.win.setGeometry(old.geometry())
        self.win.show()
        old.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    args = sys.argv[1:]
    ui.apply(app, theme=args.pop(0) if args and args[0] in ui.THEMES else "dark")
    demo = Demo(app)
    demo.win.resize(900, 460)
    demo.win.show()
    if args:
        for _ in range(3):
            app.processEvents()
            QtCore.QThread.msleep(100)
        demo.win.grab().save(args[0])
        sys.exit(0)
    sys.exit(app.exec())
