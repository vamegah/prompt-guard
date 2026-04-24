import jsonschema
from typing import Any, Dict
from .base import ValidationResult


class SchemaValidator:
    """Validates data against a JSON schema."""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        # Optionally pre-compile schema for performance
        self._validator = jsonschema.Draft7Validator(schema)

    def validate(self, data: Any) -> ValidationResult:
        errors = []
        for error in self._validator.iter_errors(data):
            errors.append(error.message)
        return ValidationResult(passed=len(errors) == 0, errors=errors)
