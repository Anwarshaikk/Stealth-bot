# Minimal conftest for pytest (can be empty unless fixtures are needed globally) 

import pytest
from unittest.mock import MagicMock

@pytest.fixture(scope="function")
def mock_redis_conn():
    """Fixture to mock the Redis connection."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    return mock_redis 