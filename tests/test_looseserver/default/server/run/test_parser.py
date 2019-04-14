"""Test cases for commandline parser."""

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.default.server.run import create_parser


def test_host():
    """Test host parameter.

    1. Create the parser.
    2. Parse arguments with the host parameter.
    3. Check that host is parsed.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args(["--host", "test"])
    assert parsed_arguments.host == "test", "Wrong host"


def test_default_host():
    """Test default value for the host.

    1. Create the parser.
    2. Parse arguments without host parameters.
    3. Check value of the host.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args([])
    assert parsed_arguments.host == "127.0.0.1", "Wrong host"


def test_port():
    """Test port parameter.

    1. Create the parser.
    2. Parse arguments with the port parameter.
    3. Check that port is parsed.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args(["--port", "11111"])
    assert parsed_arguments.port == 11111, "Wrong port"


def test_default_port():
    """Test default value for the port.

    1. Create the parser.
    2. Parse arguments without port parameters.
    3. Check value of the port.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args([])
    assert parsed_arguments.port == 50000, "Wrong port"


def test_base_endpoint():
    """Test base endpoint parameter.

    1. Create the parser.
    2. Parse arguments with parameter for a base endpoint.
    3. Check that base endpoint is parsed.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args(["--base-endpoint", "/test"])
    assert parsed_arguments.base_endpoint == "/test", "Wrong endpoint"


def test_default_base_endpoint():
    """Test default value for the base endpoint.

    1. Create parser.
    2. Parse arguments without base endpoint.
    3. Check value of the base endpoint.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args([])
    assert parsed_arguments.base_endpoint == DEFAULT_BASE_ENDPOINT, "Wrong endpoint"


def test_configuration_endpoint():
    """Test configuration endpoint parameter.

    1. Create the parser.
    2. Parse arguments with parameter for a configuration endpoint.
    3. Check that base endpoint is parsed.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args(["--configuration-endpoint", "/test"])
    assert parsed_arguments.configuration_endpoint == "/test", "Wrong endpoint"


def test_default_configuration_endpoint():
    """Test default value for the base endpoint.

    1. Create parser.
    2. Parse arguments without base endpoint.
    3. Check value of the base endpoint.
    """
    parser = create_parser()
    parsed_arguments = parser.parse_args([])
    assert parsed_arguments.configuration_endpoint == DEFAULT_CONFIGURATION_ENDPOINT, (
        "Wrong endpoint"
        )
