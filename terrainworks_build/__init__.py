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


def _cached_version(bin_dir: Path, filename: str) -> str | None:
    """Read the version marker for a specific binary."""
    try:
        return (bin_dir / f".{filename}.version").read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _write_version_marker(bin_dir: Path, filename: str) -> None:
    """Write the current package version as the version marker for a specific binary."""
    try:
        (bin_dir / f".{filename}.version").write_text(__version__, encoding="utf-8")
    except OSError:
        pass


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
        if __version__ != "unknown" and _cached_version(bin_dir, filename) != __version__:
            try:
                cached.unlink()
            except OSError:
                print(
                    f"Warning: could not remove stale {filename}; "
                    "using existing binary."
                )
                return str(cached)
        else:
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
    tmp = cached.with_suffix(".tmp")
    try:
        urllib.request.urlretrieve(url, tmp)  # noqa: S310
        tmp.replace(cached)
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise FileNotFoundError(
            f"Failed to download {name!r} from {url}: {e}"
        ) from e

    if not is_windows:
        cached.chmod(cached.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    _write_version_marker(bin_dir, filename)
    return str(cached)
