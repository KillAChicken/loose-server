"""Module to manage the application."""

import urllib.parse as urlparse

from flask import Flask
from flask_restful import Api

from looseserver.server.core import Manager
from looseserver.server.api import RulesManager, Rule, Response
from looseserver.default.server.rule import create_rule_factory
from looseserver.default.server.response import create_response_factory


DEFAULT_BASE_ENDPOINT = "/routes/"
DEFAULT_CONFIGURATION_ENDPOINT = "/_configuration/"


def configure_application(
        base_endpoint=DEFAULT_BASE_ENDPOINT,
        configuration_endpoint=DEFAULT_CONFIGURATION_ENDPOINT,
        rule_factory=None,
        response_factory=None,
    ):
    """Configure application.

    :param base_endpoint: string with base endpoint for configured routes.
    :param configuration_endpoint: string with endpoint to configure routes.
    :param rule_factory: :class:`RuleFactory <looseserver.common.rule.RuleFactory>`
        to parse and serialize rules.
    :param response_factory: :class:`ResponseFactory <looseserver.common.response.ResponseFactory>`
        to parse and serialize responses.
    :returns: flask.Flask object.
    """
    base_endpoint = _ensure_endpoint(base_endpoint)
    configuration_endpoint = _ensure_endpoint(configuration_endpoint)

    if rule_factory is None:
        rule_factory = create_rule_factory(base_endpoint)
    if response_factory is None:
        response_factory = create_response_factory()

    core_manager = Manager(base=base_endpoint)

    application = Flask(__name__.split(".")[0])
    api = Api(application)

    api.add_resource(
        RulesManager,
        urlparse.urljoin(configuration_endpoint, "rules"),
        endpoint="configuration_rules",
        resource_class_args=(core_manager, rule_factory),
        )

    api.add_resource(
        Rule,
        urlparse.urljoin(configuration_endpoint, "rule/<rule_id>"),
        endpoint="configuration_rule",
        resource_class_args=(core_manager, rule_factory),
        )

    api.add_resource(
        Response,
        urlparse.urljoin(configuration_endpoint, "response/<rule_id>"),
        endpoint="configuration_response",
        resource_class_args=(core_manager, response_factory),
        )

    methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]
    application.add_url_rule(
        rule=base_endpoint,
        endpoint="base",
        view_func=core_manager.view,
        methods=methods,
        )
    application.add_url_rule(
        rule=urlparse.urljoin(base_endpoint, "<path:path>"),
        endpoint="route",
        view_func=core_manager.view,
        methods=methods,
        )

    return application


def _ensure_endpoint(endpoint):
    """Ensure that endpoint starts and ends with slashes.

    :param endpoint: string endpoint.
    :returns: the same string starting and ending with slashes.
    """
    ensured_endpoint = urlparse.urljoin("/", endpoint)
    if not ensured_endpoint.endswith("/"):
        ensured_endpoint += "/"
    return ensured_endpoint
