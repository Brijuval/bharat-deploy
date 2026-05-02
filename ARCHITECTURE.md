# Architecture — BharatDeploy

## Overview

BharatDeploy follows a simple **pipeline architecture** where each stage has a single responsibility:

```
User Input (Hindi / Hinglish / English)
        │
        ▼
┌───────────────────┐
│  LangDetector     │  Detect language + Hinglish flag
└────────┬──────────┘
         │ {language, confidence, is_hinglish}
         ▼
┌───────────────────┐
│  PromptPackager   │  Format system + user prompts
└────────┬──────────┘
         │ {system, user}
         ▼
┌───────────────────┐
│  GroqHandler      │  Send to LLaMA via Groq API
└────────┬──────────┘
         │ JSON response
         ▼
┌───────────────────┐
│  ActionMapper     │  Validate & map to AWS CLI command
└────────┬──────────┘
         │ {aws_cli_command, bash_script, ...}
         ▼
┌───────────────────┐
│  AWSExecutor      │  Execute the command safely
└────────┬──────────┘
         │ {success, stdout, stderr}
         ▼
     CLI Output
  (or ErrorExplainer)
```

---

## Module Descriptions

### `src/lang_detector.py`

Detects whether the user wrote in:
- **Hindi** (Devanagari script) — detected via Unicode range `\u0900-\u097F`
- **Hinglish** (Roman-script Hindi) — detected via a keyword list (`banao`, `karo`, `hatao`, ...)
- **English** — fallback via `langdetect` library

Returns: `{"language": "hi"|"en"|"hinglish", "confidence": float, "is_hinglish": bool}`

### `src/prompt_packager.py`

Constructs the system and user messages for the LLM:
- System prompt defines the JSON response schema and safety rules
- User message appends a language hint so the LLM knows what language to use in explanations
- Optional context (AWS region, account ID) is included

### `src/groq_handler.py`

- Uses the official `groq` Python SDK
- Enforces `response_format: {"type": "json_object"}` so responses are always parseable
- Implements exponential-backoff retry (configurable)
- Does NOT retry on authentication errors

### `src/action_mapper.py`

Validates the LLM JSON response before creating any AWS command:
1. Schema check — `aws_cli_command` must be present
2. Safety check — command must start with `aws`
3. Allow-list — service must be in the approved list
4. Injection guard — blocks `;`, `&&`, `|`, `` ` ``, `$(`, `${`
5. Destructiveness re-evaluation — catches cases where the LLM missed destructive patterns

### `src/aws_executor.py`

- Runs the validated command via `subprocess.run`
- Supports **dry-run mode** (logs the command but never executes it)
- Captures stdout, stderr, and exit code
- Raises `AWSExecutorError` on timeout, missing CLI, or rejected commands

### `src/error_explainer.py`

Maps well-known AWS error patterns (regex) to:
- A plain Hindi explanation
- An English explanation
- A suggested fix in Hindi

### `src/config.py`

Loads settings in priority order:
1. Environment variables (highest)
2. YAML config file (`config/bharat.yaml`)
3. Built-in defaults (lowest)

### `src/cli.py`

Click command group with four subcommands:
- `deploy` — deploy a resource
- `list` — list existing resources
- `delete` — delete a resource (always confirms)
- `explain` — explain an error in Hindi

---

## Data Flow Example

```
Input: "ek EC2 instance banao"

LangDetector → {language: "hinglish", confidence: 0.75, is_hinglish: true}

PromptPackager →
  system: "You are BharatDeploy ... respond with JSON ..."
  user:   "Hinglish detected. User request: ek EC2 instance banao\nAWS Region: ap-south-1"

GroqHandler →
  {
    "action": "ec2_create_instance",
    "aws_cli_command": "aws ec2 run-instances --image-id ami-... --instance-type t3.micro",
    "is_destructive": false,
    "explanation_hi": "एक नई EC2 instance बनाई जाएगी।",
    "confidence": 0.92
  }

ActionMapper →
  validates, adds bash_script wrapper → passes through

AWSExecutor →
  runs: aws ec2 run-instances ...
  returns: {success: true, stdout: "{...}", exit_code: 0}
```

---

## Security Considerations

- **No shell=True** — `subprocess.run` always receives a list of tokens
- **Command allow-list** — only approved AWS services are permitted
- **Injection guards** — shell metacharacters are blocked
- **Secrets** — API keys/credentials are loaded only from `.env` / environment, never hardcoded
- **Destructive confirmation** — `delete`, `terminate`, `remove` always ask for confirmation
