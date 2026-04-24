import asyncio
import click
from pathlib import Path

from promptguard.utils.env import get_api_key
from promptguard.utils.file_loader import load_prompt, load_schema, load_test_inputs
from promptguard.core.runner import ValidationRunner
from promptguard.core.reporter import Reporter


@click.group()
def cli():
    """PromptGuard CLI - Validate LLM prompts against schemas."""
    pass


@cli.command()
@click.argument("prompt", required=False, type=click.Path(exists=True, dir_okay=False))
@click.argument("schema", required=False, type=click.Path(exists=True, dir_okay=False))
@click.argument("tests", required=False, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--prompt",
    "-p",
    "prompt_opt",
    type=click.Path(exists=True, dir_okay=False),
    help="Prompt template file",
)
@click.option(
    "--schema",
    "-s",
    "schema_opt",
    type=click.Path(exists=True, dir_okay=False),
    help="JSON schema file",
)
@click.option(
    "--tests",
    "-t",
    "tests_opt",
    type=click.Path(exists=True, dir_okay=False),
    help="Test inputs file (JSON array of objects or strings)",
)
@click.option(
    "--provider",
    default="openai",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    help="LLM provider",
)
@click.option("--model", help="Model name (e.g., gpt-4, claude-3-opus)")
@click.option(
    "--output-format",
    "-o",
    default="text",
    type=click.Choice(["text", "json", "junit"], case_sensitive=False),
    help="Output format",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate(prompt, schema, tests, prompt_opt, schema_opt, tests_opt, provider, model, output_format, verbose):
    """Run validation tests.
    
    Usage:
      promptguard validate prompt.txt schema.json tests.json
      promptguard validate --prompt prompt.txt --schema schema.json --tests tests.json
    """
    # Support both positional and named arguments
    prompt_value = prompt_opt or prompt
    schema_value = schema_opt or schema
    tests_value = tests_opt or tests or "tests.json"

    if not prompt_value:
        raise click.ClickException(
            "Prompt template path is required. Provide it as a positional argument or with --prompt."
        )
    if not schema_value:
        raise click.ClickException(
            "JSON schema path is required. Provide it as a positional argument or with --schema."
        )

    # Load files
    prompt_template = load_prompt(Path(prompt_value))
    schema_dict = load_schema(Path(schema_value))
    test_inputs = load_test_inputs(Path(tests_value))

    # Get API key
    api_key = get_api_key(provider)
    if not api_key:
        raise click.ClickException(
            f"API key for {provider} not found. Set {provider.upper()}_API_KEY environment variable."
        )

    # Create runner
    runner = ValidationRunner(
        provider=provider,
        api_key=api_key,
        model=model,
        prompt_template=prompt_template,
        schema_dict=schema_dict,
        test_inputs=test_inputs,
        verbose=verbose,
    )

    # Run tests asynchronously
    try:
        report = asyncio.run(runner.run())
    except Exception as e:
        raise click.ClickException(f"Error during validation: {e}")

    # Output report
    reporter = Reporter(report, output_format)
    output = reporter.generate()
    click.echo(output)

    # Exit with non-zero if any test failed
    if report.total_failed > 0:
        ctx = click.get_current_context()
        ctx.exit(1)


if __name__ == "__main__":
    cli()
