"""Module to start quick server."""

import argparse
import urllib.parse as urlparse

from flask import Flask
from flask_restful import Api

from looseserver.server.core import Manager
from looseserver.server.api import RulesManager, Rule, Response
from looseserver.default.server.rule import create_rule_factory
from looseserver.default.server.response import create_response_factory


def configure_application(base_endpoint, configuration_endpoint):
    """Configure application.

    :param base_endpoint: string with base endpoint for configured routes.
    :param configuration_endpoint: string with endpoint to configure routes.
    :returns: flask.Flask object.
    """
    base_endpoint = _ensure_endpoint(base_endpoint)
    configuration_endpoint = _ensure_endpoint(configuration_endpoint)

    core_manager = Manager(base=base_endpoint)
    rule_factory = create_rule_factory(base_endpoint)
    response_factory = create_response_factory()

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


def _parse_args():
    """Parse commandline arguments.

    :returns: argparse namespace.
    """
    parser = argparse.ArgumentParser(description="Quick server")
    parser.add_argument("--host", default="127.0.0.1", dest="host", help="Host to bind")
    parser.add_argument("--port", default=50000, dest="port", type=int, help="Port to listen")
    parser.add_argument(
        "--configuration-endpoint",
        default="/_configuration/",
        dest="configuration_endpoint",
        help="Endpoint for configuration",
        )
    parser.add_argument(
        "--base-endpoint",
        default="/routes/",
        dest="base_endpoint",
        help="Base endpoint for configured routes",
        )
    return parser.parse_args()


def _ensure_endpoint(endpoint):
    """Ensure that endpoint starts and ends with slashes.

    :param endpoint: string endpoint.
    :returns: the same string starting and ending with slashes.
    """
    ensured_endpoint = urlparse.urljoin("/", endpoint)
    if not ensured_endpoint.endswith("/"):
        ensured_endpoint += "/"
    return ensured_endpoint


def _run():
    """Entrypoint to run a quick server."""
    args = _parse_args()

    application = configure_application(
        base_endpoint=args.base_endpoint,
        configuration_endpoint=args.configuration_endpoint,
        )

    application.run(host=args.host, port=args.port)


if __name__ == "__main__":
    _run()
