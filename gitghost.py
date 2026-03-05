#!/usr/bin/env python3
"""
GitGhost v14.F - Friendly CLI Wrapper
The primary entry point for the Forensic Academy and Learning Studio.
"""

import sys
import subprocess
import os

def main():
    if len(sys.argv) < 2:
        print("\n🕵️ GitGhost v14.F Forensic Academy")
        print("====================================")
        print("Usage:")
        print("  python gitghost.py [target_repo]")
        print("\nQuick Commands:")
        print("  - python gitghost.py juice-shop    (Start Learning Lab)")
        print("  - python app.py                   (Launch Command Center Dashboard)")
        print("  - python demo.py                  (Show Feature Demos)")
        print("\nNeed help? Check LEARNING_SETUP.md")
        return

    target = sys.argv[1]
    # Default to 4 workers and 365 days depth for a 'Proper' scan
    cmd = ["python", "gitghost_core_v14.py", target, "--workers", "4", "--since", "365"]
    
    print(f"\n[*] Initiating Kinetic Forensic Scan on: {target}")
    print("[*] Calibration: 4 parallel workers, 365-day depth.")
    print("[*] Learning Studio integration: ENABLED\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[!] Scan aborted by user.")
    except Exception as e:
        print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()
