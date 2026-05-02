# Setup Guide — BharatDeploy

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9+ | `python --version` |
| pip | 22+ | `pip --version` |
| AWS CLI | v2 | [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |
| Groq API Key | — | Free at [console.groq.com](https://console.groq.com) |

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy
```

---

## Step 2 — Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

---

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```dotenv
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=ap-south-1
```

> **Never commit `.env` to git.** It is already listed in `.gitignore`.

---

## Step 5 — Configure AWS CLI (alternative)

If you prefer, configure AWS credentials using the standard AWS CLI tool:

```bash
aws configure
```

---

## Step 6 — Verify installation

```bash
# Run tests (no real API calls)
pytest tests/ -v

# Run the demo (requires GROQ_API_KEY)
python demo.py

# Try the CLI
python main.py --help
python main.py deploy "EC2 instance dikhao" --dry-run
```

---

## Optional: Install as a CLI tool

```bash
pip install -e .
bharat --help
```

---

## Configuration File (optional)

Copy and edit `config/bharat.yaml.example`:

```bash
cp config/bharat.yaml.example config/bharat.yaml
```

Then edit `config/bharat.yaml` with your preferred defaults.
The YAML file is loaded automatically if present.

---

## Troubleshooting

### `groq` package not found
```bash
pip install groq
```

### AWS CLI not found
Download from [aws.amazon.com/cli](https://aws.amazon.com/cli/).

### `GROQ_API_KEY` not set
Make sure `.env` exists and contains `GROQ_API_KEY=gsk_...`.

### Tests failing
```bash
pip install pytest pytest-mock
pytest tests/ -v
```
