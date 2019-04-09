"""Configuration of pytest."""

import pytest

from looseserver.server.core import Manager


@pytest.fixture
def core_manager(base_endpoint):
    """Core manager."""
    return Manager(base=base_endpoint)
