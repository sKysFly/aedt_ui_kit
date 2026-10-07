"""Propagate ui_kit/ to the toolkits that embed a copy of it, or report the copies that drifted.

Usage: python tools/sync_ui_kit.py [--check]
The toolkit repositories are expected next to this one. --check only reports (exit code 1 on a drift).
"""

import filecmp
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), "ui_kit")
REPOS = os.path.dirname(os.path.dirname(HERE))

COPIES = [
    "aedt_tdr/tdr_impedance_toolkit/ui_kit",
    "aedt_eye/eye_diagram_toolkit/ui_kit",
    "aedt_eye/eye_diagram_toolkit_dist/ui_kit",
    "aedt_crosstalk/crosstalk_matrix_toolkit/ui_kit",
    "aedt_crosstalk/crosstalk_matrix_toolkit_dist/ui_kit",
    "aedt_port_checker/port_checker_toolkit/ui_kit",
]


def source_files() -> list:
    out = []
    for root, dirs, files in os.walk(SOURCE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        out += [os.path.relpath(os.path.join(root, f), SOURCE) for f in files]
    return sorted(out)


def drift(copy_dir: str) -> list:
    """Files of the source that are missing or different in `copy_dir`."""
    return [rel for rel in source_files()
            if not os.path.isfile(os.path.join(copy_dir, rel))
            or not filecmp.cmp(os.path.join(SOURCE, rel), os.path.join(copy_dir, rel), shallow=False)]


def main() -> int:
    check = "--check" in sys.argv
    status = 0
    for rel in COPIES:
        target = os.path.join(REPOS, *rel.split("/"))
        if not os.path.isdir(target):
            print(f"absent  {rel}")
            continue
        bad = drift(target)
        if not bad:
            print(f"ok      {rel}")
            continue
        status = 1
        if check:
            print(f"écart   {rel} : {', '.join(bad)}")
            continue
        for f in bad:
            os.makedirs(os.path.dirname(os.path.join(target, f)), exist_ok=True)
            shutil.copyfile(os.path.join(SOURCE, f), os.path.join(target, f))
        print(f"copié   {rel} : {', '.join(bad)}")
    return status if check else 0


if __name__ == "__main__":
    sys.exit(main())
