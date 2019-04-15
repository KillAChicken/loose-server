"""Configuration of pytest."""

import pytest

from looseserver.common.rule import RuleFactory
from looseserver.common.response import ResponseFactory
from looseserver.server.rule import ServerRule
from looseserver.server.response import ServerResponse
from looseserver.server.application import configure_application


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
def server_rule_factory():
    """Custom rule factory for server."""
    return RuleFactory()


@pytest.fixture
def server_response_factory():
    """Custom response factory for server."""
    return ResponseFactory()


@pytest.fixture
def client_rule_factory():
    """Custom rule factory for client."""
    return RuleFactory()


@pytest.fixture
def client_response_factory():
    """Custom response factory for client."""
    return ResponseFactory()


@pytest.fixture
def application_factory(
        base_endpoint,
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
    ):
    """
    Callable factory, producing configured application.
    Other fixtures are used for the default values, namely:
        base_endpoint,
        configuration_endpoint,
        server_rule_factory,
        server_response_factory.
    """
    def _application_factory(
            base_endpoint=base_endpoint,
            configuration_endpoint=configuration_endpoint,
            rule_factory=server_rule_factory,
            response_factory=server_response_factory,
        ):
        return configure_application(
            base_endpoint=base_endpoint,
            configuration_endpoint=configuration_endpoint,
            rule_factory=rule_factory,
            response_factory=response_factory,
            )

    return _application_factory


@pytest.fixture
def server_rule_prototype():
    """Rule prototype."""
    class ConfigurableRule(ServerRule):
        """Class for configurable rule."""

        def __init__(self, rule_type="test", match_implementation=None):
            super(ConfigurableRule, self).__init__(rule_type=rule_type)

            if not callable(match_implementation):
                value = match_implementation
                match_implementation = lambda *args, **kwargs: value

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
def server_response_prototype():
    """Response prototype."""
    class ConfigurableResponse(ServerResponse):
        """Class for configurable response."""

        def __init__(self, response_type="test", builder_implementation=None):
            super(ConfigurableResponse, self).__init__(response_type=response_type)

            if not callable(builder_implementation):
                value = builder_implementation
                builder_implementation = lambda *args, **kwargs: value

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
