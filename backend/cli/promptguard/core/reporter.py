import xml.etree.ElementTree as ET
from promptguard_shared.models.result import ValidationReport


class Reporter:
    def __init__(self, report: ValidationReport, format: str):
        self.report = report
        self.format = format

    def generate(self) -> str:
        if self.format == "text":
            return self._text_report()
        elif self.format == "json":
            return self._json_report()
        elif self.format == "junit":
            return self._junit_report()
        else:
            return self._text_report()

    def _text_report(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("PROMPT GUARD VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Total tests: {len(self.report.results)}")
        lines.append(f"Passed: {self.report.total_passed}")
        lines.append(f"Failed: {self.report.total_failed}")
        lines.append(f"Duration: {self.report.duration_ms:.2f} ms")
        lines.append("-" * 60)
        for result in self.report.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"{status} | Test {result.test_input_id}")
            if not result.passed:
                for err in result.errors:
                    lines.append(f"      - {err}")
            if result.llm_latency_ms:
                lines.append(f"      Latency: {result.llm_latency_ms:.2f} ms")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _json_report(self) -> str:
        return self.report.model_dump_json(indent=2)

    def _junit_report(self) -> str:
        # Create a simple JUnit XML structure
        testsuites = ET.Element("testsuites")
        testsuite = ET.SubElement(
            testsuites,
            "testsuite",
            name="PromptGuard Validation",
            tests=str(len(self.report.results)),
            failures=str(self.report.total_failed),
            time=str(self.report.duration_ms / 1000),
        )
        for result in self.report.results:
            testcase = ET.SubElement(
                testsuite,
                "testcase",
                name=f"test_{result.test_input_id}",
                time=str((result.llm_latency_ms or 0) / 1000),
            )
            if not result.passed:
                failure = ET.SubElement(
                    testcase, "failure", message="Schema validation failed"
                )
                failure.text = "\n".join(result.errors)
        return ET.tostring(testsuites, encoding="unicode", method="xml")
