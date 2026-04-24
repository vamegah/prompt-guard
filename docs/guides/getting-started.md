# Getting Started with PromptGuard

## Installation

### CLI
```bash
pip install promptguard-cli
```

### From Source
```bash
git clone https://github.com/yourusername/promptguard.git
cd promptguard/backend/cli
pip install -e .
```

## Basic Usage

### Create a prompt file
```
# prompt.txt
You are a helpful assistant. Answer the following question: {{input}}
```

### Create a schema
```json
{
  "type": "string"
}
```

### Create a tests file
```json
[
  "What is the capital of France?",
  "Translate hello to Spanish."
]
```

### Validate
```bash
promptguard validate prompt.txt schema.json tests.json
```

The CLI also supports named flags:

```bash
promptguard validate --prompt prompt.txt --schema schema.json --tests tests.json
```

If the tests file is omitted, PromptGuard will look for `tests.json` in the current working directory.
