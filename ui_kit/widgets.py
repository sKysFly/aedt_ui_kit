"""Reusable widgets of the AEDT toolkit visual identity."""

from __future__ import annotations

from typing import List, Optional

from PyQt6 import QtCore, QtWidgets

from .theme import TOKENS, status_token


def caption(text: str, upper: bool = True) -> QtWidgets.QLabel:
    """Small monospace label used for field and section names (keep `upper=False` for symbols like εr, t_r)."""
    lbl = QtWidgets.QLabel(upper_latin(text) if upper else text)
    lbl.setProperty("role", "caption")
    return lbl


def upper_latin(text: str) -> str:
    """Uppercase without touching Greek symbols (εr, τ, Δ keep their meaning)."""
    return "".join(c if "\u0370" <= c <= "\u03ff" else c.upper() for c in text)


def vsep() -> QtWidgets.QFrame:
    sep = QtWidgets.QFrame()
    sep.setObjectName("VSep")
    sep.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    return sep


def restyle(w: QtWidgets.QWidget) -> None:
    """Re-apply the stylesheet after a dynamic property change."""
    w.style().unpolish(w)
    w.style().polish(w)


class Segmented(QtWidgets.QWidget):
    """Exclusive segmented control. Emits `changed(key)`."""

    changed = QtCore.pyqtSignal(str)

    def __init__(self, items: List[tuple], parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._group = QtWidgets.QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons = {}
        for i, (key, label, tip) in enumerate(items):
            b = QtWidgets.QToolButton()
            b.setText(label)
            b.setToolTip(tip)
            b.setCheckable(True)
            b.setProperty("seg", True)
            b.setProperty("first", i == 0)
            b.setProperty("last", i == len(items) - 1)
            b.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            # fixed width: a narrow bar must never elide the labels to "..."
            b.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
            self._group.addButton(b)
            self._buttons[key] = b
            lay.addWidget(b)
            b.toggled.connect(lambda on, k=key: on and self.changed.emit(k))

    def key(self) -> str:
        for k, b in self._buttons.items():
            if b.isChecked():
                return k
        return ""

    def set_enabled(self, key: str, enabled: bool) -> None:
        self._buttons[key].setEnabled(enabled)

    def set_key(self, key: str, emit: bool = False) -> None:
        b = self._buttons.get(key)
        if b is None:
            return
        b.blockSignals(not emit)
        b.setChecked(True)
        b.blockSignals(False)


class Pill(QtWidgets.QLabel):
    """Status chip: PASS / MARGINAL / FAIL / neutral."""

    def __init__(self, text: str = "—", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.verdict = text
        self.set_state(text)

    def refresh(self) -> None:
        """Re-read the theme tokens after a theme switch."""
        self.set_state(self.verdict)

    def set_state(self, verdict: str) -> None:
        self.verdict = verdict
        tok = status_token(verdict)
        fg = TOKENS[tok]
        bg = TOKENS["hover"] if tok == "dim" else _rgba(fg, 0.14)
        self.setText(verdict if verdict and verdict != "N/A" else "—")
        self.setStyleSheet(
            f"color:{fg}; background:{bg}; border-radius:3px; padding:2px 6px;"
            f"font-family:'IBM Plex Mono'; font-size:10.5px; font-weight:600;"
        )


class KpiTile(QtWidgets.QFrame):
    """Label / large value / sub-line tile of the KPI strip."""

    def __init__(self, label: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(1)
        self._args = ("—", "", None, False)
        self.lbl = caption(label)
        self.val = QtWidgets.QLabel("—")
        self.sub = QtWidgets.QLabel("")
        self.sub.setProperty("role", "hint")
        lay.addWidget(self.lbl)
        lay.addWidget(self.val)
        lay.addWidget(self.sub)
        self.set("—")

    def set_label(self, text: str) -> None:
        self.lbl.setText(upper_latin(text))

    def refresh(self) -> None:
        """Re-read the theme tokens after a theme switch."""
        self.set(*self._args)

    def set(self, value: str, sub: str = "", tone: Optional[str] = None, display: bool = False) -> None:
        self._args = (value, sub, tone, display)
        self.val.setText(value)
        self.sub.setText(sub)
        col = TOKENS[tone] if tone else TOKENS["fg"]
        family = "'IBM Plex Sans'" if display else "'IBM Plex Mono'"
        weight = 600 if display else 500
        self.val.setStyleSheet(f"color:{col}; font-family:{family}; font-size:18px; font-weight:{weight};")


class KpiStrip(QtWidgets.QFrame):
    """Row of KpiTile separated by hairlines."""

    def __init__(self, labels: List[str], parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("KpiStrip")
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.tiles: List[KpiTile] = []
        for i, lab in enumerate(labels):
            if i:
                lay.addWidget(vsep())
            t = KpiTile(lab)
            self.tiles.append(t)
            lay.addWidget(t, 1)


class DecimalSpinBox(QtWidgets.QDoubleSpinBox):
    """QDoubleSpinBox that accepts both "." and "," as decimal separator whatever the system locale.

    Text is always displayed with "."; "," typed or pasted is read as a decimal point (no thousands separator).
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setLocale(QtCore.QLocale.c())

    def validate(self, text: str, pos: int):
        return super().validate(text.replace(",", "."), pos)

    def valueFromText(self, text: str) -> float:
        return super().valueFromText(text.replace(",", "."))


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
