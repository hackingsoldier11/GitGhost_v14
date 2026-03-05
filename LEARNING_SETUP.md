# 🎓 GitGhost Learning Setup & Forensic Academy

Welcome to the **GitGhost v14.0 Learning Path**. This document outlines the "Proper Learning Setup" required to master kinetic forensic security and secret exhumation.

---

## 🏗️ Phase 1: Environment Setup

Before starting the labs, ensure your local environment is calibrated for forensic analysis.

### 1. Repository Preparation
GitGhost requires a native Git installation to traverse the DAG.
```bash
# Verify git installation
git --version

# Clone the training target (OWASP Juice Shop)
# This repo contains 10+ years of 'deleted' secrets
git clone https://github.com/juice-shop/juice-shop
```

### 2. Dependency Matrix
Install the specific DevSecOps stack required for v14.0:
```bash
pip install -r requirements_v14.txt
```

---

## 📚 Phase 2: Core Curriculum

### Module 1: The Forensic Mindset
*   **Concept:** "Deletion is not Destruction."
*   **Learning Goal:** Understand how Git objects persist even after files are removed from the working tree.
*   **Activity:** Run `git log --diff-filter=D --summary` and observe the "graveyard" of files.

### Module 2: The Math of Secrets (Shannon Entropy)
*   **Concept:** Cryptographic chaos vs. structured code.
*   **Learning Goal:** Learn why standard regex isn't enough.
*   **Formula:** $H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$
*   **Activity:** Use the GitGhost Dashboard to visualize entropy scores of different findings.

### Module 3: Isolation Forest ML
*   **Concept:** Unsupervised anomaly detection.
*   **Learning Goal:** Understand how GitGhost finds "outliers" without prior training data.
*   **Activity:** Locate the `scikit-learn` integration in `app.py` and see how it clusters findings.

### Module 4: The Purge Protocol
*   **Concept:** Immutable history rewriting.
*   **Learning Goal:** Master `git filter-repo` to surgically remove secrets without destroying the repository.
*   **Lab:** Follow the instructions in the "AI Remediation" tab to fix a findings.

---

## 🔬 Interactive Labs

### Lab 1: Targeted Exhumation
1. Start the Command Center: `python app.py`
2. Enter `juice-shop` as the target.
3. Locate the **CRITICAL** finding in `.env.production`.
4. Use the **Learning Studio** tab to understand why this was flagged.

### Lab 2: Pre-Commit Defense
1. Install the hook: `cp hooks/pre-commit.py .git/hooks/pre-commit`.
2. Attempt to commit a "fake" secret (e.g., `AKIAIOSFODNN7EXAMPLE`).
3. Observe how GitGhost intercepts the commit *before* it becomes a ghost.

---

## 🏆 Certification
Upon completing all modules and labs, you are prepared to deploy GitGhost in an enterprise environment to protect the software supply chain.

> "To protect the future, we must audit the past." - GitGhost Forensic Team
