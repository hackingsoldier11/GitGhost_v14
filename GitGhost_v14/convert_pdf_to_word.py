
import win32com.client
import os
import sys

# Absolute paths
pdf_path = os.path.abspath(r"d:\PROJRCT  CAS\GitGhost\GitGhost_Final_v14\GitGhost_v14\GITGHOST_PROJECT_REPORT_V15.pdf")
docx_path = os.path.abspath(r"d:\PROJRCT  CAS\GitGhost\GitGhost_Final_v14\GitGhost_v14\GITGHOST_PROJECT_REPORT_V15.docx")

print(f"Converting {pdf_path} to {docx_path}...")

if not os.path.exists(pdf_path):
    print(f"Error: Source file not found: {pdf_path}")
    sys.exit(1)

try:
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    
    # Open the PDF
    doc = word.Documents.Open(pdf_path)
    
    # Save as DOCX
    # wdFormatXMLDocument = 16
    doc.SaveAs2(docx_path, FileFormat=16)
    
    doc.Close()
    word.Quit()
    print("Conversion Successful!")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
