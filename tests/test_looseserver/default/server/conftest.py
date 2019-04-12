"""Configuration of pytest."""

import pytest


@pytest.fixture
def configured_application_client(application_factory):
    """Configured application."""
    return application_factory().test_client()
