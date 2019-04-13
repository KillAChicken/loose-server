"""Module to manage the default application."""

from looseserver.common.utils import ensure_endpoint
from looseserver.server.application import (
    configure_application as main_configure_application,
    DEFAULT_BASE_ENDPOINT,
    DEFAULT_CONFIGURATION_ENDPOINT,
    )
from looseserver.default.server.rule import create_rule_factory
from looseserver.default.server.response import create_response_factory


def configure_application(
        rule_factory=None,
        response_factory=None,
        base_endpoint=DEFAULT_BASE_ENDPOINT,
        configuration_endpoint=DEFAULT_CONFIGURATION_ENDPOINT,
    ):
    """Configure application with default factories.

    :param rule_factory: :class:`RuleFactory <looseserver.common.rule.RuleFactory>`
        to parse and serialize rules. Default rule factory is used if not specified.
    :param response_factory: :class:`ResponseFactory <looseserver.common.response.ResponseFactory>`
        to parse and serialize responses. Default response factory is used if not specified.
    :param base_endpoint: string with base endpoint for configured routes.
    :param configuration_endpoint: string with endpoint to configure routes.
    :returns: configured application, created by
        :meth:`configure_application <looseserver.server.application.configure_application>`.
    """
    base_endpoint = ensure_endpoint(base_endpoint)
    configuration_endpoint = ensure_endpoint(configuration_endpoint)

    if rule_factory is None:
        rule_factory = create_rule_factory(base_url=base_endpoint)
    if response_factory is None:
        response_factory = create_response_factory()

    return main_configure_application(
        rule_factory=rule_factory,
        response_factory=response_factory,
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        )
