"""Module to start loose server with default configuration."""

import argparse

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.default.server.application import configure_application


def create_parser():
    """Create argument parser.

    :returns: instance of argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(description="Loose server")
    parser.add_argument("--host", default="127.0.0.1", dest="host", help="Host to bind")
    parser.add_argument("--port", default=50000, dest="port", type=int, help="Port to listen")
    parser.add_argument(
        "--configuration-endpoint",
        default=DEFAULT_CONFIGURATION_ENDPOINT,
        dest="configuration_endpoint",
        help="Endpoint for configuration",
        )
    parser.add_argument(
        "--base-endpoint",
        default=DEFAULT_BASE_ENDPOINT,
        dest="base_endpoint",
        help="Base endpoint for configured routes",
        )

    return parser


def _run(commandline_arguments=None):
    """Entrypoint to run a loose server."""
    if __name__ == "__main__":
        parser = create_parser()
        arguments = parser.parse_args(commandline_arguments)
        application = configure_application(
            base_endpoint=arguments.base_endpoint,
            configuration_endpoint=arguments.configuration_endpoint,
            )

        application.run(host=arguments.host, port=arguments.port)


_run()
