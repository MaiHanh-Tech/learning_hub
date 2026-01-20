# utils/file_processor.py
from pypdf import PdfReader
from docx import Document
import re
import pypinyin

def doc_file(uploaded_file):
    if not uploaded_file: return ""
    ext = uploaded_file.name.split('.')[-1].lower()
    try:
        if ext == "pdf":
            reader = PdfReader(uploaded_file)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif ext == "docx":
            doc = Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext in ["txt", "md", "html"]:
            return str(uploaded_file.read(), "utf-8")
    except:
        return ""
    return ""

def clean_pdf_text(text):
    if not text: return ""
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('•', '•')
    text = text.replace('impor tant', 'important').replace('scienti c', 'scientific')
    return text.strip()

# Các hàm khác nếu cần: split_smart_chunks, convert_to_pinyin
