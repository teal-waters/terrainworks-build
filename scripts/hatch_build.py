"""Hatch build hook to bundle terrainworks binaries into the wheel."""

import platform
import shutil
import stat
import urllib.request
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

TERRAINWORKS_REPO = "teal-waters/terrainworks-build"
BINARIES = ["MakeGrids", "build_derivs", "bldgrds"]


class CustomBuildHook(BuildHookInterface):
    """Bundles platform-specific terrainworks binaries into the wheel.

    For editable installs (local dev): copies binaries built by ``make`` from
    the repo root.  For wheel builds: downloads from the matching GitHub release.
    """

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Locate and bundle binaries for the current platform.

        Args:
            version: Package version string provided by hatchling.  When
                building an editable install this is ``"editable"``; for a
                normal wheel build it is the resolved package version (e.g.
                ``"0.1.0"``).
            build_data: Mutable build metadata dict provided by hatchling.
        """
        system = platform.system()
        if system not in ("Linux", "Windows"):
            print(
                f"Warning: terrainworks binaries are not available for {system}. "
                "Add MakeGrids, build_derivs, and bldgrds to PATH manually."
            )
            return

        is_windows = system == "Windows"
        machine = platform.machine().lower()
        is_editable = version == "editable"

        bin_dir = Path("terrainworks_build") / "bin"
        bin_dir.mkdir(exist_ok=True)

        for binary in BINARIES:
            filename = f"{binary}.exe" if is_windows else binary
            dest = bin_dir / filename

            if not dest.exists():
                if is_editable:
                    self._copy_local(filename, dest)
                else:
                    self._download(filename, dest, version)

            if dest.exists():
                if not is_windows:
                    dest.chmod(dest.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                build_data["force_include"][str(dest)] = f"terrainworks_build/bin/{filename}"

        if is_windows:
            build_data["tag"] = f"py3-none-win_{machine}"
        else:
            build_data["tag"] = f"py3-none-linux_{machine}"

    def _copy_local(self, filename: str, dest: Path) -> None:
        """Copy a locally-built binary (from ``make``) into the bin dir."""
        local = Path(filename)
        if local.exists():
            print(f"Copying local build of {filename}...")
            shutil.copy2(local, dest)
        else:
            print(
                f"Warning: {filename} not found in repo root. "
                "Run 'make' to build it, or it will be looked up on PATH at runtime."
            )

    def _download(self, filename: str, dest: Path, version: str) -> None:
        """Download a binary from the matching GitHub release."""
        tag = f"v{version}"
        url = (
            f"https://github.com/{TERRAINWORKS_REPO}/releases/download/"
            f"{tag}/{filename}"
        )
        print(f"Downloading {filename} from {TERRAINWORKS_REPO}@{tag}...")
        try:
            urllib.request.urlretrieve(url, dest)  # noqa: S310
        except Exception:
            dest.unlink(missing_ok=True)
            raise
