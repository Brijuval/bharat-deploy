# Examples — BharatDeploy

A collection of real-world commands you can use with BharatDeploy.

---

## EC2 (Virtual Machines)

### Create an instance

```bash
# Hinglish
bharat deploy "Flask app ke liye EC2 instance banao"

# Hindi (Devanagari)
bharat deploy "नया EC2 instance बनाओ"

# English
bharat deploy "Create an EC2 t3.micro instance for my Flask app"
```

### List instances

```bash
bharat list "Meri saari EC2 instances dikhao"
bharat list "सभी running instances दिखाओ"
```

### Stop an instance

```bash
bharat deploy "i-1234567890abcdef0 instance band karo"
```

### Terminate an instance

```bash
# Requires confirmation (destructive)
bharat delete "i-1234567890abcdef0 instance delete karo"
```

---

## S3 (Object Storage)

### Create a bucket

```bash
bharat deploy "my-new-bucket naam ka S3 bucket banao"
bharat deploy "नया S3 bucket बनाओ my-app-data"
```

### List buckets

```bash
bharat list "Saari S3 buckets dikhao"
bharat list "मेरी सभी S3 buckets की list दिखाओ"
```

### Upload a file

```bash
bharat deploy "report.pdf file my-bucket mein upload karo"
```

### Delete a bucket

```bash
# Requires confirmation (destructive)
bharat delete "test-bucket S3 bucket delete karo"
```

---

## RDS (Databases)

### Create a database

```bash
bharat deploy "MySQL database banao production ke liye"
bharat deploy "MySQL RDS instance banao -- instance type db.t3.micro"
```

### List databases

```bash
bharat list "Saare RDS databases dikhao"
```

---

## Lambda (Serverless)

### List functions

```bash
bharat list "Saari Lambda functions dikhao"
```

### Invoke a function

```bash
bharat deploy "process-orders Lambda function invoke karo"
```

---

## Error Explanation

### Explain an access error

```bash
bharat explain "AccessDenied: User is not authorized to perform: ec2:RunInstances"
```

Output:
```
📖 Hindi: आपके पास इस ऑपरेशन की अनुमति नहीं है।
📖 English: You don't have permission for this operation.
💡 Suggestion: अपने IAM permissions चेक करें या admin से मदद लें।
```

### Explain a credentials error

```bash
bharat explain "Unable to locate credentials"
```

Output:
```
📖 Hindi: AWS credentials नहीं मिले।
📖 English: No AWS credentials found.
💡 Suggestion: `aws configure` चलाएं या .env में credentials सेट करें।
```

---

## CLI Flags

### Dry run (preview without executing)

```bash
bharat --dry-run deploy "EC2 instance banao"
```

### Force a specific language

```bash
bharat --language hi deploy "नया server बनाओ"
bharat --language en list "show all instances"
```

### Skip confirmation for destructive operations

```bash
bharat delete --yes "test-bucket delete karo"
```

### Use a custom config file

```bash
bharat --config-file /path/to/bharat.yaml deploy "EC2 banao"
```

---

## Programmatic Usage

```python
from src.lang_detector import detect_language
from src.error_explainer import ErrorExplainer

# Language detection
result = detect_language("EC2 instance banao")
print(result)
# {'language': 'hinglish', 'confidence': 0.75, 'is_hinglish': True}

# Error explanation
explainer = ErrorExplainer()
exp = explainer.explain("AccessDenied: ec2:RunInstances")
print(exp["explanation_hi"])  # "आपके पास इस ऑपरेशन की अनुमति नहीं है।"
print(exp["suggestion_hi"])   # "अपने IAM permissions चेक करें..."
```
