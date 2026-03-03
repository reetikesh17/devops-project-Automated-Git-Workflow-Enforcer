# Line Endings Guide

## Understanding the Warning

When you see:
```
warning: in the working copy of 'file.yaml', LF will be replaced by CRLF the next time Git touches it
```

This is **normal on Windows** and indicates Git is handling line ending conversions.

---

## What Are Line Endings?

### LF (Line Feed) - `\n`
- Used by: Linux, macOS, Unix
- Represented as: `\n`
- Hex: `0A`

### CRLF (Carriage Return + Line Feed) - `\r\n`
- Used by: Windows
- Represented as: `\r\n`
- Hex: `0D 0A`

---

## Why This Matters

### Critical for Shell Scripts
Shell scripts (`.sh` files) **must** use LF endings to work on Linux/Mac:
```bash
#!/bin/bash
# This script needs LF endings to execute properly on Linux
```

If a shell script has CRLF endings, you'll get errors like:
```
bash: ./script.sh: /bin/bash^M: bad interpreter
```

### Critical for YAML Files
Kubernetes and Docker Compose YAML files should use LF for consistency across platforms.

---

## Solution Implemented

### 1. `.gitattributes` File Created ✅

This file tells Git how to handle line endings for different file types:

```gitattributes
# Shell scripts - always LF
*.sh text eol=lf

# YAML files - always LF
*.yaml text eol=lf
*.yml text eol=lf

# Python files - always LF
*.py text eol=lf

# Windows scripts - always CRLF
*.bat text eol=crlf
*.ps1 text eol=crlf
```

### 2. Git Configuration

Your Git is already configured correctly with:
```
core.autocrlf=true
```

This means:
- **Checkout**: Converts LF → CRLF (for Windows editing)
- **Commit**: Converts CRLF → LF (for repository)

---

## What Happens Now

### When You Commit

1. **Files with LF in repo** (like `.sh`, `.yaml`):
   - Git stores them with LF
   - On Windows checkout, they may be converted to CRLF for editing
   - On commit, converted back to LF

2. **Files with CRLF in repo** (like `.bat`):
   - Git stores them with CRLF
   - No conversion needed

### The Warning Explained

```
warning: in the working copy of 'file.yaml', LF will be replaced by CRLF the next time Git touches it
```

This means:
- ✅ File will be stored with LF in repository (correct)
- ℹ️ File will have CRLF in your working directory (for Windows editing)
- ✅ This is expected behavior on Windows

---

## Verify Line Endings

### Check Current Line Endings

**Windows (PowerShell)**:
```powershell
# Check a file
Get-Content infrastructure/kubernetes/cronjob.yaml -Raw | Select-String "`r`n"
```

**Linux/Mac**:
```bash
# Check a file
file infrastructure/kubernetes/cronjob.yaml

# Or use dos2unix
dos2unix -i infrastructure/kubernetes/cronjob.yaml
```

### Convert Line Endings (If Needed)

**Windows (PowerShell)**:
```powershell
# Convert CRLF to LF
(Get-Content file.sh -Raw) -replace "`r`n", "`n" | Set-Content file.sh -NoNewline
```

**Linux/Mac**:
```bash
# Convert CRLF to LF
dos2unix file.sh

# Or using sed
sed -i 's/\r$//' file.sh
```

---

## Best Practices

### 1. Use `.gitattributes` ✅
Already created and configured for your project.

### 2. Configure Git Properly

**Windows**:
```bash
git config --global core.autocrlf true
```

**Linux/Mac**:
```bash
git config --global core.autocrlf input
```

### 3. Editor Configuration

**VS Code** (`.vscode/settings.json`):
```json
{
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true
}
```

**IntelliJ/PyCharm**:
- Settings → Editor → Code Style → Line separator → Unix and macOS (\n)

---

## Handling the Warnings

### Option 1: Ignore Them (Recommended)
These warnings are informational and don't indicate a problem. Git is working correctly.

### Option 2: Suppress Warnings
```bash
# Disable the warning
git config --global core.safecrlf false
```

### Option 3: Normalize Repository
```bash
# After adding .gitattributes, normalize all files
git add --renormalize .
git commit -m "chore: normalize line endings"
```

---

## Current Status

### Files Affected
- `infrastructure/kubernetes/cronjob.yaml` - ✅ Will be LF in repo
- `infrastructure/kubernetes/test-configmap.sh` - ✅ Will be LF in repo
- `infrastructure/terraform/deploy.sh` - ✅ Will be LF in repo

### What Git Will Do
1. **In Repository**: Store with LF (correct for Linux/Mac compatibility)
2. **In Working Directory**: May convert to CRLF on Windows (for editing)
3. **On Commit**: Convert back to LF (automatic)

---

## Testing Line Endings

### Test Shell Scripts on Linux

After committing, test on Linux:
```bash
# Clone on Linux
git clone <repo-url>

# Check line endings
file infrastructure/kubernetes/test-configmap.sh
# Should show: ASCII text

# Make executable
chmod +x infrastructure/kubernetes/test-configmap.sh

# Run
./infrastructure/kubernetes/test-configmap.sh
# Should work without errors
```

### Test on Windows

```powershell
# Clone on Windows
git clone <repo-url>

# Files will have CRLF in working directory (for editing)
# But will be committed as LF (for Linux compatibility)
```

---

## Troubleshooting

### Problem: Shell Script Won't Execute on Linux

**Symptom**:
```
bash: ./script.sh: /bin/bash^M: bad interpreter
```

**Cause**: Script has CRLF line endings

**Solution**:
```bash
# Convert to LF
dos2unix script.sh

# Or
sed -i 's/\r$//' script.sh

# Make executable
chmod +x script.sh
```

### Problem: Git Shows Many Modified Files

**Symptom**: After adding `.gitattributes`, many files show as modified

**Cause**: Line ending normalization

**Solution**:
```bash
# This is expected. Commit the changes:
git add --renormalize .
git commit -m "chore: normalize line endings with .gitattributes"
```

---

## Summary

### ✅ What We Did
1. Created `.gitattributes` file
2. Configured line endings for all file types
3. Ensured shell scripts use LF
4. Ensured YAML files use LF
5. Ensured Windows scripts use CRLF

### ✅ What This Means
- **Shell scripts** will work on Linux/Mac
- **YAML files** will be consistent
- **Windows scripts** will work on Windows
- **Cross-platform compatibility** ensured

### ✅ What You Should Do
1. **Commit the changes**:
   ```bash
   git add .gitattributes
   git commit -m "chore: add .gitattributes for line ending consistency"
   ```

2. **Normalize existing files** (optional):
   ```bash
   git add --renormalize .
   git commit -m "chore: normalize line endings"
   ```

3. **Ignore the warnings**: They're informational and indicate Git is working correctly

---

## Quick Reference

| File Type | Line Ending | Why |
|-----------|-------------|-----|
| `.sh` | LF | Must work on Linux/Mac |
| `.yaml` | LF | Consistency across platforms |
| `.py` | LF | Python convention |
| `.bat` | CRLF | Windows requirement |
| `.ps1` | CRLF | PowerShell convention |
| `.md` | LF | Markdown convention |

---

## Conclusion

The warnings you see are **normal and expected** on Windows. Git is correctly:
1. ✅ Storing files with LF in the repository
2. ✅ Converting to CRLF in your working directory (for Windows editing)
3. ✅ Converting back to LF when you commit

**No action required** - just commit your changes as normal!

---

**Status**: ✅ Configured Correctly  
**Action**: Commit and push as normal  
**Warnings**: Safe to ignore
