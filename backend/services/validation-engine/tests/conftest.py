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


@pytest.fixture(autouse=True)
def isolate_service_imports():
    original_path = list(sys.path)
    original_app_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "app" or name.startswith("app.")
    }
    if base_path in sys.path:
        sys.path.remove(base_path)
    sys.path.insert(0, base_path)
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]
    importlib.invalidate_caches()
    yield
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]
    sys.modules.update(original_app_modules)
    sys.path[:] = original_path
    importlib.invalidate_caches()


@pytest.fixture
def set_env():
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["LLM_GATEWAY_URL"] = "http://llm-gateway:8002/api/v1/generate"
    os.environ["ANALYTICS_URL"] = "http://analytics:8003/api/v1/metrics"
    os.environ["INTERNAL_API_KEY"] = "internal-key"
    yield
