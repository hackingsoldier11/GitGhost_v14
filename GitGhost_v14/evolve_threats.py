import re

# Target the THREAT INTEL tab
start_marker = 'elif app_mode == "🌐 THREAT INTEL":'
end_marker = 'elif app_mode == "📈 ANALYTICS":'

# The NEW Content (Side-by-Side Evolution)
new_content = """    st.title("🌐 THREAT LANDSCAPE EVOLUTION")
    st.markdown("`TRACKING THE SHIFT FROM WEB 2.0 TO AI & QUANTUM VECTORS`")
    
    # Create Layout
    col1, mid, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.subheader("📊 CURRENT: OWASP Relevance")
        st.caption("Standard Web Risks (2021-2024)")
        # Current Data
        df_now = pd.DataFrame({
            "Threat": ["A02: Crypto Failures", "A05: Misconfiguration", "A01: Broken Access", "A07: Auth Failures"],
            "Score": [98, 85, 92, 70]
        })
        fig1 = px.bar(df_now, x="Score", y="Threat", orientation='h', color="Score", color_continuous_scale="Blues")
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C9D1D9", height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🔮 FUTURE: OWASP 2025")
        st.caption("AI & Post-Quantum Risks")
        # Future Data
        df_next = pd.DataFrame({
            "Threat": ["LLM06: Git Data Leaks", "A02: Post-Quantum", "LLM03: Poisoning", "A05: AI Supply Chain"],
            "Score": [99, 95, 88, 96]
        })
        fig2 = px.bar(df_next, x="Score", y="Threat", orientation='h', color="Score", color_continuous_scale="Reds")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41", height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    
    # The Connection
    st.info("⚠️ CRITICAL INSIGHT: Attackers are shifting from 'A02 Crypto Failures' to 'LLM06 Data Leaks' to poison AI models. GitGhost stops both.")
"""

# Apply the Patch
with open("dashboard_v14.py", "r") as f:
    code = f.read()

pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + new_content + "\n" + end_marker

if start_marker in code:
    fixed_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    with open("dashboard_v14.py", "w") as f:
        f.write(fixed_code)
    print("✅ EVOLUTION COMPLETE: Current vs 2025 view installed.")
else:
    print("⚠️ ERROR: Could not find tab markers.")
