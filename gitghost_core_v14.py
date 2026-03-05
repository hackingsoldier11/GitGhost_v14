#!/usr/bin/env python3
"""
GitGhost v14.0 - Enhanced Forensic Scanner
New Features:
- Multiprocessing for large repos
- Advanced false positive filtering
- Time-range filtering
- Enhanced ML features
- Input validation & security hardening
"""

import subprocess
import sys
import os
import math
import re
import json
import base64
import hashlib
from datetime import datetime, timedelta
from collections import Counter
from multiprocessing import Pool, cpu_count
from pathlib import Path
import argparse

# --- CONFIGURATION ---
ENTROPY_THRESHOLD = 6.0
MAX_FILE_SIZE = 1024 * 1024  # 1MB
MAX_LINE_LENGTH = 500
BLOB_TIMEOUT = 5  # seconds
MIN_SECRET_LENGTH = 8
CACHE_FILE = ".gitghost_cache.json"

# --- ENHANCED SIGNATURES ---
SIGNATURES = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret": re.compile(r"(?i)aws_secret_access_key.{0,20}[0-9a-zA-Z\/+]{40}"),
    "Google API": re.compile(r"AIza[0-9A-Za-z\\-_]{35}"),
    "Private Key": re.compile(r"-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    "Generic Secret": re.compile(r"(?i)(api_key|secret|password|auth_token|passwd)\s*[:=]\s*['\"][A-Za-z0-9+/=_.]{10,}['\"]"),
    "S3 Bucket Config": re.compile(r"(?i)s3_bucket\s*[\"']?:\s*[\"'][a-z0-9.-]+[\"']"),
    "Terraform State": re.compile(r"(?i)\"terraform_version\":"),
    "Generic API Key": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]"),
    "JWT Token": re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    "Database URL": re.compile(r"(?i)(mongodb|mysql|postgres|redis)://[^\s\"']+"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}"),
    "GitHub Token": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    "NPM Token": re.compile(r"npm_[a-zA-Z0-9]{36}"),
    "Encryption Key": re.compile(r"(?i)(aes|des|iv|salt|encryption).{0,20}[0-9a-fA-F]{32,64}"),
    "CTF Flag": re.compile(r"\{[a-zA-Z0-9_]{10,}\}"),
}

# --- ENHANCED NEGATIVE SIGNATURES (False Positive Reduction) ---
NEGATIVE_SIGS = [
    "color:", "background:", "font-family:", "function", "var ", "<svg",
    "placeholder", "example.com", "lorem ipsum", "test@test.com",
    "0123456789", "abcdefghijk"
]

TEST_PATH_INDICATORS = ['/test/', '/tests/', '/cypress/', '/e2e/', '/__tests__/', '/spec/', '.spec.', '.test.']
MOCK_INDICATORS = ['mock', 'example', 'sample', 'dummy', 'fixture', 'stub', 'fake']

# --- BACKUP EXTENSIONS ---
TEMP_EXTENSIONS = ('.bak', '.old', '.tmp', '.swp', '.backup', '.log', '.sql.gz', '.tar.gz', '~')
SUSPICIOUS_FILENAMES = {".env", "config.js", "secrets.yml", "passwd", "shadow", "main.tf", ".npmrc", ".pypirc"}
IGNORED_EXTENSIONS = ('.jpg', '.png', '.css', '.min.js', '.svg', '.gif', '.woff', '.ttf', '.eot')

# --- ENHANCED SCORING WITH CONTEXT ---
def get_cvss(finding_type, context=""):
    """Enhanced CVSS scoring with context awareness"""
    SCORING = {
        "AWS Access Key": (9.8, "CRITICAL", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"),
        "AWS Secret": (9.8, "CRITICAL", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"),
        "Private Key": (9.1, "CRITICAL", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N"),
        "Backup File": (6.5, "MEDIUM", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N"),
        "Terraform State": (8.5, "HIGH", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"),
        "Critical Filename": (7.5, "HIGH", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"),
        "High Entropy": (5.0, "MEDIUM", "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N"),
        "Database URL": (8.2, "HIGH", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N"),
        "JWT Token": (7.3, "HIGH", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"),
        "GitHub Token": (9.0, "CRITICAL", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N"),
        "Encryption Key": (8.8, "HIGH", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N"),
        "CTF Flag": (7.0, "MEDIUM", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"),
    }
    
    score, severity, vector = SCORING.get(finding_type, (5.0, "MEDIUM", "CVSS:3.1/Unknown"))
    
    # Downgrade if in test context
    if any(indicator in context.lower() for indicator in TEST_PATH_INDICATORS + MOCK_INDICATORS):
        if severity == "CRITICAL":
            severity = "HIGH"
            score -= 2.0
        elif severity == "HIGH":
            severity = "MEDIUM"
            score -= 1.5
    
    return score, severity, vector

def shannon_entropy(data):
    """Calculate Shannon entropy for randomness detection"""
    if not data: 
        return 0
    entropy = 0
    length = len(data)
    for count in Counter(data).values():
        p_x = count / length
        entropy += - p_x * math.log2(p_x)
    return entropy

def is_likely_false_positive(content, filename):
    """Advanced false positive detection"""
    lower_content = content[:1000].lower()
    lower_filename = filename.lower()
    
    # Check 1: Test files
    if any(test_path in lower_filename for test_path in TEST_PATH_INDICATORS):
        # If contains mock indicators, very likely FP
        if any(mock in lower_content for mock in MOCK_INDICATORS):
            return True
    
    # Check 2: Obvious examples/placeholders
    if any(neg in lower_content for neg in NEGATIVE_SIGS):
        # Check density - if more than 3 negative sigs, likely FP
        neg_count = sum(1 for neg in NEGATIVE_SIGS if neg in lower_content)
        if neg_count >= 3:
            return True
    
    # Check 3: Short "secrets" that are likely not real
    secret_matches = re.findall(r'(?i)(password|secret|key)\s*[:=]\s*["\']([^"\']+)["\']', content[:500])
    for _, value in secret_matches:
        if len(value) < MIN_SECRET_LENGTH:
            return True
        # Common test passwords
        if value.lower() in ['admin']:
            return True
    
    return False

def recursive_base64_decoder(content):
    """Enhanced base64 decoder with binary filtering"""
    decoded_findings = []
    for candidate in re.findall(r'[A-Za-z0-9+/=]{20,}', content):
        try:
            padding = len(candidate) % 4
            if padding: 
                candidate += '=' * (4 - padding)
            decoded_bytes = base64.b64decode(candidate)
            
            # Filter binary formats
            if decoded_bytes.startswith(b'\x89PNG') or \
               decoded_bytes.startswith(b'\xff\xd8') or \
               decoded_bytes.startswith(b'GIF8') or \
               decoded_bytes.startswith(b'%PDF'):
                continue
            
            decoded = decoded_bytes.decode('utf-8', errors='ignore')
            
            # Only flag if contains security-relevant keywords
            if any(s in decoded.lower() for s in ['key', 'secret', 'password', 'token', 'bucket', 'api']):
                decoded_findings.append(f"Decoded: {decoded[:50]}...")
        except: 
            pass
    return decoded_findings

def analyze_content(content, filename, commit_date=None):
    """Enhanced content analysis with context awareness"""
    findings = []
    reason_parts = []
    
    # Quick false positive check
    if is_likely_false_positive(content, filename):
        return None, None, None, None, None, True  # Added FP flag
    
    # Check 1: Backups
    if filename.lower().endswith(TEMP_EXTENSIONS) or filename.startswith("~$") or filename.endswith("~"):
        findings.append("Backup File")
    
    # Check 2: Signatures
    for name, pattern in SIGNATURES.items():
        matches = pattern.findall(content)
        if matches:
            findings.append(name)
            # Store first match for context
            if isinstance(matches[0], tuple):
                reason_parts.append(f"{name}: {matches[0][0][:20]}...")
            else:
                reason_parts.append(f"{name}: {str(matches[0])[:20]}...")
    
    # Check 3: Base64
    decoded = recursive_base64_decoder(content)
    if decoded:
        findings.append("Hidden Base64")
        reason_parts.append(decoded[0])
    
    # Check 4: Context
    if any(s in filename.lower() for s in SUSPICIOUS_FILENAMES): 
        findings.append("Critical Filename")
    
    entropy = shannon_entropy(content)
    primary_finding = findings[0] if findings else ("High Entropy" if entropy > ENTROPY_THRESHOLD else None)
    
    if not primary_finding: 
        return None, None, None, None, None, False
    
    if findings: 
        reason_parts.insert(0, f"Found: {', '.join(list(set(findings))[:3])}")
    elif primary_finding == "High Entropy": 
        reason_parts.append("High Entropy")
    
    score, severity, vector = get_cvss(primary_finding, filename)
    
    return severity, " | ".join(reason_parts), entropy, score, vector, False

def load_cache(cache_path):
    """Load previously scanned blob hashes"""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_cache(cache_path, cache_data):
    """Save scanned blob hashes"""
    try:
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
    except:
        pass

def validate_repo_path(repo_path):
    """Security: validate repository path"""
    repo_path = os.path.abspath(repo_path)
    
    # Check for path traversal attempts
    if '..' in repo_path or repo_path.startswith('/etc') or repo_path.startswith('/root'):
        raise ValueError("Invalid repository path: potential security risk")
    
    # Verify it's actually a git repo
    git_dir = os.path.join(repo_path, '.git')
    if not os.path.isdir(git_dir):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    return repo_path

def process_blob(args):
    """Worker function for multiprocessing"""
    repo_path, blob_hash, path, curr_commit, cache = args
    
    # Check cache
    if blob_hash in cache:
        return None
    
    try:
        blob_cmd = ["git", "-C", repo_path, "show", blob_hash]
        result = subprocess.run(blob_cmd, capture_output=True, text=True, 
                              errors="replace", timeout=BLOB_TIMEOUT)
        content = result.stdout
        # Normalize: strip BOM and non-printable prefixes
        content = content.lstrip('\ufeff').lstrip('\xff\xfe').lstrip('\xfe\xff')
        print(f"DEBUG: Scanning {path} | Content: {content.strip()}")
        
        if not content or len(content) > MAX_FILE_SIZE:
            return None
        
        risk, reason, entropy, cvss_score, cvss_vector, is_fp = analyze_content(
            content, path, curr_commit.get("time")
        )
        
        if risk and not is_fp:
            return {
                "risk": risk, 
                "cvss_score": cvss_score, 
                "cvss_vector": cvss_vector,
                "file": path, 
                "author": curr_commit.get("author", "Unknown"),
                "email": curr_commit.get("email", "Unknown"), 
                "commit": curr_commit.get("hash", "Unknown"),
                "date": datetime.fromtimestamp(int(curr_commit.get("time", 0))).strftime('%Y-%m-%d'),
                "reason": reason, 
                "entropy": round(entropy, 4), 
                "snippet": content[:200].replace("\n", " "),
                "blob_hash": blob_hash
            }
    except subprocess.TimeoutExpired:
        print(f"[!] Timeout processing blob: {blob_hash}")
    except Exception as e:
        print(f"[!] Error processing blob {blob_hash}: {e}")
    
    return None

def scan_repo(repo_path, since_days=None, max_workers=None, use_cache=True):
    """Enhanced repository scanner with multiprocessing"""
    repo_path = validate_repo_path(repo_path)
    
    print(f"[*] GitGhost v14.0 - Enhanced Forensic Scanner")
    print(f"[*] Target: {repo_path}")
    
    # Load cache
    cache_path = os.path.join(repo_path, CACHE_FILE)
    cache = load_cache(cache_path) if use_cache else {}
    
    report_data = []
    # Changed from --diff-filter=D to include Added/Modified files for v14 Full Scan
    cmd = ["git", "-C", repo_path, "log", "--all", "--raw", 
           "--format=COMMIT:%H:%at:%an:%ae:%s", "--no-renames"]
    
    # Add time filter if specified
    if since_days:
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
        cmd.extend(["--since", since_date])
        print(f"[*] Filtering commits since: {since_date}")
    
    try: 
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, errors="replace")
    except Exception as e: 
        print(f"[!] Error: {e}")
        return
    
    work_items = []
    # --- HYBRID SCAN: Part 1: Current Files ---
    print("[*] Parsing current codebase (Live Shield)...")
    ls_cmd = ["git", "-C", repo_path, "ls-tree", "-r", "HEAD"]
    try:
        ls_process = subprocess.run(ls_cmd, capture_output=True, text=True, check=True)
        for line in ls_process.stdout.splitlines():
            # format: mode type hash    path
            parts = line.split(None, 3)
            if len(parts) < 4: continue
            blob_hash, path = parts[2], parts[3]
            if path.lower().endswith(IGNORED_EXTENSIONS): continue
            
            # Dummy commit for current files
            curr_commit = {"hash": "HEAD (Live)", "time": str(int(datetime.now().timestamp())), 
                           "author": "Current Workspace", "email": "live@system", "msg": "Active Codebase"}
            work_items.append((repo_path, blob_hash, path, curr_commit, cache))
    except:
        print("[!] Warning: Could not scan current HEAD")

    # --- HYBRID SCAN: Part 2: Deleted and Historical Files ---
    print("[*] Parsing git history (Ghost Exhumation)...")
    for line in process.stdout:
        line = line.strip()
        if not line: continue
        
        if line.startswith("COMMIT:"):
            parts = line.split(":", 5)
            curr_commit = {
                "hash": parts[1], "time": parts[2], "author": parts[3], 
                "email": parts[4], "msg": parts[5] if len(parts) > 5 else ""
            }
            continue
        
        try:
            metadata, path = line.split("\t", 1)
            blob_hash = metadata.split(" ")[2]
            if path.lower().endswith(IGNORED_EXTENSIONS): continue
            work_items.append((repo_path, blob_hash, path, curr_commit.copy(), cache))
        except:
            continue
    
    print(f"[*] Found {len(work_items)} total artifacts to analyze")
    
    # Process with multiprocessing
    workers = max_workers or max(1, cpu_count() - 1)
    print(f"[*] Using {workers} worker processes")
    
    if workers > 1 and len(work_items) > 10:
        with Pool(workers) as pool:
            results = pool.map(process_blob, work_items)
    else:
        results = [process_blob(item) for item in work_items]
    
    # Filter out None results
    report_data = [r for r in results if r is not None]
    
    # Update cache
    if use_cache:
        for item in work_items:
            blob_hash = item[1]
            cache[blob_hash] = True
        save_cache(cache_path, cache)
    
    # Print summary
    print(f"\n[*] SCAN COMPLETE")
    print(f"[*] Total artifacts found: {len(report_data)}")
    
    if report_data:
        severity_counts = Counter(r['risk'] for r in report_data)
        print(f"[*] Critical: {severity_counts.get('CRITICAL', 0)}")
        print(f"[*] High: {severity_counts.get('HIGH', 0)}")
        print(f"[*] Medium: {severity_counts.get('MEDIUM', 0)}")
    
    # Sort by CVSS score
    report_data.sort(key=lambda x: x['cvss_score'], reverse=True)
    
    # Save report
    output_file = "ghost_report_v14.json"
    with open(output_file, "w") as f: 
        json.dump(report_data, f, indent=4)
    
    print(f"[*] Report saved to: {output_file}")
    
    return report_data

def main():
    parser = argparse.ArgumentParser(
        description="GitGhost v14.0 - AI-Powered Forensic Scanner for Deleted Files"
    )
    parser.add_argument("repo_path", help="Path to git repository")
    parser.add_argument("--since", type=int, help="Scan commits from last N days", default=None)
    parser.add_argument("--workers", type=int, help="Number of worker processes", default=None)
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--output", help="Output JSON file", default="ghost_report_v14.json")
    
    args = parser.parse_args()
    
    scan_repo(
        args.repo_path, 
        since_days=args.since, 
        max_workers=args.workers,
        use_cache=not args.no_cache
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gitghost_core_v14.py <path_to_repo> [--since DAYS] [--workers N] [--no-cache]")
        print("Example: python gitghost_core_v14.py /path/to/repo --since 90 --workers 4")
    else:
        main()
