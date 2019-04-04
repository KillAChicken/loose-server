"""Configuration of pytest."""

import pytest

from looseserver.server.core import Manager
from looseserver.server.rule import ServerRule
from looseserver.server.response import ServerResponse


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


@pytest.fixture
def rule_prototype():
    """Rule prototype."""
    class ConfigurableRule(ServerRule):
        """Class for configurable rule."""

        def __init__(self, rule_type="test", match_implementation=None):
            super(ConfigurableRule, self).__init__(rule_type=rule_type)

            if match_implementation is None:
                match_implementation = lambda *args, **kwargs: None

            self.match_implementation = match_implementation

        def is_match_found(self, request):
            """Check request for a match."""
            return self.match_implementation(self, request)

        def create_new(self, rule_type=None, match_implementation=None):
            """Create new rule from the existing one."""
            if rule_type is None:
                rule_type = self.rule_type

            if match_implementation is None:
                match_implementation = self.match_implementation

            return ConfigurableRule(rule_type=rule_type, match_implementation=match_implementation)

    return ConfigurableRule()


@pytest.fixture
def response_prototype():
    """Response prototype."""
    class ConfigurableResponse(ServerResponse):
        """Class for configurable response."""

        def __init__(self, response_type="test", builder_implementation=None):
            super(ConfigurableResponse, self).__init__(response_type=response_type)

            if builder_implementation is None:
                builder_implementation = lambda *args, **kwargs: None

            self.builder_implementation = builder_implementation

        def build_response(self, request, rule):
            """Build response."""
            return self.builder_implementation(self, request, rule)

        def create_new(self, response_type=None, builder_implementation=None):
            """Create new rule from the existing one."""
            if response_type is None:
                response_type = self.response_type

            if builder_implementation is None:
                builder_implementation = self.builder_implementation

            return ConfigurableResponse(
                response_type=response_type,
                builder_implementation=builder_implementation,
                )

    return ConfigurableResponse()
# pylint: enable=redefined-outer-name
