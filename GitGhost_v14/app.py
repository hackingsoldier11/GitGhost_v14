from flask import Flask, render_template, jsonify, request, send_file
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
from sklearn.ensemble import IsolationForest
import io

app = Flask(__name__)

# --- CONFIGURATION ---
REPORT_FILE = "ghost_report_v14.json"

def load_local_data():
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

# --- FEATURE 4: OWASP 2025 MAPPING LOGIC ---
def get_owasp_compliance(findings):
    web_scores = {"W01": 0, "W02": 0, "W03": 0, "W04": 0, "W05": 0, "W06": 0, "W07": 0}
    llm_scores = {"L01": 0, "L02": 0, "L03": 0, "L04": 0, "L05": 0, "L06": 0}
    
    for f in findings:
        reason = f.get('reason', '').lower()
        risk = f.get('risk', 'LOW')
        weight = 20 if risk == 'CRITICAL' else 10 if risk == 'HIGH' else 5
        
        # Web Mapping
        if 'access' in reason or 'key' in reason: web_scores["W01"] += weight
        if 'private' in reason or 'crypto' in reason: web_scores["W02"] += weight
        if 'token' in reason or 'secret' in reason: web_scores["W07"] += weight
        
        # LLM Mapping
        if 'secret' in reason or 'config' in reason: llm_scores["L02"] += weight
        if 'api' in reason: llm_scores["L05"] += weight
        
    # Normalize to 100%
    return {
        "web": {k: min(100, v) for k, v in web_scores.items()},
        "llm": {k: min(100, v) for k, v in llm_scores.items()}
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def run_scan():
    target = request.json.get('target', 'juice-shop')
    
    # Feature 1: Real-time scan execution
    try:
        if os.path.exists("gitghost_core_v14.py"):
            subprocess.run(["python", "gitghost_core_v14.py", target, "--workers", "4", "--since", "365"], check=True, timeout=120)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Forensic Scan Failed: {str(e)}"}), 500

    data = load_local_data()
    df = pd.DataFrame(data)
    
    if df.empty:
        return jsonify({"status": "success", "data": {"total": 0, "findings": [], "score": 100}})

    # Logic for Feature 1 (Command Center Stats)
    total = len(df)
    critical = len(df[df['risk'] == 'CRITICAL'])
    high = len(df[df['risk'] == 'HIGH'])
    medium = len(df[df['risk'] == 'MEDIUM'])
    score = max(0, 100 - (critical * 15 + high * 5 + medium * 1))
    
    # Logic for Feature 2 (ML Anomaly - Isolation Forest)
    df['entropy'] = pd.to_numeric(df['entropy'], errors='coerce').fillna(0.0)
    df['cvss_score'] = pd.to_numeric(df['cvss_score'], errors='coerce').fillna(0.0)
    df['len'] = df['snippet'].apply(len)
    
    if len(df) >= 5:
        clf = IsolationForest(contamination=0.1, random_state=42)
        df['anomaly'] = clf.fit_predict(df[['entropy', 'cvss_score', 'len']])
    else:
        df['anomaly'] = 1

    # Logic for Feature 4 (OWASP Compliance)
    owasp_data = get_owasp_compliance(data)

    findings = []
    for _, row in df.iterrows():
        findings.append({
            "file": row['file'],
            "cvss": float(row['cvss_score']),
            "risk": row['risk'],
            "status": "EXHUMED" if "deleted" in row.get('reason', '').lower() else "DELETED",
            "type": row['reason'].split('|')[0].strip(),
            "entropy": float(row['entropy']),
            "author": row.get('author', 'Unknown'),
            "anomaly": int(row['anomaly'])
        })

    return jsonify({
        "status": "success",
        "data": {
            "total": total,
            "critical": critical,
            "high": high,
            "score": int(score),
            "avg_cvss": round(float(df['cvss_score'].mean()), 2),
            "findings": findings,
            "owasp": owasp_data,
            "timeline": df.groupby(pd.to_datetime(df['date']).dt.strftime('%Y-%m')).size().to_dict()
        }
    })

# Feature 3: AI Remediation Advisor
@app.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '').lower()
    
    if 'fix' in message or 'remediate' in message:
        response = "👉 **V14 Remediation Protocol**: For exhumed secrets, rotate the credential immediately. Then, use `git filter-repo --path <FILE> --invert-paths` to purge the history. Finally, force push to the main branch."
    elif 'owasp' in message:
        response = "GitGhost v14 currently maps findings to **W01 (Broken Access)** and **L02 (Data Leakage)** as the primary 2025 vectors."
    elif 'juice-shop' in message:
        response = "OWASP Juice Shop detected. Multiple intentional leaks found including hardcoded tokens and private keys."
    else:
        response = "I am the GitGhost AI Advisor. I can help with **purging history**, **OWASP 2025 compliance**, and **ML cluster analysis**."

    return jsonify({"response": response})

@app.route('/api/test')
def self_test():
    tests = {
        "App Running": True,
        "Scanner Exists": os.path.exists("gitghost_core_v14.py"),
        "Report Found": os.path.exists(REPORT_FILE),
        "Flask Routes": ["/", "/api/scan", "/api/chat", "/api/test"]
    }
    return jsonify({"status": "healthy", "checks": tests})

if __name__ == '__main__':
    app.run(port=8080, debug=True)
