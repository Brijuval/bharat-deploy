# BharatDeploy 🇮🇳

> **Multi-language DevOps CLI Agent for AWS** — deploy infrastructure using natural language commands in Hindi, Hinglish, or English.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🗣️ **Hindi & Hinglish support** — type commands like `banao ek instance` or `hatao yeh server`
- 🤖 **LLaMA-3 powered** — uses Groq's ultra-fast inference to understand your intent
- 🛡️ **Safety first** — destructive operations always require confirmation
- 🌏 **India region default** — `ap-south-1` (Mumbai) out of the box
- 🔍 **Error explanation in Hindi** — AWS errors translated for you
- 🧪 **Fully mocked tests** — no real API calls needed to run the test suite

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Run the demo (no API key needed)
python demo.py

# 5. Try the CLI
python main.py deploy flask-app --language hi
```

---

## 📦 Modules

| Module | File | Description |
|--------|------|-------------|
| Language Detector | `src/lang_detector.py` | Detects Hindi, English, and Hinglish |
| CLI | `src/cli.py` | Click-based CLI with `deploy`, `list-resources`, `delete` |
| Prompt Packager | `src/prompt_packager.py` | Formats prompts for Groq |
| Groq Handler | `src/groq_handler.py` | LLaMA-3 integration via Groq API |
| Action Mapper | `src/action_mapper.py` | Maps AI response to AWS actions |
| AWS Executor | `src/aws_executor.py` | Executes AWS CLI commands safely |
| Error Explainer | `src/error_explainer.py` | Explains errors in Hindi |
| Config Handler | `src/config.py` | Loads YAML configuration |

---

## 🖥️ CLI Commands

```bash
# Deploy an application
python main.py deploy flask-app
python main.py deploy flask-app --language hi
python main.py deploy flask-app --dry-run

# List resources
python main.py list-resources
python main.py list-resources --language hi

# Delete a resource
python main.py delete i-1234567890abcdef0

# Show current configuration
python main.py show-config
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src

# Run a specific test file
pytest tests/test_lang_detector.py -v
```

---

## 🌐 Supported Languages

| Language | Script | Example |
|----------|--------|---------|
| Hindi | Devanagari | `नमस्ते, मुझे एक instance चाहिए` |
| Hinglish | Roman | `banao ek flask app` |
| English | Latin | `create a new EC2 instance` |

---

## 📚 Documentation

- [SETUP.md](SETUP.md) — Installation guide
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design
- [EXAMPLES.md](EXAMPLES.md) — Usage examples in Hindi & Hinglish

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest tests/ -v`
5. Open a pull request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.