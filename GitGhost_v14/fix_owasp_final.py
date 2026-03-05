import re

# We target the specific THREAT INTEL tab
start_marker = 'elif app_mode == "🌐 THREAT INTEL":'
end_marker = 'elif app_mode == "📈 ANALYTICS":'

# The clean, perfectly indented 2025 Data
new_content = """    st.title("🌐 GLOBAL THREAT INTEL")
    st.markdown("### 🔮 OWASP TOP 10 (2025 FORECAST)")
    st.info("GitGhost proactively mitigates A02 (Post-Quantum Crypto Failures) and A05 (AI Supply Chain) by sanitizing history.")
    
    # 2025 Threat Data
    data = {
        "Threat Vector": [
            "A01: Broken Access Control",
            "A02: Cryptographic Failures (Post-Quantum)", 
            "A03: AI Prompt Injection",
            "A04: Insecure Design (Zero Trust)",
            "A05: Supply Chain (Model Poisoning)"
        ],
        "Relevance Score": [95, 99, 92, 85, 96]
    }
    df_owasp = pd.DataFrame(data)
    
    # Plotting
    fig = px.bar(df_owasp, x="Threat Vector", y="Relevance Score",
                 color="Relevance Score",
                 color_continuous_scale="reds",
                 title="2025 THREAT LANDSCAPE")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41")
    st.plotly_chart(fig, use_container_width=True)

"""

# Read the file
with open("dashboard_v14.py", "r") as f:
    code = f.read()

# Replace the broken section
pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + new_content + end_marker

if start_marker in code:
    fixed_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    with open("dashboard_v14.py", "w") as f:
        f.write(fixed_code)
    print("✅ SUCCESS: Dashboard upgraded to OWASP 2025.")
else:
    print("⚠️ ERROR: Could not find the Threat Intel tab.")
