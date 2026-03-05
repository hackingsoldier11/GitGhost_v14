import re

start_marker = 'elif app_mode == "🌐 THREAT INTEL":'
end_marker = 'elif app_mode == "📈 ANALYTICS":'

# NEW CONTENT: Your Exact Order for 2025
new_content = """    st.title("🌐 THREAT LANDSCAPE EVOLUTION")
    st.markdown("`OWASP TOP 10: 2025 FORECAST`")
    
    col1, mid, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.subheader("📊 CURRENT: Standard Web Risks")
        st.caption("Traditional Attack Vectors")
        # Standard Context
        df_now = pd.DataFrame({
            "Threat": ["A01: Broken Access", "A02: Crypto Failures", "A03: Injection", "A04: Insecure Design"],
            "Score": [95, 90, 85, 80]
        })
        fig1 = px.bar(df_now, x="Score", y="Threat", orientation='h', color="Score", color_continuous_scale="Blues")
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#C9D1D9", height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🔮 FUTURE: OWASP 2025")
        st.caption("Your Custom Forecast")
        # YOUR EXACT LIST
        df_next = pd.DataFrame({
            "Threat": [
                "A07: Authentication Failure", 
                "A01: Broken Access Control", 
                "A02: Security Misconfiguration", 
                "A04: Cryptographic Failure"
            ],
            # Scores assigned to maintain your order (Top = Highest)
            "Score": [99, 95, 88, 85]
        })
        # We sort by score to keep your A07 at the top
        fig2 = px.bar(df_next, x="Score", y="Threat", orientation='h', color="Score", color_continuous_scale="Reds")
        # Force the order to match your list
        fig2.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00FF41", height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    
    st.info("⚠️ 2025 FORECAST: A07 (Auth Failures) and A01 (Access Control) are projected to dominate the threat landscape.")
"""

# Apply Patch
with open("dashboard_v14.py", "r") as f:
    code = f.read()

pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + new_content + "\n" + end_marker

if start_marker in code:
    fixed_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    with open("dashboard_v14.py", "w") as f:
        f.write(fixed_code)
    print("✅ ORDER APPLIED: 2025 Chart updated with A07, A01, A02, A04.")
else:
    print("⚠️ ERROR: Tab markers not found.")
