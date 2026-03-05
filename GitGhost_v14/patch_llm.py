import re

file_path = "dashboard_v14.py"
with open(file_path, "r") as f:
    content = f.read()

# The data we want to inject (OWASP LLM 2025)
new_data = """    st.markdown("### 🤖 OWASP TOP 10 FOR LLM (2025)")
    st.info("GitGhost mitigates LLM06 (Sensitive Info Disclosure) by scrubbing training data.")
    df_owasp = pd.DataFrame({
        "Threat Vector": [
            "LLM01: Prompt Injection",
            "LLM06: Sensitive Info Disclosure (Git Leaks)",
            "LLM05: Supply Chain (Poisoned Repos)",
            "LLM02: Insecure Output Handling",
            "LLM03: Training Data Poisoning"
        ],
        "Relevance Score": [99, 98, 92, 85, 80]
    })"""

# Regex to find the old OWASP block (matches any version of it)
pattern = r"df_owasp\s*=\s*pd\.DataFrame\s*\(\{[\s\S]*?\}\)"

if re.search(pattern, content):
    new_content = re.sub(pattern, new_data, content)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("✅ SUCCESS: Dashboard upgraded to OWASP LLM 2025.")
else:
    print("⚠️ ERROR: Could not find the code block. Is the file already patched?")
