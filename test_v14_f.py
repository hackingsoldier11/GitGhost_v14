import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_system():
    print("[*] Testing GitGhost v14.F FullStack System")
    
    # 1. UI Check
    try:
        r = requests.get(BASE_URL)
        print(f"[+] UI Availability: {'ONLINE' if r.status_code == 200 else 'OFFLINE'}")
    except:
        print("[-] UI Availability: OFFLINE (Backend might not be running)")
        return

    # 2. API Scan Test
    print("[*] Triggering Forensic Scan API...")
    try:
        r = requests.post(f"{BASE_URL}/api/scan", json={"target": "clean_repo"})
        data = r.json()
        if data['status'] == 'success':
            print(f"[+] Scan Engine: WORKING (Found {data['data']['total']} artifacts)")
            print(f"[+] Security Score: {data['data']['score']}%")
            print(f"[+] ML Anomalies: {len([f for f in data['data']['findings'] if f['anomaly'] == -1])} detected")
        else:
            print("[-] Scan Engine: FAILED")
    except Exception as e:
        print(f"[-] Scan Engine Error: {e}")

    # 3. AI Advisor Test
    print("[*] Testing AI Advisor (Chat API)...")
    try:
        r = requests.post(f"{BASE_URL}/api/chat", json={"message": "How do I remediate findings found in secrets.txt?"})
        data = r.json()
        if 'remediate' in data['response'].lower() or 'triage' in data['response'].lower():
            print("[+] AI Advisor: WORKING (Contextual response received)")
        else:
            print("[-] AI Advisor: UNEXPECTED RESPONSE")
    except Exception as e:
        print(f"[-] AI Advisor Error: {e}")

    # 4. OWASP 2025 Test
    try:
        r = requests.post(f"{BASE_URL}/api/scan", json={"target": "clean_repo"})
        owasp = r.json()['data']['owasp']
        if any(v > 0 for v in owasp['web'].values()):
            print("[+] OWASP 2025 Mapping: WORKING")
        else:
            print("[-] OWASP 2025 Mapping: NO DATA")
    except:
        print("[-] OWASP 2025 Test Failed")

if __name__ == "__main__":
    test_system()
