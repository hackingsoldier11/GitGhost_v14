#!/usr/bin/env python3
"""
GitGhost Pre-Commit Hook v14.0
Prevents secrets from entering git history in the first place

Installation:
  cp pre-commit.py .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
"""

import subprocess
import sys
import re
import os
from pathlib import Path

# Signature patterns (sync with core scanner)
CRITICAL_PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret": re.compile(r"(?i)aws_secret_access_key.{0,20}[0-9a-zA-Z\/+]{40}"),
    "Private Key": re.compile(r"-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    "GitHub Token": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}"),
    "NPM Token": re.compile(r"npm_[a-zA-Z0-9]{36}"),
    "Database URL": re.compile(r"(?i)(mongodb|mysql|postgres)://[^\s\"']+"),
}

BACKUP_EXTENSIONS = ['.bak', '.old', '.tmp', '.swp', '~', '.backup']

def scan_staged_files():
    """Scan all staged files for secrets"""
    violations = []
    
    # Get list of staged files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    
    staged_files = result.stdout.strip().split('\n')
    
    for filepath in staged_files:
        if not filepath:
            continue
        
        # Check for backup files
        if any(filepath.endswith(ext) for ext in BACKUP_EXTENSIONS):
            violations.append({
                'file': filepath,
                'type': 'Backup File',
                'line': 0,
                'content': 'Backup file detected'
            })
        
        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue
        
        # Scan for secrets
        for line_num, line in enumerate(content.split('\n'), 1):
            for secret_type, pattern in CRITICAL_PATTERNS.items():
                if pattern.search(line):
                    violations.append({
                        'file': filepath,
                        'type': secret_type,
                        'line': line_num,
                        'content': line[:80] + '...' if len(line) > 80 else line
                    })
    
    return violations

def scan_staged_deletions():
    """Scan files being deleted for secrets (warn user)"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=D'],
        capture_output=True,
        text=True
    )
    
    deleted_files = result.stdout.strip().split('\n')
    deleted_files = [f for f in deleted_files if f]
    
    if deleted_files:
        print("\n⚠️  WARNING: You are deleting files:")
        for f in deleted_files[:5]:
            print(f"  - {f}")
        if len(deleted_files) > 5:
            print(f"  ... and {len(deleted_files) - 5} more")
        print("\n💡 Remember: Deletion doesn't remove from git history!")
        print("   Run 'gitghost scan' after commit to check for exposed secrets.\n")

def main():
    print("🔍 GitGhost Pre-Commit Scanner v14.0")
    print("=" * 50)
    
    # Check for staged deletions
    scan_staged_deletions()
    
    # Scan for secrets
    violations = scan_staged_files()
    
    if violations:
        print("\n❌ COMMIT BLOCKED - Secrets detected!\n")
        
        # Group by file
        by_file = {}
        for v in violations:
            if v['file'] not in by_file:
                by_file[v['file']] = []
            by_file[v['file']].append(v)
        
        for filepath, file_violations in by_file.items():
            print(f"\n📄 {filepath}")
            for v in file_violations:
                if v['line'] > 0:
                    print(f"  Line {v['line']}: [{v['type']}]")
                    print(f"    {v['content']}")
                else:
                    print(f"  [{v['type']}] {v['content']}")
        
        print("\n" + "=" * 50)
        print("💡 REMEDIATION OPTIONS:")
        print("  1. Remove the secrets from staged files")
        print("  2. Add files to .gitignore")
        print("  3. Use environment variables instead")
        print("  4. Override (NOT RECOMMENDED): git commit --no-verify")
        print("=" * 50)
        
        return 1
    else:
        print("✅ No secrets detected - commit allowed\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
