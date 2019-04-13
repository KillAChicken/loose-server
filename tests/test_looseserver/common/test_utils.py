"""Test cases for looseserver common helper functions."""

import pytest

from looseserver.common.utils import ensure_endpoint


@pytest.mark.parametrize(
    argnames="specified_endpoint,expected_endpoint",
    argvalues=[
        ("/valid/", "/valid/"),
        ("/missed-at-the-end", "/missed-at-the-end/"),
        ("missed-at-the-beginning/", "/missed-at-the-beginning/"),
        ("missed-both", "/missed-both/"),
        ],
    ids=[
        "No missing slashes",
        "Missing at the end",
        "Missing at the beginning",
        "Missing both",
        ],
    )
def test_ensure_endpoint(specified_endpoint, expected_endpoint):
    """Check that missing slashes are added by the ensure_endpoint function."""
    assert ensure_endpoint(specified_endpoint) == expected_endpoint, "Wrong endpoint"
