import os
import sys
from pathlib import Path

import pytest


base = Path(__file__).resolve().parents[1]
if str(base) not in sys.path:
    sys.path.insert(0, str(base))


@pytest.fixture
def set_env():
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["LLM_GATEWAY_URL"] = "http://llm-gateway:8002/api/v1/generate"
    os.environ["ANALYTICS_URL"] = "http://analytics:8003/api/v1/metrics"
    yield
