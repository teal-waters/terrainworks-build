"""Unit tests for binary download/update logic in terrainworks_build.

Tests are fully hermetic — no network calls, no real binaries — using
unittest.mock and pytest's tmp_path fixture.
"""
from pathlib import Path
from unittest.mock import patch

import pytest

import terrainworks_build as tw


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def bin_env(tmp_path):
    """Redirect bin_dir to tmp_path, freeze version to 1.0.0, platform to Linux."""
    with patch("terrainworks_build._bin_dir", return_value=tmp_path), \
         patch.object(tw, "__version__", "1.0.0"), \
         patch("terrainworks_build.platform.system", return_value="Linux"):
        yield tmp_path


def _seed_bin(bin_dir: Path, filename: str, version: str) -> None:
    """Write a fake binary and its per-binary version marker."""
    (bin_dir / filename).write_bytes(b"fake")
    (bin_dir / f".{filename}.version").write_text(version)


def _fake_download(url: str, dest: str) -> None:
    Path(dest).write_bytes(b"new-binary")


# ---------------------------------------------------------------------------
# _cached_version / _write_version_marker
# ---------------------------------------------------------------------------

def test_cached_version_missing(tmp_path):
    assert tw._cached_version(tmp_path, "bldgrds") is None


def test_cached_version_reads_correct_file(tmp_path):
    (tmp_path / ".bldgrds.version").write_text("1.2.3")
    assert tw._cached_version(tmp_path, "bldgrds") == "1.2.3"


def test_version_markers_are_independent(tmp_path):
    with patch.object(tw, "__version__", "2.0.0"):
        tw._write_version_marker(tmp_path, "bldgrds")
    with patch.object(tw, "__version__", "1.0.0"):
        tw._write_version_marker(tmp_path, "MakeGrids")

    assert tw._cached_version(tmp_path, "bldgrds") == "2.0.0"
    assert tw._cached_version(tmp_path, "MakeGrids") == "1.0.0"


# ---------------------------------------------------------------------------
# Cache hits
# ---------------------------------------------------------------------------

def test_returns_cached_when_version_matches(bin_env):
    _seed_bin(bin_env, "bldgrds", "1.0.0")
    with patch("terrainworks_build.urllib.request.urlretrieve") as dl:
        result = tw.get_binary_path("bldgrds")
    assert result == str(bin_env / "bldgrds")
    dl.assert_not_called()


def test_unknown_version_returns_cached_without_download(tmp_path):
    _seed_bin(tmp_path, "bldgrds", "1.0.0")
    with patch("terrainworks_build._bin_dir", return_value=tmp_path), \
         patch.object(tw, "__version__", "unknown"), \
         patch("terrainworks_build.urllib.request.urlretrieve") as dl:
        result = tw.get_binary_path("bldgrds")
    assert result == str(tmp_path / "bldgrds")
    dl.assert_not_called()


# ---------------------------------------------------------------------------
# Stale binary replacement
# ---------------------------------------------------------------------------

def test_deletes_and_redownloads_stale_binary(bin_env):
    _seed_bin(bin_env, "bldgrds", "0.9.0")
    with patch("terrainworks_build.urllib.request.urlretrieve", side_effect=_fake_download):
        result = tw.get_binary_path("bldgrds")
    assert result == str(bin_env / "bldgrds")
    assert tw._cached_version(bin_env, "bldgrds") == "1.0.0"


def test_stale_unlink_failure_returns_existing_with_warning(bin_env, capsys):
    _seed_bin(bin_env, "bldgrds", "0.9.0")
    with patch("terrainworks_build.urllib.request.urlretrieve") as dl, \
         patch.object(Path, "unlink", side_effect=OSError("locked")):
        result = tw.get_binary_path("bldgrds")
    assert result == str(bin_env / "bldgrds")
    assert "Warning" in capsys.readouterr().out
    dl.assert_not_called()


# ---------------------------------------------------------------------------
# Regression: shared version marker (issue #27)
# ---------------------------------------------------------------------------

def test_downloading_one_binary_does_not_mark_another_as_current(bin_env):
    """Downloading bldgrds must not cause MakeGrids to appear up-to-date."""
    _seed_bin(bin_env, "bldgrds", "0.9.0")
    _seed_bin(bin_env, "MakeGrids", "0.9.0")

    with patch("terrainworks_build.urllib.request.urlretrieve", side_effect=_fake_download):
        tw.get_binary_path("bldgrds")

    assert tw._cached_version(bin_env, "MakeGrids") == "0.9.0"


# ---------------------------------------------------------------------------
# Download failures
# ---------------------------------------------------------------------------

def test_download_failure_raises_file_not_found(bin_env):
    with patch("terrainworks_build.urllib.request.urlretrieve", side_effect=OSError("timeout")):
        with pytest.raises(FileNotFoundError, match="timeout"):
            tw.get_binary_path("bldgrds")


def test_download_failure_cleans_up_tmp_file(bin_env):
    with patch("terrainworks_build.urllib.request.urlretrieve", side_effect=OSError):
        with pytest.raises(FileNotFoundError):
            tw.get_binary_path("bldgrds")
    assert not any(bin_env.iterdir())


def test_version_marker_not_written_on_download_failure(bin_env):
    with patch("terrainworks_build.urllib.request.urlretrieve", side_effect=OSError):
        with pytest.raises(FileNotFoundError):
            tw.get_binary_path("bldgrds")
    assert tw._cached_version(bin_env, "bldgrds") is None


def test_unknown_version_raises_when_no_binary(tmp_path):
    with patch("terrainworks_build._bin_dir", return_value=tmp_path), \
         patch.object(tw, "__version__", "unknown"):
        with pytest.raises(FileNotFoundError, match="unknown"):
            tw.get_binary_path("bldgrds")


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------

def test_windows_uses_exe_suffix(tmp_path):
    _seed_bin(tmp_path, "bldgrds.exe", "1.0.0")
    with patch("terrainworks_build._bin_dir", return_value=tmp_path), \
         patch.object(tw, "__version__", "1.0.0"), \
         patch("terrainworks_build.platform.system", return_value="Windows"), \
         patch("terrainworks_build.urllib.request.urlretrieve") as dl:
        result = tw.get_binary_path("bldgrds")
    assert result.endswith("bldgrds.exe")
    dl.assert_not_called()


def test_windows_downloads_exe(tmp_path):
    with patch("terrainworks_build._bin_dir", return_value=tmp_path), \
         patch.object(tw, "__version__", "1.0.0"), \
         patch("terrainworks_build.platform.system", return_value="Windows"), \
         patch("terrainworks_build.urllib.request.urlretrieve", side_effect=_fake_download) as dl:
        tw.get_binary_path("bldgrds")
    url = dl.call_args[0][0]
    assert url.endswith("bldgrds.exe")
