import re

# The known markers for the start and end of the broken tab
start_marker = 'elif app_mode == "🌐 THREAT INTEL":'
end_marker = 'elif app_mode == "📈 ANALYTICS":'

# The CORRECT code (Perfectly indented with 4 spaces)
clean_code = """    st.title("🌐 GLOBAL THREAT INTEL")
    st.markdown("### 🤖 OWASP TOP 10 FOR LLM (2025)")
    st.info("GitGhost mitigates LLM06 (Sensitive Info Disclosure) by scrubbing training data.")
    
    # AI Threat Data
    data = {
        "Threat Vector": [
            "LLM01: Prompt Injection",
            "LLM06: Sensitive Info Disclosure",
            "LLM05: Supply Chain Vulnerabilities", 
            "LLM02: Insecure Output Handling",
            "LLM03: Training Data Poisoning"
        ],
        "Relevance Score": [99, 98, 92, 85, 80]
    }
    df_owasp = pd.DataFrame(data)
    
    # Plot
    fig = px.bar(df_owasp, x="Threat Vector", y="Relevance Score",
                 color="Relevance Score",
                 color_continuous_scale="reds",
                 title="AI THREAT LANDSCAPE")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41")
    st.plotly_chart(fig, use_container_width=True)

"""

# Read the broken file
with open("dashboard_v14.py", "r") as f:
    content = f.read()

# Regex to replace everything between the start marker and the next tab
pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + clean_code + end_marker

# Perform the swap
if start_marker in content and end_marker in content:
    # re.DOTALL makes (.) match newlines too
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open("dashboard_v14.py", "w") as f:
        f.write(new_content)
    print("✅ FIXED: Indentation repaired. OWASP LLM 10 installed.")
else:
    print("⚠️ ERROR: Could not find the Threat Intel section markers.")
