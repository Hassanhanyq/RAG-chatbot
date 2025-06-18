import os
from typing import List, Dict
from PyPDF2 import PdfReader

def load_all_pdfs(pdf_directory: str) -> List[Dict[str, str]]:
    """
    Load and extract text from all PDF files in a directory.

    Args:
        pdf_directory (str): Path to the directory containing PDF files.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing:
            - 'filename': the name of the PDF file.
            - 'text': the full extracted text from the PDF.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    if not os.path.isdir(pdf_directory):
        raise FileNotFoundError(f"Directory '{pdf_directory}' does not exist.")
    
    all_text = []

    for filename in os.listdir(pdf_directory):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(pdf_directory, filename)
            print(f"Processing: {file_path}")
            try:
                reader = PdfReader(file_path)
                pdf_text = [page.extract_text() for page in reader.pages if page.extract_text()]
                all_text.append({
                    "filename": filename,
                    "text": "\n".join(pdf_text)
                })
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return all_text