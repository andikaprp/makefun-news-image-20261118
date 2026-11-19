"""Install the shipped entry image into the output directory.

The page itself is drawn by render.py (Pillow) and committed to this
repository as entry.png; this program simply copies that file to
$MAKEFUN_OUTPUT_DIR (default /output) as entry.png. Standard library
only, so it runs in any Python 3 environment.
"""

import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_dir / "entry.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
