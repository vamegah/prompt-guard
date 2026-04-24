import os
import sys
from pathlib import Path

import pytest


base = Path(__file__).resolve().parents[1]
if str(base) not in sys.path:
    sys.path.insert(0, str(base))


@pytest.fixture
def set_env():
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    os.environ["OPENAI_API_KEY"] = "test"
    os.environ["INTERNAL_API_KEY"] = "internal-key"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["REQUIRE_ORG_SCOPED_KEYS"] = "false"
    yield
