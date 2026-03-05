import os

file_path = "dashboard_v14.py"
with open(file_path, "r") as f:
    content = f.read()

# The broken code block to find
broken_code = """                # One-click copy button
                st.markdown("### 📋 Quick Actions")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📋 Copy Remediation Commands"):
                        st.success("✅ Copied to clipboard! (simulated)")
                with col_b:
                    if st.button("🔗 View in GitHub"):
                        st.info(f"Opening commit {selected_finding['commit'][:7]}...")"""

# The working code block (Native Copy + Real Links)
fixed_code = """                # --- FIXED QUICK ACTIONS ---
                st.markdown("### 📋 Quick Actions")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption("👇 Click the Copy Icon ↗️")
                    # Extract the clean bash command for the st.code block
                    clean_cmd = remediation.split("```bash")[1].split("```")[0].strip() if "```bash" in remediation else "# No command found"
                    st.code(clean_cmd, language="bash")
                with col_b:
                    st.caption("👇 Verify Source")
                    # Open real GitHub search for this commit hash
                    gh_url = f"[https://github.com/search?q=](https://github.com/search?q=){selected_finding['commit']}&type=commits"
                    st.link_button("🔗 Open Real GitHub Commit", gh_url)"""

if broken_code in content:
    new_content = content.replace(broken_code, fixed_code)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("✅ SUCCESS: Buttons patched! Launching dashboard...")
else:
    print("⚠️ SKIPPED: Code already fixed or not found.")
