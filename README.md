# PromptGuard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/promptguard/promptguard/actions/workflows/ci.yml/badge.svg)](https://github.com/promptguard/promptguard/actions/workflows/ci.yml)

**PromptGuard** is an enterprise-grade platform for validating LLM prompts against JSON schemas. It helps teams ensure reliable, structured outputs from language models by integrating validation into CI/CD pipelines and providing a collaborative dashboard.

## Features

- ✅ CLI tool for local validation and CI integration (GitHub Action included)
- ✅ Centralized management of prompts, schemas, and test suites
- ✅ Support for multiple LLM providers (OpenAI, Anthropic, more to come)
- ✅ Schema validation with detailed reporting
- ✅ Async validation engine for scalability
- ✅ Analytics and metrics on validation runs
- ✅ React-based dashboard for team collaboration

## Quick Start

1. **Clone the repo**: `git clone https://github.com/promptguard/promptguard.git`
2. **Run bootstrap script**: `./scripts/bootstrap.sh`
3. **Start services**: `cd backend && docker-compose up -d`
4. **Access dashboard**: `http://localhost:3000`
5. **Use CLI**: `cd backend/cli && promptguard validate prompt.txt schema.json tests.json`

6. **Use GitHub Action**: see `.github/workflows/promptguard-pr-validation.yml` for PR validation and comment reporting.

## Documentation

Full documentation is available in the [docs](docs/) folder:
- [Architecture Overview](docs/architecture.md)
- [API Specification](docs/api-spec.yaml)
- [Getting Started Guide](docs/guides/getting-started.md)
- [Deployment Guide](docs/guides/deployment.md)

## Contributing

Please see [CONTRIBUTING.md](docs/guides/contributing.md) for guidelines.

## License
MIT License

Copyright (c) 2024 PromptGuard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

PromptGuard is open-source software licensed under the [MIT license](LICENSE).