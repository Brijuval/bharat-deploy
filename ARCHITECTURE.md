# BharatDeploy Architecture

## System Overview

BharatDeploy follows a pipeline architecture where user input (in any Indian language) flows through several processing stages before resulting in AWS CLI command execution.

```
User Input (Hindi/Hinglish/Tamil/Kannada/English)
         │
         ▼
┌─────────────────┐
│ Language        │  Detect language, identify Hinglish keywords
│ Detector        │  Returns: language code + confidence score
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt          │  Format input + language into structured prompt
│ Packager        │  Adds action-specific instructions for LLM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Groq Handler    │  Send prompt to LLaMA via Groq API
│                 │  response_format: json_object enforced
│                 │  Retry logic with exponential backoff
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Action Mapper   │  Parse JSON → validate → AWS CLI commands
│                 │  Safety checks, injection prevention
│                 │  Destructive operation detection
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AWS Executor    │  Execute validated AWS CLI commands
│                 │  Capture output/errors
│                 │  Support dry-run mode
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
Success    Failure
    │         │
    ▼         ▼
Display   Error
Output   Explainer (Hindi)
```

## Module Descriptions

### 1. Language Detector (`src/lang_detector.py`)

Detects the language of user input using two approaches:

**Script-based detection (fast, high accuracy):**
- Devanagari Unicode range (0x0900-0x097F) → Hindi
- Tamil Unicode range (0x0B80-0x0BFF) → Tamil
- Kannada Unicode range (0x0C80-0x0CFF) → Kannada

**Keyword-based Hinglish detection:**
- Checks for Roman-script Hindi words: "banao", "karo", "hatao", etc.
- Calculates keyword density for confidence score
- Falls back to `langdetect` library for other cases

### 2. Prompt Packager (`src/prompt_packager.py`)

Creates structured prompts for the LLM:
- Action-specific system prompts (deploy/list/delete/explain)
- Language-specific instructions added to system prompt
- AWS context injected (region, existing resources)
- Always instructs LLM to return valid JSON only

### 3. Groq Handler (`src/groq_handler.py`)

Manages all Groq API interactions:
- Uses `response_format: {"type": "json_object"}` to enforce JSON output
- Implements exponential backoff retry logic
- Parses and validates JSON responses
- Handles rate limiting gracefully

### 4. Action Mapper (`src/action_mapper.py`)

Validates and maps LLM output to executable commands:
- Validates AWS CLI command structure
- Prevents shell injection (blocks `;`, `&&`, `|`, backticks, etc.)
- Validates AWS service against allowlist
- Detects destructive operations for safety confirmation
- Generates bash scripts for complex operations

**Security Model:**
```
Allowed services: ec2, s3, rds, lambda, ecs, eks, iam,
                  cloudformation, dynamodb, route53, etc.

Blocked patterns: ; && || ` $( | > <

Always blocked: aws iam delete-user
                aws iam delete-role
                aws s3 rb --force
```

### 5. AWS Executor (`src/aws_executor.py`)

Executes validated commands safely:
- Runs commands via `subprocess.run`
- Captures stdout/stderr
- Handles timeouts gracefully
- Stops execution on first failure (unless dry-run)
- Injects `--region` flag if configured

### 6. Error Explainer (`src/error_explainer.py`)

Maps AWS error codes to beginner-friendly Hindi explanations:
- Pattern matching against common AWS error codes
- Provides step-by-step fix instructions in Hindi/Hinglish
- Links to relevant AWS documentation

### 7. Config Handler (`src/config.py`)

Layered configuration system (priority: env vars > yaml > defaults):
```
1. Defaults (hardcoded in config.py)
2. bharat.yaml (user config file)
3. Environment variables (highest priority)
```

### 8. CLI (`src/cli.py`)

Click-based command-line interface:
- Commands: deploy, list, delete, explain
- `--language` override flag
- `--dry-run` mode
- `--verbose` for debugging
- Integrates all modules in the pipeline

## Data Flow Example

Input: `"flask app banao"`

1. **Language Detector** → `{language: "hinglish", confidence: 0.8, keywords: ["banao"]}`
2. **Prompt Packager** → Creates system prompt with deploy action + Hinglish instructions
3. **Groq Handler** → Returns `{action: "deploy", resource_type: "ec2", aws_commands: [...]}`
4. **Action Mapper** → Validates commands, detects non-destructive
5. **User confirms** → Yes
6. **AWS Executor** → Runs `aws ec2 run-instances ...`
7. **Display** → Shows success output

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| CLI Framework | Click 8.x |
| LLM Provider | Groq (LLaMA 3) |
| Language Detection | langdetect + custom script detection |
| Config | PyYAML + python-dotenv |
| Testing | pytest + unittest.mock |
| Cloud | AWS CLI |
