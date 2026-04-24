# PromptGuard CLI

A command-line tool to validate LLM prompts against JSON schemas.

## Installation

```bash
pip install promptguard-cli

git clone https://github.com/yourorg/promptguard
cd promptguard/backend/cli
pip install -e .

export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...

promptguard validate prompt.txt schema.json tests.json
```

## Usage

The CLI supports positional arguments and optional flags.

```bash
promptguard validate prompt.txt schema.json tests.json
```

If the tests file is omitted, the CLI will look for `tests.json` in the current working directory.

You can also use named flags:

```bash
promptguard validate --prompt prompt.txt --schema schema.json --tests tests.json
```

Options:

--prompt, -p: Path to prompt template file (supports {{placeholder}}).

--schema, -s: Path to JSON schema file.

--tests, -t: Path to JSON file containing an array of test input objects.

--provider: LLM provider (openai or anthropic, default: openai).

--model: Model name (e.g., gpt-4, claude-3-opus). If not specified, a default is used.

--output-format, -o: Output format (text, json, junit).

--verbose, -v: Show detailed output.

Exit Codes

0: All tests passed.

1: One or more tests failed.