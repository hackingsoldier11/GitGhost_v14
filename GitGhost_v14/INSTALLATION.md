# GitGhost v14.0 - Installation & Usage Guide

## 🚀 What's New in v14

### Major Features
1. **⚡ Performance Optimizations**
   - Multiprocessing support for large repositories
   - Blob caching to avoid re-scanning
   - Time-range filtering for incremental scans

2. **🧠 Enhanced AI Detection**
   - Advanced false positive reduction
   - Context-aware CVSS scoring
   - Support for 10+ new credential types (GitHub tokens, NPM, Slack)

3. **🔒 Pre-Commit Hooks**
   - Real-time secret prevention
   - Blocks commits before they enter history
   - Warns about file deletions

4. **🤖 CI/CD Integration**
   - GitHub Actions workflow
   - SARIF format for Security tab
   - Automatic PR comments with findings
   - Fails builds on critical findings

5. **🌐 Multi-Repo Scanning**
   - Scan entire GitHub organizations
   - Generate security scorecards
   - Comparative analysis across repos

6. **📊 Enhanced Dashboard**
   - LLM-powered remediation advice
   - Timeline analysis
   - Interactive filtering
   - Export to CSV/SARIF

---

## 📦 Installation

### Prerequisites
```bash
# Python 3.9 or higher
python --version

# Git 2.20 or higher
git --version
```

### Install GitGhost
```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/gitghost.git
cd gitghost

# Install dependencies
pip install -r requirements_v14.txt

# Make scripts executable
chmod +x gitghost_core_v14.py
chmod +x hooks/pre-commit.py
```

### Optional: Install as Command
```bash
# Create symlink
sudo ln -s $(pwd)/gitghost_core_v14.py /usr/local/bin/gitghost

# Now you can use: gitghost /path/to/repo
```

---

## 🔍 Basic Usage

### 1. Scan a Single Repository
```bash
# Basic scan
python gitghost_core_v14.py /path/to/your/repo

# Scan last 90 days only (faster)
python gitghost_core_v14.py /path/to/repo --since 90

# Use 4 worker processes
python gitghost_core_v14.py /path/to/repo --workers 4

# Disable caching (for testing)
python gitghost_core_v14.py /path/to/repo --no-cache
```

**Output:**
```
[*] GitGhost v14.0 - Enhanced Forensic Scanner
[*] Target: /path/to/repo
[*] Found 234 deleted files to analyze
[*] Using 3 worker processes
[HIGH] CVSS:7.5 | lib/config.js
[CRITICAL] CVSS:9.8 | .env.backup
...
[*] SCAN COMPLETE
[*] Total artifacts found: 12
[*] Critical: 2
[*] High: 4
[*] Medium: 6
[*] Report saved to: ghost_report_v14.json
```

### 2. View Dashboard
```bash
# Launch interactive dashboard
streamlit run dashboard_v14.py

# Open browser to: http://localhost:8501
```

### 3. Generate PDF Report
```bash
python reporter_v14.py
# Creates: GitGhost_Audit_Report_v14.pdf
```

---

## 🛡️ Installing Pre-Commit Hook

Prevent secrets from entering git history:

```bash
# Navigate to your repository
cd /path/to/your/project

# Copy the hook
cp /path/to/gitghost/hooks/pre-commit.py .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit

# Test it
git add somefile.txt
git commit -m "test"
# Hook will scan and block if secrets found
```

**Example Output:**
```
🔍 GitGhost Pre-Commit Scanner v14.0
==================================================
⚠️  WARNING: You are deleting files:
  - old_config.js

❌ COMMIT BLOCKED - Secrets detected!

📄 .env.backup
  Line 3: [AWS Access Key]
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE

==================================================
💡 REMEDIATION OPTIONS:
  1. Remove the secrets from staged files
  2. Add files to .gitignore
  3. Use environment variables instead
==================================================
```

---

## 🔄 CI/CD Integration

### GitHub Actions

1. **Copy workflow file:**
```bash
mkdir -p .github/workflows
cp gitghost_v14/ci/github-actions.yml .github/workflows/gitghost.yml
```

2. **Customize settings:**
Edit `.github/workflows/gitghost.yml`:
```yaml
# Change scan frequency
schedule:
  - cron: '0 2 * * 1'  # Every Monday at 2 AM

# Adjust time range
--since 180  # Scan last 6 months
```

3. **Commit and push:**
```bash
git add .github/workflows/gitghost.yml
git commit -m "Add GitGhost security scanning"
git push
```

**What happens:**
- ✅ Scans run on every PR and push
- ✅ Results appear in GitHub Security tab (SARIF)
- ✅ PR gets commented with findings
- ❌ Build fails if CRITICAL findings exist

---

## 🌐 Multi-Repo Scanning

### Scan GitHub Organization
```bash
# Requires GitHub Personal Access Token
export GITHUB_TOKEN=ghp_your_token_here

python multi_repo_scanner.py org YOUR_ORG_NAME \
  --token $GITHUB_TOKEN \
  --max-repos 10 \
  --workers 3
```

**Output:**
```
[*] GitGhost v14.0 - Organization Scanner
[*] Target: YOUR_ORG_NAME
[*] Found 47 repositories
[*] Limiting to 10 repos

[*] Scanning: frontend-app
[*] Scanning: backend-api
...

================================================================================
SECURITY SCORECARD: YOUR_ORG_NAME
================================================================================

📊 ORGANIZATION OVERVIEW
  Total Repositories Scanned: 10
  Total Security Findings: 34
  Critical: 3
  High: 12

🔴 TOP 10 RISKIEST REPOSITORIES
Rank   Repository                               Score    Critical   High      
--------------------------------------------------------------------------------
1      legacy-admin-panel                       45       2          5         
2      mobile-app-v1                            67       1          4         
3      internal-tools                           72       0          3         

✅ CLEAN REPOSITORIES (4)
  - documentation-site
  - ui-component-library
```

### Scan from Repository List
```bash
# Create repos.txt
cat > repos.txt << EOF
https://github.com/user/repo1.git
https://github.com/user/repo2.git
https://github.com/org/repo3.git
EOF

# Scan all
python multi_repo_scanner.py list repos.txt --output ./results
```

---

## 🎯 Advanced Usage

### Custom False Positive Filtering

Edit `gitghost_core_v14.py`:

```python
# Add your own negative signatures
NEGATIVE_SIGS = [
    "color:", "background:", 
    "your_company_test_placeholder",
    "example@yourcompany.com"
]

# Whitelist test paths
TEST_PATH_INDICATORS = [
    '/test/', '/tests/', 
    '/your_custom_test_dir/'
]
```

### Adjust Entropy Threshold
```python
# Lower = more sensitive (more false positives)
# Higher = less sensitive (might miss some secrets)
ENTROPY_THRESHOLD = 6.0  # Default
ENTROPY_THRESHOLD = 5.5  # More sensitive
ENTROPY_THRESHOLD = 6.5  # Less sensitive
```

### Custom Signatures
```python
SIGNATURES = {
    # Add your own patterns
    "Your Custom API Key": re.compile(r"YOURAPP_[A-Z0-9]{32}"),
    "Internal Token": re.compile(r"INT-[0-9a-f]{16}"),
}
```

---

## 📊 Understanding the Results

### CVSS Scores
- **9.0-10.0 (CRITICAL)**: Immediate action required (AWS keys, private keys)
- **7.0-8.9 (HIGH)**: High priority remediation (API tokens, database URLs)
- **4.0-6.9 (MEDIUM)**: Medium priority (backup files, config leaks)
- **0.1-3.9 (LOW)**: Low priority (informational)

### Risk Categories
```json
{
  "risk": "CRITICAL",
  "cvss_score": 9.8,
  "file": ".env.production.backup",
  "reason": "Found: AWS Secret",
  "author": "john.doe@company.com",
  "commit": "abc123def456",
  "date": "2024-01-15"
}
```

### Remediation Priority
1. **CRITICAL findings** → Rotate credentials immediately
2. **HIGH findings** → Schedule remediation within 24-48 hours
3. **MEDIUM findings** → Address in next sprint
4. **Test files** → Review context before acting

---

## 🔧 Troubleshooting

### "Not a git repository" Error
```bash
# Ensure you're pointing to the repo root
ls -la .git/  # Should show .git directory

# If scanning a subdirectory, use parent:
python gitghost_core_v14.py ../
```

### Scan Taking Too Long
```bash
# Use time filtering
--since 90  # Only scan last 3 months

# Increase workers
--workers 8  # Use more CPU cores

# Enable caching (default)
# Second scan will be much faster
```

### Too Many False Positives
```bash
# Edit NEGATIVE_SIGS in gitghost_core_v14.py
# Add your company's test patterns

# Example:
NEGATIVE_SIGS = [
    "example.com",
    "test@test.com",
    "my_company_placeholder"
]
```

### Hook Not Working
```bash
# Check if executable
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit

# Bypass for emergency (NOT RECOMMENDED)
git commit --no-verify -m "message"
```

---

## 🎓 Best Practices

### 1. Regular Scanning
```bash
# Weekly cron job
0 2 * * 0 /usr/local/bin/gitghost /path/to/repo --since 7
```

### 2. Pre-Commit Hook in All Repos
```bash
# Add to your .gitignore template
echo ".gitghost_cache.json" >> ~/.gitignore_global
```

### 3. CI/CD Integration
- ✅ Run on every PR
- ✅ Fail build on CRITICAL findings
- ✅ Weekly full scans

### 4. Team Onboarding
- Share this README
- Demo the dashboard
- Explain CVSS scores
- Review common patterns

### 5. Remediation Workflow
```bash
# 1. Identify finding
python gitghost_core_v14.py /repo

# 2. View in dashboard
streamlit run dashboard_v14.py

# 3. Use AI remediation advice
# Click finding → Get commands

# 4. Remove from history
git filter-repo --path secret.txt --invert-paths
git push origin --force --all

# 5. Rotate credentials
# Follow service-specific rotation procedures
```

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

## 🤝 Contributing

Found a false positive pattern? Want to add a new signature?

1. Fork the repo
2. Add to `gitghost_core_v14.py`
3. Test thoroughly
4. Submit PR

---

## 📄 License

MIT License - See LICENSE file

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_ORG/gitghost/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_ORG/gitghost/discussions)
- **Security:** security@yourcompany.com
