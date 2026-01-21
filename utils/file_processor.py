"""
META-BLOCK: File Processor Utility (Enhanced)
Nguyên tắc: Single Responsibility - Đọc file (PDF, Docx, Text, Excel, Markdown)
"""

from pypdf import PdfReader
from docx import Document
import pandas as pd
import re


def doc_file(uploaded_file):
    """
    Đọc file upload từ Streamlit
    
    Supported formats:
    - PDF
    - DOCX
    - TXT, MD, HTML
    - XLSX (Excel)
    
    Returns:
        str: Nội dung file dưới dạng text
    """
    if not uploaded_file:
        return ""
    
    ext = uploaded_file.name.split('.')[-1].lower()
    
    try:
        # PDF
        if ext == "pdf":
            reader = PdfReader(uploaded_file)
            text = "\n".join([
                page.extract_text() or ""
                for page in reader.pages
            ])
            return text
        
        # DOCX
        elif ext == "docx":
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        
        # Excel
        elif ext in ["xlsx", "xls"]:
            # Đọc tất cả sheets
            df_dict = pd.read_excel(uploaded_file, sheet_name=None)
            
            text_parts = []
            for sheet_name, df in df_dict.items():
                text_parts.append(f"=== Sheet: {sheet_name} ===\n")
                
                # Convert DataFrame to readable text
                text_parts.append(df.to_string(index=False))
                text_parts.append("\n\n")
            
            return "\n".join(text_parts)
        
        # Text-based files
        elif ext in ["txt", "md", "html"]:
            content = uploaded_file.read()
            
            # Try decode as UTF-8
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to latin-1
                return content.decode("latin-1")
    
    except Exception as e:
        return f"[Error reading file: {str(e)}]"
    
    return ""


def clean_pdf_text(text):
    """
    Clean text extracted from PDF
    
    Args:
        text: Raw text from PDF
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Fix hyphenated words split across lines
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Replace single newlines with space (keep paragraph breaks)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Fix bullet points
    text = text.replace('•', '•')
    
    # Common PDF split fixes
    text = text.replace('impor tant', 'important')
    text = text.replace('scienti c', 'scientific')
    text = text.replace('di erent', 'different')
    
    return text.strip()


def split_smart_chunks(text, chunk_size=1500, max_total_chars=50000):
    """
    Split text into smart chunks (by sentences)
    
    Args:
        text: Input text
        chunk_size: Max chars per chunk
        max_total_chars: Max total chars to process
    
    Returns:
        list: List of text chunks
    """
    if not text:
        return []
    
    # Truncate if too long
    if len(text) > max_total_chars:
        text = text[:max_total_chars]
    
    # Split by sentences (simple regex)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])', text)
    
    chunks = []
    current = ""
    
    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += sentence + " "
        else:
            if current:
                chunks.append(current.strip())
            current = sentence + " "
    
    if current:
        chunks.append(current.strip())
    
    return chunks
