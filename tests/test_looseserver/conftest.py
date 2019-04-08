"""Configuration of pytest."""

import pytest

from looseserver.common.rule import RuleFactory
from looseserver.common.response import ResponseFactory


@pytest.fixture
def rule_factory():
    """Rule factory."""
    return RuleFactory()


@pytest.fixture
def response_factory():
    """Response factory."""
    return ResponseFactory()
