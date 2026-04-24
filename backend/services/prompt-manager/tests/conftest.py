import os
import sys
from pathlib import Path

import pytest


base = Path(__file__).resolve().parents[1]
if str(base) not in sys.path:
    sys.path.insert(0, str(base))


@pytest.fixture
def set_env():
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://promptguard:password@localhost:5432/promptguard_test"
    )
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    yield
