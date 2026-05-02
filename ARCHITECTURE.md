# Architecture

## System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (CLI)                              │
│   "banao ek EC2 instance" / "create EC2" / "नमस्ते instance"   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    src/cli.py  (Click CLI)                      │
│  Commands: deploy | list-resources | delete | show-config       │
└───────┬─────────────────────┬───────────────────────────────────┘
        │                     │
        ▼                     ▼
┌───────────────┐   ┌─────────────────────┐
│ lang_detector │   │   prompt_packager   │
│ Detect Hindi/ │   │ Format prompt for   │
│ Hinglish/EN   │   │ Groq LLaMA-3        │
└───────────────┘   └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    groq_handler     │
                    │ Call Groq API →     │
                    │ LLaMA-3.1-70B       │
                    │ Parse JSON response │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    action_mapper    │
                    │ Map AI response to  │
                    │ AWS CLI command     │
                    │ Check safety flags  │
                    └──────────┬──────────┘
                               │
                       ┌───────┴───────┐
                       │ Confirmation? │
                       └───────┬───────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    aws_executor     │
                    │ Run AWS CLI command │
                    │ dry_run supported   │
                    └──────────┬──────────┘
                               │
                   ┌───────────┴───────────┐
                   │ success?              │ error?
                   ▼                       ▼
              ✅ Output            ┌─────────────────┐
                                   │ error_explainer │
                                   │ Translate error │
                                   │ to Hindi        │
                                   └─────────────────┘
```

## Data Flow

1. **User** enters a command (Hindi / Hinglish / English)
2. **LanguageDetector** identifies the language and Hinglish keywords
3. **PromptPackager** wraps the input into a structured Groq prompt
4. **GroqHandler** sends the prompt to LLaMA-3.1-70B via Groq API and returns JSON
5. **ActionMapper** parses the JSON, flags destructive operations and low-confidence actions
6. **CLI** asks for confirmation when required
7. **AWSExecutor** runs the AWS CLI command (or previews it in dry-run mode)
8. **ErrorExplainer** translates any AWS errors into Hindi

## Component Descriptions

### `src/lang_detector.py`
Uses the `langdetect` library for probabilistic language identification. A curated list of Hinglish keywords (Roman-script Hindi words) is checked first to catch mixed-language inputs that `langdetect` might misclassify.

### `src/cli.py`
Built with [Click](https://click.palletsprojects.com/). Provides four subcommands: `deploy`, `list-resources`, `delete`, and `show-config`. Each command loads the `.env` file, detects language, packages the prompt, calls Groq, maps the action, and executes.

### `src/prompt_packager.py`
Formats user input into structured prompts that instruct LLaMA-3 to respond with a specific JSON schema. Separate methods for deploy, list, and delete ensure the model receives the most relevant context.

### `src/groq_handler.py`
Thin wrapper around the official `groq` Python SDK. Uses `response_format: json_object` to guarantee valid JSON output from the model.

### `src/action_mapper.py`
Parses the Groq JSON response and adds safety metadata. Marks operations as destructive if the action contains words like "delete", "terminate", "destroy", or "remove". Any operation with confidence < 0.75 also requires confirmation.

### `src/aws_executor.py`
Uses `subprocess.run` with `shell=True` to execute AWS CLI commands. The `dry_run` flag prevents execution and returns a preview message instead.

### `src/error_explainer.py`
Maps known AWS error codes to human-readable Hindi explanations. Falls back to the raw error string for unknown codes.

### `src/config.py`
Reads `config/bharat.yaml` using PyYAML. Falls back to safe defaults (Mumbai region, t3.micro) when the file is absent.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Groq over OpenAI | 10-100× faster inference, free tier available |
| LLaMA-3.1-70B | Excellent multilingual understanding including Hindi |
| `response_format: json_object` | Eliminates JSON parsing failures |
| Confirmation for confidence < 0.75 | Prevents unintended actions from ambiguous input |
| `subprocess.run` with shell=True | Simplest way to delegate to AWS CLI; consider boto3 for production |
| ap-south-1 default | Lowest latency for Indian developers |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| AWS credentials in environment | `.gitignore` excludes `.env`; `.env.example` provided |
| Destructive commands run accidentally | Mandatory confirmation prompt |
| Groq API key exposed | Loaded from environment only; never hard-coded |
| `shell=True` injection | Commands come from LLaMA output, not raw user input |
