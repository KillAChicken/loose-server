"""Module to manage the application."""

import urllib.parse as urlparse

from flask import Flask
from flask_restful import Api

from looseserver.common.utils import ensure_endpoint
from looseserver.server.core import Manager
from looseserver.server.api import RulesManager, Rule, Response


DEFAULT_BASE_ENDPOINT = "/routes/"
DEFAULT_CONFIGURATION_ENDPOINT = "/_configuration/"


def configure_application(
        rule_factory,
        response_factory,
        base_endpoint=DEFAULT_BASE_ENDPOINT,
        configuration_endpoint=DEFAULT_CONFIGURATION_ENDPOINT,
    ):
    """Configure application.

    :param rule_factory: :class:`RuleFactory <looseserver.common.rule.RuleFactory>`
        to parse and serialize rules.
    :param response_factory: :class:`ResponseFactory <looseserver.common.response.ResponseFactory>`
        to parse and serialize responses.
    :param base_endpoint: string with base endpoint for configured routes.
    :param configuration_endpoint: string with endpoint to configure routes.
    :returns: flask.Flask object.
    """
    base_endpoint = ensure_endpoint(base_endpoint)
    configuration_endpoint = ensure_endpoint(configuration_endpoint)

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
