from pathlib import Path
from setuptools import setup, find_packages

shared_path = Path(__file__).resolve().parents[1] / "shared"
shared_uri = shared_path.as_uri()

setup(
    name="promptguard-cli",
    version="0.1.0",
    description="CLI tool for validating LLM prompts against schemas",
    author="PromptGuard Team",
    author_email="team@promptguard.io",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        f"promptguard-shared @ {shared_uri}",
    ],
    entry_points={
        "console_scripts": [
            "promptguard = promptguard.cli:cli",
        ],
    },
    python_requires=">=3.9",
)
