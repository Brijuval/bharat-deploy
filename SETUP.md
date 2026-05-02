# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip
- AWS CLI installed and in PATH (for real executions)
- A Groq API key (free at https://console.groq.com)

---

## Step 1 — Clone & Install

```bash
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy
pip install -r requirements.txt
```

## Step 2 — Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to **API Keys** and create a new key

## Step 3 — Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

## Step 4 — AWS Credentials (optional for dry-run)

If you want to execute real AWS commands, configure the AWS CLI:

```bash
aws configure
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region name: ap-south-1
# Default output format: json
```

## Step 5 — Configuration File (optional)

```bash
cp config/bharat.yaml.example config/bharat.yaml
# Edit config/bharat.yaml as needed
```

## Step 6 — Run Tests

```bash
pytest tests/ -v
```

All tests use mocks — no real API calls are made.

## Step 7 — Try the Demo

```bash
python demo.py
```

## Step 8 — Use the CLI

```bash
python main.py --help
python main.py deploy flask-app --dry-run
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'groq'`
```bash
pip install -r requirements.txt
```

### `GROQ_API_KEY environment variable is not set`
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### `langdetect` returns unexpected language
This can happen with very short text. Use `--language hi` to force Hindi.
