import asyncio
import time
from typing import List, Dict, Any, Optional

from promptguard_shared.models.prompt import PromptTemplate
from promptguard_shared.models.test import TestInput
from promptguard_shared.models.result import PromptTestResult, ValidationReport
from promptguard_shared.validation.schema_validator import SchemaValidator
from promptguard_shared.llm import OpenAIClient, AnthropicClient, LLMClient


class ValidationRunner:
    def __init__(
        self,
        provider: str,
        api_key: str,
        prompt_template: PromptTemplate,
        schema_dict: Dict[str, Any],
        test_inputs: List[TestInput],
        model: Optional[str] = None,
        verbose: bool = False,
    ):
        self.provider = provider
        self.api_key = api_key
        self.prompt_template = prompt_template
        self.schema_dict = schema_dict
        self.test_inputs = test_inputs
        self.model = model
        self.verbose = verbose

        self.llm_client = self._create_llm_client()
        self.validator = SchemaValidator(schema_dict)

    def _create_llm_client(self) -> LLMClient:
        if self.provider == "openai":
            return OpenAIClient(api_key=self.api_key, model=self.model or "gpt-4")
        elif self.provider == "anthropic":
            return AnthropicClient(
                api_key=self.api_key, model=self.model or "claude-3-opus-20240229"
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def run(self) -> ValidationReport:
        start_time = time.time()
        run_id = f"cli-run-{int(start_time * 1000)}"
        tasks = [self._run_single_test(test_input) for test_input in self.test_inputs]
        results = await asyncio.gather(*tasks)
        duration_ms = (time.time() - start_time) * 1000

        total_passed = sum(1 for r in results if r.passed)
        total_failed = len(results) - total_passed

        return ValidationReport(
            test_case_id=run_id,
            results=results,
            total_passed=total_passed,
            total_failed=total_failed,
            duration_ms=duration_ms,
            metadata={"provider": self.provider, "model": self.model, "run_id": run_id},
        )

    async def _run_single_test(self, test_input: TestInput) -> PromptTestResult:
        if self.verbose:
            print(f"Running test {test_input.id}...")
        # Render prompt
        prompt = self.prompt_template.render(**test_input.input_data)

        # Call LLM
        llm_start = time.time()
        try:
            response = await self.llm_client.generate(prompt)
        except Exception as e:
            return PromptTestResult(
                test_input_id=test_input.id,
                passed=False,
                errors=[f"LLM call failed: {str(e)}"],
                llm_latency_ms=(time.time() - llm_start) * 1000,
                llm_cost=0.0,
            )
        llm_latency = (time.time() - llm_start) * 1000

        response_text = getattr(response, "text", response)

        # Validate against schema
        validation_result = self.validator.validate(response_text)
        # For now, we only check schema; later we could add semantic checks.

        return PromptTestResult(
            test_input_id=test_input.id,
            passed=validation_result.passed,
            errors=validation_result.errors,
            llm_response=response_text,
            llm_latency_ms=llm_latency,
            llm_cost=self.llm_client.get_cost(response),
        )
