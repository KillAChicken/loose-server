"""Module to start loose server."""

import argparse

from looseserver.server.application import (
    configure_application,
    DEFAULT_BASE_ENDPOINT,
    DEFAULT_CONFIGURATION_ENDPOINT,
    )


def _parse_args():
    """Parse commandline arguments.

    :returns: argparse namespace.
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
    return parser.parse_args()


def _run():
    """Entrypoint to run a loose server."""
    args = _parse_args()

    application = configure_application(
        base_endpoint=args.base_endpoint,
        configuration_endpoint=args.configuration_endpoint,
        )

    application.run(host=args.host, port=args.port)


if __name__ == "__main__":
    _run()
