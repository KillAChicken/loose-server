"""Test cases for common test cases for the core manager."""

import looseserver.server.core as core


def test_base(base_endpoint):
    """Check base endpoint used by the manager.

    1. Create core manager.
    2. Check base.
    """
    manager = core.Manager(base=base_endpoint)
    assert manager.base == base_endpoint, "Base endpoint has been changed"
