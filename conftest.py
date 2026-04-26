import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Make local backend packages importable during pytest runs without requiring installation.
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "cli"))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "shared"))

# These are application modules whose names describe PromptGuard test suites,
# not pytest test modules. Without this, pytest tries to collect imported
# Pydantic/SQLAlchemy classes such as TestSuite and TestSuiteCreate.
collect_ignore = [
    "backend/services/prompt-manager/app/api/test_suites.py",
    "backend/services/prompt-manager/app/models/test_suite.py",
    "backend/services/prompt-manager/app/models/test_suites.py",
    "backend/services/prompt-manager/app/repositories/test_suite.py",
    "backend/services/prompt-manager/app/schemas/test_suite.py",
    "backend/services/prompt-manager/app/schemas/s/test_suite.py",
]
