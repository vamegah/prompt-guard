import json
from pathlib import Path
from typing import List, Dict, Any

from promptguard_shared.models.prompt import PromptTemplate
from promptguard_shared.models.test import TestInput


def load_prompt(path: Path) -> PromptTemplate:
    """Load a prompt template from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return PromptTemplate(name=path.stem, template=content)


def load_schema(path: Path) -> Dict[str, Any]:
    """Load a JSON schema from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_test_inputs(path: Path) -> List[TestInput]:
    """Load test inputs from a JSON file.

    Supported formats:
      - ["Hello", "World"]
      - [{"input": "Hello"}, {"input": "World"}]
      - [{"question": "Hello"}, {"question": "World"}]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Test inputs file must contain a JSON array")

    test_inputs: List[TestInput] = []
    for idx, item in enumerate(data):
        if isinstance(item, str):
            test_inputs.append(TestInput(id=str(idx), input_data={"input": item}))
        elif isinstance(item, dict):
            if "input_data" in item and isinstance(item["input_data"], dict):
                input_data = item["input_data"]
            elif "input" in item:
                input_data = {"input": item["input"]}
            else:
                input_data = item
            test_inputs.append(
                TestInput(
                    id=str(item.get("id", idx)),
                    input_data=input_data,
                    expected_output=item.get("expected_output"),
                    description=item.get("description"),
                )
            )
        else:
            raise ValueError(
                f"Each test input must be a string or object, got {type(item)} at index {idx}"
            )
    return test_inputs
