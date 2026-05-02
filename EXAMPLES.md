# Examples

## Hindi Commands (Devanagari)

### Deploy

```bash
python main.py deploy "नमस्ते, मुझे एक Flask app deploy करना है" --language hi
```

Expected output:
```
🔍 Detected language: hi
✅ Instance i-0abc1234def567890 launched successfully.
```

### List Resources

```bash
python main.py list-resources --language hi
```

### Delete a Resource

```bash
python main.py delete i-0abc1234def567890 --language hi
```

```
⚠️  About to delete: i-0abc1234def567890
   Command: aws ec2 terminate-instances --instance-ids i-0abc1234def567890
क्या आप sure हैं? / Are you sure? [y/N]:
```

---

## Hinglish Commands (Roman script)

### Deploy

```bash
python main.py deploy "banao ek EC2 instance ap-south-1 mein"
```

Output:
```
🔍 Detected language: hi
✅ Instance launched in ap-south-1.
```

### Common Hinglish Keywords

| Keyword | Meaning | Example |
|---------|---------|---------|
| `banao` | create  | `banao ek S3 bucket` |
| `karo`  | do      | `deploy karo mera app` |
| `hatao` | delete  | `hatao yeh server` |
| `dikhao`| show    | `dikhao mujhe resources` |
| `dekho` | see     | `dekho kaun se instances chal rahe hain` |

---

## English Commands

```bash
python main.py deploy flask-app
python main.py deploy "create a new S3 bucket named my-bucket"
python main.py list-resources
python main.py delete i-0abc1234def567890
```

---

## Dry Run Mode

Preview what would happen without executing:

```bash
python main.py deploy flask-app --dry-run
```

Output:
```
🔍 Detected language: en
✅ [DRY RUN] aws ec2 run-instances --image-id ami-0abcdef1234567890 --instance-type t3.micro
```

---

## Error Scenarios

### Missing Groq API Key

```
❌ GROQ_API_KEY environment variable is not set.
```

**Fix:** Add `GROQ_API_KEY=...` to your `.env` file.

### Invalid AMI ID

```
❌ यह AMI image आपके region में available नहीं है।
```

### Insufficient Permissions

```
❌ आपके पास इस operation को करने की permission नहीं है।
```

---

## Running the Demo

```bash
python demo.py
```

The demo shows all 8 modules working end-to-end with mocked Groq responses — no API key required.
