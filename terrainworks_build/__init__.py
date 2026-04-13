"""TerrainWorks binary distribution package."""

try:
    from terrainworks_build._version import __version__
except ImportError:
    __version__ = "unknown"

import platform
import shutil
from pathlib import Path


def get_binary_path(name: str) -> str:
    """Locate a terrainworks binary.

    Checks the bundled bin directory first, then falls back to PATH.

    Args:
        name: Binary name without extension (e.g. ``"MakeGrids"``).

    Returns:
        Absolute path to the binary.

    Raises:
        FileNotFoundError: If the binary is not found in the package or on PATH.
    """
    filename = f"{name}.exe" if platform.system() == "Windows" else name

    bundled = Path(__file__).parent / "bin" / filename
    if bundled.exists():
        return str(bundled)

    on_path = shutil.which(name)
    if on_path:
        return on_path

    raise FileNotFoundError(
        f"Could not find {name!r}. Reinstall terrainworks-build, "
        "or ensure the binary is available on PATH."
    )
