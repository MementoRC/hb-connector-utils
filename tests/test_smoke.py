"""Smoke tests for hb-connector-utils — verifies the package imports and version is set."""

import pytest

import connector_utils
from connector_utils import __version__


@pytest.mark.unit
def test_package_importable() -> None:
    """Package imports without error."""
    assert connector_utils is not None


@pytest.mark.unit
def test_version_is_string() -> None:
    """__version__ is a non-empty string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


@pytest.mark.unit
def test_version_format() -> None:
    """__version__ follows semver major.minor.patch pattern."""
    parts = __version__.split(".")
    assert len(parts) == 3, f"Expected 3 version parts, got: {__version__!r}"
    assert all(part.isdigit() for part in parts), f"Non-numeric version part in: {__version__!r}"
