import os
from PyPDF2 import PdfReader


pdf_directory = "app/data"

all_extracted_text = []


if not os.path.isdir(pdf_directory):
    print(f"Error: Directory '{pdf_directory}' does not exist.")
else:
    
    for filename in os.listdir(pdf_directory):
        
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_directory, filename)
            print(f"Processing: {file_path}")
            try:
                
                loader = PdfReader(file_path)
                
                
                pdf_text = []
                for page in loader.pages:
                    pdf_text.append(page.extract_text())
                
                
                all_extracted_text.append({
                    "filename": filename,
                    "text": "\n".join(pdf_text) 
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")