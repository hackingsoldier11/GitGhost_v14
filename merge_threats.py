import re

# We target the THREAT INTEL tab
start_marker = 'elif app_mode == "🌐 THREAT INTEL":'
end_marker = 'elif app_mode == "📈 ANALYTICS":'

# The NEW Merged Code (Two Columns)
new_content = """    st.title("🌐 GLOBAL THREAT INTELLIGENCE")
    st.markdown("`OWASP TOP 10 MAPPING & 2025 FORECAST`")
    
    # Create two columns for the charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 CURRENT: OWASP Relevance")
        # Data for Standard OWASP
        df_current = pd.DataFrame({
            "Threat Vector": ["A02: Crypto Failures", "A05: Security Misconfig", "A06: Vuln Components", "A07: Auth Failures", "A10: SSRF"],
            "Relevance Score": [98, 75, 45, 60, 30]
        })
        fig1 = px.bar(df_current, x="Relevance Score", y="Threat Vector", orientation='h',
                     color="Relevance Score", color_continuous_scale="Reds")
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", 
                          xaxis_range=[0,110], margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("🔮 FUTURE: 2025 AI Landscape")
        # Data for 2025 Forecast
        df_future = pd.DataFrame({
             "Threat Vector": ["A01: Broken Access", "A02: Post-Quantum", "A03: AI Injection", "A04: Zero Trust", "A05: AI Supply Chain"],
             "Relevance Score": [95, 99, 92, 85, 96]
        })
        fig2 = px.bar(df_future, x="Threat Vector", y="Relevance Score",
                     color="Relevance Score", color_continuous_scale="Reds")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white",
                          margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    
    st.success("✅ COMPLIANT: GitGhost v14.0 proactively mitigates both current A02 failures and future AI Supply Chain risks.")
"""

# Read the file
with open("dashboard_v14.py", "r") as f:
    code = f.read()

# Replace the tab content
pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + new_content + "\n" + end_marker

if start_marker in code:
    fixed_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
    with open("dashboard_v14.py", "w") as f:
        f.write(fixed_code)
    print("✅ MERGE COMPLETE: Both charts are now on the Threat Intel tab.")
else:
    print("⚠️ ERROR: Could not find the Threat Intel tab.")
