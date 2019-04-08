"""Configuration of pytest."""

import pytest

from looseserver.server.core import Manager


# Fixtures use other fixtures, so we disable the check.
# pylint: disable=redefined-outer-name
@pytest.fixture
def base_endpoint():
    """Base endpoint for routes."""
    return "/routes/"


@pytest.fixture
def configuration_endpoint():
    """Endpoint to configure routes."""
    return "/_configuration/"


@pytest.fixture
def core_manager(base_endpoint):
    """Core manager."""
    return Manager(base=base_endpoint)
# pylint: enable=redefined-outer-name
