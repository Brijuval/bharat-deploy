# BharatDeploy Setup Guide

Complete installation and configuration guide for BharatDeploy.

## Prerequisites

- Python 3.9 or higher
- AWS CLI installed and configured
- Groq API key (free at https://console.groq.com)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Brijuval/bharat-deploy.git
cd bharat-deploy
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
# OR
venv\Scripts\activate       # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required: Groq API Key
GROQ_API_KEY=gsk_your_key_here

# AWS Region (Mumbai recommended for India)
AWS_DEFAULT_REGION=ap-south-1
```

### Step 5: Configure AWS

```bash
aws configure
```

Enter when prompted:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region: `ap-south-1` (Mumbai)
- Default output format: `json`

### Step 6: Verify Setup

```bash
# Test language detection (no API key needed)
pytest tests/test_lang_detector.py -v

# Run all tests
pytest tests/ -v

# Try the demo
python demo.py
```

## Configuration File (Optional)

Create a `bharat.yaml` for advanced settings:

```bash
cp config/bharat.yaml.example bharat.yaml
```

See `config/bharat.yaml.example` for all available options.

## Groq API Key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Create an API key
4. Add it to your `.env` file:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

## Troubleshooting

### "GROQ_API_KEY not set" Error

Make sure `.env` file exists with your API key:
```bash
cat .env | grep GROQ_API_KEY
```

### "AWS credentials not configured" Error

Run `aws configure` and enter your credentials.

### Language Not Detected Correctly

Use the `--language` flag to override:
```bash
python main.py deploy "my app" --language hi
python main.py list --language en
```

### Command Times Out

Increase timeout in `bharat.yaml`:
```yaml
aws:
  timeout: 60
```

### Import Errors

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_lang_detector.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Development Setup

For development, install dev dependencies:

```bash
pip install -e ".[dev]"
```
