# backend/ingest.py
import os
import json
from PyPDF2 import PdfReader
# langchain splitters moved to separate package
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = splitter.split_text(text)
    chunks = [c.strip() for c in chunks if len(c.strip()) > 30]
    return chunks

def ingest_pdf(uploaded_pdf_path: str, output_json: str = "data/chunks.json") -> int:
    text = extract_text_from_pdf(uploaded_pdf_path)
    if not text.strip():
        raise ValueError("No text could be extracted from PDF.")
    chunks = chunk_text(text)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    return len(chunks)

if __name__ == "__main__":
    print("Run ingest via Streamlit UI (ingest_pdf).")
