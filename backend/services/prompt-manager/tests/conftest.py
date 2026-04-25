import importlib
import os
import sys
from pathlib import Path

import pytest


base = Path(__file__).resolve().parents[1]
base_path = str(base)
if base_path in sys.path:
    sys.path.remove(base_path)
sys.path.insert(0, base_path)

for module_name in list(sys.modules):
    if module_name == "app" or module_name.startswith("app."):
        del sys.modules[module_name]
importlib.invalidate_caches()


@pytest.fixture
def set_env():
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://promptguard:password@localhost:5432/promptguard_test"
    )
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    yield
