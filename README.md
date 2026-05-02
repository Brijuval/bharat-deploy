# 🇮🇳 BharatDeploy

**Multi-language DevOps CLI Agent for AWS** — Deploy to the cloud in Hindi, Hinglish, or English!

> "banao" means "create" | "hatao" means "delete" | "dikhao" means "show"

## What is BharatDeploy?

BharatDeploy is an AI-powered CLI tool that lets Indian developers interact with AWS using natural language — including Hindi, Hinglish (Roman script Hindi), Tamil, and Kannada.

Instead of memorizing complex AWS CLI commands, just say what you want:

```bash
bharat deploy "flask app banao"          # Deploy a Flask app
bharat list "EC2 instances dikhao"       # List EC2 instances  
bharat delete "purana server hatao"      # Delete an old server
bharat explain "S3 bucket kya hota hai" # Explain S3 buckets
```

## Features

- 🗣️ **Multi-language support** — Hindi, Hinglish, Tamil, Kannada, English
- 🤖 **AI-powered** — Uses Groq's LLaMA model to understand natural language
- ☁️ **AWS integration** — Generates and executes AWS CLI commands
- 🔒 **Safety first** — Confirms destructive operations, blocks dangerous commands
- 💬 **Hindi error explanations** — AWS errors explained in simple Hindi/Hinglish
- 🧪 **Well tested** — Comprehensive test suite with mocked external calls

## Quick Start

### 1. Install dependencies

```bash
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

Get a free Groq API key at: https://console.groq.com

### 3. Configure AWS

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (ap-south-1 for Mumbai)
```

### 4. Run tests

```bash
pytest tests/ -v
```

### 5. Try the demo

```bash
python demo.py
```

### 6. Use the CLI

```bash
python main.py deploy "flask app banao"
python main.py list "EC2 instances dikhao"
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `bharat deploy` | Deploy an application | `bharat deploy "app banao"` |
| `bharat list` | List AWS resources | `bharat list "servers dikhao"` |
| `bharat delete` | Delete a resource | `bharat delete "test server hatao"` |
| `bharat explain` | Explain an AWS concept | `bharat explain "Lambda kya hai"` |

## Hinglish Keywords

| Hindi Word | Meaning | Example |
|-----------|---------|---------|
| banao | create | "server banao" |
| karo | do/execute | "deploy karo" |
| hatao | delete/remove | "instance hatao" |
| dikhao | show/list | "buckets dikhao" |
| chalao | run | "script chalao" |
| shuru | start | "service shuru karo" |
| band | stop | "instance band karo" |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.

## Setup Guide

See [SETUP.md](SETUP.md) for detailed installation instructions.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for usage examples in Hindi and Hinglish.

## Project Structure

```
bharat-deploy/
├── src/
│   ├── lang_detector.py    # Language detection + Hinglish
│   ├── cli.py              # Click CLI interface
│   ├── prompt_packager.py  # Prompt formatting
│   ├── groq_handler.py     # Groq LLM integration
│   ├── action_mapper.py    # Command parsing & validation
│   ├── aws_executor.py     # AWS CLI execution
│   ├── error_explainer.py  # Error explanation in Hindi
│   └── config.py           # Configuration handler
├── tests/                  # Test suite (all mocked)
├── config/                 # Configuration templates
├── main.py                 # CLI entry point
└── demo.py                 # Working demo
```

## License

MIT License — see LICENSE file for details.