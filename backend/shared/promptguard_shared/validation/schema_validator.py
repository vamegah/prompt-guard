import json
import jsonschema
from typing import Any, Dict
from .base import ValidationResult


class SchemaValidator:
    """Validates data against a JSON schema."""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        jsonschema.Draft7Validator.check_schema(schema)
        # Optionally pre-compile schema for performance
        self._validator = jsonschema.Draft7Validator(schema)

    def validate(self, data: Any) -> ValidationResult:
        data, parse_error = self._coerce_response(data)
        if parse_error:
            return ValidationResult(passed=False, errors=[parse_error])

        errors = []
        for error in self._validator.iter_errors(data):
            errors.append(error.message)
        return ValidationResult(passed=len(errors) == 0, errors=errors)

    def _coerce_response(self, data: Any) -> tuple[Any, str | None]:
        if not isinstance(data, str):
            return data, None

        schema_type = self.schema.get("type")
        structured_types = {"object", "array", "integer", "number", "boolean", "null"}
        should_parse_json = schema_type in structured_types or data.strip().startswith(("{", "["))
        if not should_parse_json:
            return data, None

        try:
            return json.loads(data), None
        except json.JSONDecodeError as exc:
            return data, f"Response is not valid JSON: {exc.msg}"
