# BharatDeploy Usage Examples

Examples in Hindi, Hinglish, and English for common AWS operations.

---

## Deploy Commands

### Flask App deploy karna

```bash
# Hinglish
bharat deploy "flask app banao"
bharat deploy "nayi Flask application deploy karo EC2 pe"

# Hindi
bharat deploy "Flask application chalao"

# English
bharat deploy "create a Flask application on EC2"
```

### Lambda Function

```bash
# Hinglish
bharat deploy "Lambda function banao mere Python code ke liye"
bharat deploy "serverless function create karo"

# English  
bharat deploy "create a Lambda function for Python"
```

### S3 Bucket

```bash
# Hinglish
bharat deploy "S3 bucket banao meri files ke liye"
bharat deploy "storage bucket create karo 'my-app-bucket' naam se"

# English
bharat deploy "create an S3 bucket called my-app-bucket"
```

### RDS Database

```bash
# Hinglish
bharat deploy "MySQL database banao production ke liye"
bharat deploy "RDS instance create karo"

# English
bharat deploy "create a MySQL RDS instance"
```

---

## List Commands

### Saare resources dikhao

```bash
# Hinglish
bharat list
bharat list "saare EC2 instances dikhao"
bharat list "meri running instances dikhao"

# Hindi
bharat list "सभी EC2 instances दिखाओ"

# English
bharat list "show all EC2 instances"
```

### S3 Buckets

```bash
# Hinglish
bharat list "mere saare S3 buckets dikhao"
bharat list "S3 buckets ki list do"

# English
bharat list "list all my S3 buckets"
```

### Lambda Functions

```bash
# Hinglish
bharat list "Lambda functions dikhao"

# English
bharat list "show Lambda functions"
```

---

## Delete Commands

> ⚠️ Delete commands will ask for confirmation before executing!

### EC2 Instance Delete

```bash
# Hinglish
bharat delete "purana EC2 instance hatao"
bharat delete "test server hatao i-1234567890abcdef0"

# Hindi
bharat delete "पुराना instance हटाओ"

# English
bharat delete "delete the old EC2 instance"
```

### S3 Bucket

```bash
# Hinglish (use --force to skip confirmation)
bharat delete "test bucket hatao"

# English
bharat delete "remove the test-bucket S3 bucket"
```

---

## Explain Commands

### AWS Concepts samajhna

```bash
# Hinglish
bharat explain "S3 bucket kya hota hai"
bharat explain "EC2 aur Lambda mein kya fark hai"
bharat explain "VPC kya hai simple language mein"
bharat explain "AWS Lambda ke bare mein batao"

# Hindi
bharat explain "AWS क्या है समझाओ"
bharat explain "Cloud computing kya hai"

# English
bharat explain "what is an EC2 instance"
bharat explain "difference between S3 and EBS"
```

---

## Using Language Override Flag

```bash
# Force Hindi
bharat deploy "flask app" --language hi

# Force English
bharat deploy "flask app banao" --language en

# Force Hinglish
bharat list --language hinglish

# Auto-detect (default)
bharat deploy "flask app banao" --language auto
```

---

## Dry Run Mode

Preview commands without executing them:

```bash
bharat deploy "flask app banao" --dry-run
bharat delete "purana server" --dry-run
```

---

## Advanced Usage

### Verbose Output (Debugging)

```bash
bharat --verbose deploy "flask app banao"
bharat -v list "EC2 instances dikhao"
```

### Skip Confirmation for Delete

```bash
bharat delete "test server" --force
```

---

## Common Hinglish Patterns

| What you want to do | Hinglish command |
|--------------------|-----------------|
| Create EC2 instance | `bharat deploy "EC2 instance banao"` |
| List all servers | `bharat list "saare servers dikhao"` |
| Delete old resource | `bharat delete "purana resource hatao"` |
| Start stopped instance | `bharat deploy "band instance shuru karo"` |
| Explain a concept | `bharat explain "VPC kya hota hai"` |
| Check running instances | `bharat list "running instances dikhao"` |
| Create S3 bucket | `bharat deploy "S3 bucket banao"` |
| Deploy Lambda | `bharat deploy "Lambda function deploy karo"` |
