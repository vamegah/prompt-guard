import pytest
import json
from click.testing import CliRunner

from promptguard.cli import cli
from promptguard.core.runner import ValidationRunner
from promptguard_shared.models.result import ValidationReport, PromptTestResult


# We'll create fixtures in a conftest.py or here
@pytest.fixture
def sample_files(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Translate to French: {{input}}")

    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"type": "string"}))

    tests_file = tmp_path / "tests.json"
    tests_file.write_text(json.dumps([{"input": "Hello"}, {"input": "Goodbye"}]))

    return prompt_file, schema_file, tests_file


def test_validate_command(sample_files, monkeypatch):
    # Mock API key
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    # We need to mock the LLM call to avoid real API calls.
    async def mock_run(self):
        return ValidationReport(
            test_case_id="test",
            results=[
                PromptTestResult(test_input_id="0", passed=True, errors=[]),
                PromptTestResult(test_input_id="1", passed=False, errors=["Invalid schema"]),
            ],
            total_passed=1,
            total_failed=1,
            duration_ms=100,
            metadata={},
        )

    monkeypatch.setattr(ValidationRunner, "run", mock_run)

    runner = CliRunner()
    prompt_file, schema_file, tests_file = sample_files
    result = runner.invoke(
        cli,
        [
            "validate",
            "--prompt",
            str(prompt_file),
            "--schema",
            str(schema_file),
            "--tests",
            str(tests_file),
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1  # because one test failed
    data = json.loads(result.output)
    assert data["total_passed"] == 1
    assert data["total_failed"] == 1


def test_validate_command_with_positional_args(sample_files, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    async def mock_run(self):
        return ValidationReport(
            test_case_id="test",
            results=[
                PromptTestResult(test_input_id="0", passed=True, errors=[]),
                PromptTestResult(test_input_id="1", passed=False, errors=["Invalid schema"]),
            ],
            total_passed=1,
            total_failed=1,
            duration_ms=100,
            metadata={},
        )

    monkeypatch.setattr(ValidationRunner, "run", mock_run)

    runner = CliRunner()
    prompt_file, schema_file, tests_file = sample_files
    result = runner.invoke(
        cli,
        [
            "validate",
            str(prompt_file),
            str(schema_file),
            str(tests_file),
            "--output-format",
            "json",
        ],
    )

    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["total_passed"] == 1
    assert data["total_failed"] == 1


def test_load_test_inputs_supports_string_array(tmp_path):
    from promptguard.utils.file_loader import load_test_inputs

    tests_file = tmp_path / "tests.json"
    tests_file.write_text(json.dumps(["Hello world", "Goodbye"]))

    test_inputs = load_test_inputs(tests_file)
    assert len(test_inputs) == 2
    assert test_inputs[0].input_data == {"input": "Hello world"}
    assert test_inputs[1].input_data == {"input": "Goodbye"}
