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


# FIXME: rename rule_prototype into server_rule_prototype in test cases and remove the fixture
@pytest.fixture
def rule_prototype(server_rule_prototype):
    """Server rule prototype."""
    return server_rule_prototype


# FIXME: rename response_prototype into server_response_prototype in test cases and
# remove the fixture
@pytest.fixture
def response_prototype(server_response_prototype):
    """Server response prototype."""
    return server_response_prototype
# pylint: enable=redefined-outer-name
