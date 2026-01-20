"""
META-BLOCK: RAG Feature
Nguyên tắc: Single Responsibility - Chỉ lo RAG và Knowledge Graph
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from engines.embedding_engine import EmbeddingEngine
from engines.kg_engine import KnowledgeGraphEngine
from core.i18n_block import I18nBlock
from services.blocks.file_processor import doc_file, clean_pdf_text

class RagFeature:
    """
    RAG feature block
    
    Dependencies:
    - AIEngine
    - EmbeddingEngine
    - KnowledgeGraphEngine
    - I18nBlock (optional)
    """
    
    def __init__(self, ai_engine: AIEngine, embedding_engine: EmbeddingEngine, kg_engine: KnowledgeGraphEngine, i18n: Optional[I18nBlock] = None):
        self.ai = ai_engine
        self.embedding = embedding_engine
        self.kg = kg_engine
        self.i18n = i18n
    
    def t(self, key: str, default: str = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def render(self):
        """Render RAG UI"""
        st.subheader(self.t("weaver_rag", "📚 Phân Tích Sách"))
        
        # Excel upload
        excel_file = st.file_uploader(self.t("t1_up_excel", "1. Kết nối Kho Sách (Excel)"), type=["xlsx"])
        if excel_file:
            self.kg.upgrade_from_excel(excel_file)
        
        # Doc upload
        doc_file_uploader = st.file_uploader(self.t("t1_up_doc", "2. Tài liệu mới (PDF/Docx)"), type=["pdf", "docx"])
        if doc_file_uploader:
            raw_text = doc_file(doc_file_uploader)
            cleaned_text = clean_pdf_text(raw_text)
            if st.button(self.t("t1_btn", "🚀 PHÂN TÍCH NGAY")):
                with st.spinner(self.t("t1_analyzing", "Đang phân tích...")):
                    analysis = self.ai.analyze_document_streamlit(doc_file_uploader.name, cleaned_text)
                    st.markdown(analysis)
        
        # Graph render
        st.subheader(self.t("t1_graph_title", "🪐 Vũ trụ Sách"))
        graph_component = self.kg.render_graph()
        st.components.v1.html(graph_component.to_html(), height=600)
