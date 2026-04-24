import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Make local backend packages importable during pytest runs without requiring installation.
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "cli"))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "shared"))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "services", "prompt-manager"))

# Other service packages may also rely on local imports.
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "services", "validation-engine"))
sys.path.insert(0, os.path.join(ROOT_DIR, "backend", "services", "llm-gateway"))
