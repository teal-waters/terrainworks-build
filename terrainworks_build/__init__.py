"""TerrainWorks binary distribution package."""

try:
    from terrainworks_build._version import __version__
except ImportError:
    __version__ = "unknown"

import platform
import stat
import urllib.request
from pathlib import Path

TERRAINWORKS_REPO = "teal-waters/terrainworks-build"


def get_binary_path(name: str) -> str:
    """Locate a terrainworks binary, downloading it on first use if needed.

    Checks the bundled bin directory first, then PATH, then downloads from
    the matching GitHub release.

    Args:
        name: Binary name without extension (e.g. ``"bldgrds"``).

    Returns:
        Absolute path to the binary.

    Raises:
        FileNotFoundError: If the binary cannot be found or downloaded.
    """
    is_windows = platform.system() == "Windows"
    filename = f"{name}.exe" if is_windows else name
    bin_dir = Path(__file__).parent / "bin"
    cached = bin_dir / filename

    if cached.exists():
        return str(cached)

    if __version__ == "unknown":
        raise FileNotFoundError(
            f"Could not find {name!r} and package version is unknown; "
            "cannot download. Ensure the binary is available on PATH."
        )

    tag = f"v{__version__}"
    url = f"https://github.com/{TERRAINWORKS_REPO}/releases/download/{tag}/{filename}"
    bin_dir.mkdir(exist_ok=True)
    print(f"Downloading {filename} from {TERRAINWORKS_REPO}@{tag}...")
    try:
        urllib.request.urlretrieve(url, cached)  # noqa: S310
    except Exception as e:
        cached.unlink(missing_ok=True)
        raise FileNotFoundError(
            f"Failed to download {name!r} from {url}: {e}"
        ) from e

    if not is_windows:
        cached.chmod(cached.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return str(cached)
