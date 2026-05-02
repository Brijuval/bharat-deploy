# BharatDeploy 🇮🇳

> **AWS Deployment in Hindi** — Deploy cloud infrastructure using natural language commands in Hindi or Hinglish.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is BharatDeploy?

BharatDeploy is a multi-language DevOps CLI agent that lets Indian developers deploy AWS infrastructure using **Hindi** or **Hinglish** (Roman-script Hindi) commands. Under the hood it uses [Groq](https://console.groq.com) (LLaMA) to translate natural-language requests into safe, validated AWS CLI commands.

```
$ bharat deploy "Flask app ke liye EC2 instance banao"

🔍 Detected language: hinglish (confidence: 0.85)
🤖 Processing with AI...

📝 Flask application ke liye ek naya EC2 instance banaya jaayega.
   A new EC2 instance will be created for the Flask application.

💻 Command: aws ec2 run-instances --image-id ami-0abcdef1234567890 \
            --instance-type t3.micro --region ap-south-1

क्या आप आगे बढ़ना चाहते हैं? (Continue?) [y/N]: y
✅ Success!
```

---

## Features

- 🗣️ **Hindi + Hinglish** — Speak in whichever language feels natural
- 🤖 **AI-powered** — Groq LLaMA translates intent to CLI commands
- 🛡️ **Safety-first** — Destructive operations always require confirmation
- 🌏 **India-centric defaults** — `ap-south-1` (Mumbai) region by default
- 🔍 **Error Explainer** — AWS errors explained in Hindi with next steps
- 🧪 **Fully tested** — All tests run with mocks (no real cloud calls needed)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env — add GROQ_API_KEY and AWS credentials

# 4. Run
python main.py deploy "Meri S3 bucket dikhao"
```

See [SETUP.md](SETUP.md) for detailed instructions.

---

## Supported Commands

| Subcommand | Example |
|-----------|---------|
| `deploy`  | `bharat deploy "EC2 instance banao"` |
| `list`    | `bharat list "Saari S3 buckets dikhao"` |
| `delete`  | `bharat delete "test-bucket delete karo"` |
| `explain` | `bharat explain "AccessDenied: ec2:RunInstances"` |

---

## Project Structure

```
bharat-deploy/
├── src/
│   ├── __init__.py
│   ├── cli.py             # Click CLI entry point
│   ├── lang_detector.py   # Hindi / Hinglish detection
│   ├── prompt_packager.py # Prompt formatting
│   ├── groq_handler.py    # Groq LLM integration
│   ├── action_mapper.py   # JSON → AWS CLI mapping
│   ├── aws_executor.py    # Safe command execution
│   ├── error_explainer.py # Error explanation in Hindi
│   └── config.py          # Configuration management
├── tests/
│   ├── test_lang_detector.py
│   ├── test_groq_handler.py
│   ├── test_action_mapper.py
│   ├── test_aws_executor.py
│   └── test_config.py
├── config/
│   └── bharat.yaml.example
├── demo.py
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

## Documentation

- [SETUP.md](SETUP.md) — Installation and configuration guide
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and data flow
- [EXAMPLES.md](EXAMPLES.md) — Usage examples in Hindi and Hinglish

---

## License

MIT © Brijuval