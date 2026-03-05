import re

with open("GITGHOST_PROJECT_REPORT_V15.tex", "r", encoding="utf-8") as f:
    text = f.read()

# We want to replace \chapter{XYZ} with 
# \chapter{XYZ}
# \begin{center}
#     {\Large \textbf{\thechapter. XYZ} \par}
# \end{center}
# \vspace{1cm}
# But ONLY for the main chapters, not if it's already done.

def repl(match):
    title = match.group(1)
    return f'\\chapter{{{title}}}\n\\begin{{center}}\n    {{\\Large \\textbf{{\\thechapter. {title.upper()}}} \\par}}\n\\end{{center}}\n\\vspace{{1cm}}'

new_text = re.sub(r'\\chapter\{([^}]+)\}(?!\s*\\begin\{center\}\s*\{\\Large)', repl, text)

# Also check for BIBLIOGRAPHY (is it chapter or just text?)
# Currently looking at the file, there are \chapter{} commands!

with open("GITGHOST_PROJECT_REPORT_V15.tex", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Done replacing.")
