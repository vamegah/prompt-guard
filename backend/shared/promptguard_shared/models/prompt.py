import re
from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Any


class PromptTemplate(BaseModel):
    """Represents a prompt template with placeholders."""

    id: Optional[str] = None
    name: str
    template: str  # e.g., "Translate this to French: {{input}}"
    placeholders: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    version: str = "1.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_placeholders_from_template(cls, values):
        """Automatically derive placeholders from the template."""
        template = values.template
        if template:
            # Find all unique placeholders like {{placeholder}}
            found_placeholders = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template)
            values.placeholders = sorted(list(set(found_placeholders)))
        return values

    def render(self, **kwargs) -> str:
        """Renders the template by replacing placeholders with provided values."""
        # A more robust implementation than simple string replacement to avoid partial matches.
        # For more complex needs, a full templating engine like Jinja2 would be the next step.
        return re.sub(
            r"\{\{([a-zA-Z0-9_]+)\}\}",
            lambda m: str(kwargs.get(m.group(1), m.group(0))),
            self.template,
        )
