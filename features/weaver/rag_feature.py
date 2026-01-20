"""
META-BLOCK: RAG Feature
Nguyên tắc: Single Responsibility - Chỉ lo RAG và Knowledge Graph
"""

import streamlit as st
from typing import Any, Dict, Optional
from engines.ai_engine import AIEngine
from engines.embedding_engine import EmbeddingEngine
from engines.kg_engine import KnowledgeGraphEngine
from core.i18n_block import I18nBlock
from utils.file_processor import doc_file, clean_pdf_text


class RagFeature:
    """
    RAG feature block
    
    Dependencies:
    - AIEngine: gọi AI phân tích
    - EmbeddingEngine: tạo vector
    - KnowledgeGraphEngine: quản lý KG sách
    - I18nBlock: đa ngôn ngữ UI (optional)
    """
    
    def __init__(
        self,
        ai_engine: AIEngine,
        embedding_engine: EmbeddingEngine,
        kg_engine: KnowledgeGraphEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[dict] = None  # Optional config nếu cần limit
    ):
        self.ai = ai_engine
        self.embedding = embedding_engine
        self.kg = kg_engine
        self.i18n = i18n
        self.config = config or {}
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """Helper dịch UI"""
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def render(self):
        """Render RAG UI"""
        st.subheader(self.t("weaver_rag", "📚 Phân Tích Sách & Knowledge Graph"))
        
        # 1. Upload Excel để upgrade KG (kho sách)
        st.markdown(self.t("t1_up_excel_desc", "1. Kết nối kho sách từ Excel (tên sách + cảm nhận)"))
        excel_file = st.file_uploader(
            self.t("t1_up_excel", "Chọn file Excel (.xlsx)"),
            type=["xlsx"],
            help=self.t("t1_up_excel_help", "File cần có cột: Tên sách, CẢM NHẬN, Tác giả, Tags")
        )
        
        if excel_file:
            with st.spinner(self.t("t1_upgrading_kg", "Đang nâng cấp Knowledge Graph...")):
                try:
                    success_count = self.kg.upgrade_from_excel(excel_file)
                    st.success(f"✅ Đã thêm {success_count} sách vào Knowledge Graph!")
                except Exception as e:
                    st.error(f"❌ Lỗi nâng cấp KG từ Excel: {str(e)}")
                    st.info("Kiểm tra file Excel có cột 'Tên sách' và 'CẢM NHẬN' không?")
        
        st.divider()
        
        # 2. Upload tài liệu mới để phân tích (PDF/Docx)
        st.markdown(self.t("t1_up_doc_desc", "2. Phân tích tài liệu mới (PDF, Docx, TXT)"))
        doc_file_uploader = st.file_uploader(
            self.t("t1_up_doc", "Chọn tài liệu cần phân tích"),
            type=["pdf", "docx", "txt", "md"],
            help=self.t("t1_up_doc_help", "Tài liệu sẽ được clean và phân tích bằng AI")
        )
        
        if doc_file_uploader:
            with st.spinner(self.t("t1_processing_doc", "Đang xử lý tài liệu...")):
                try:
                    raw_text = doc_file(doc_file_uploader)
                    if not raw_text.strip():
                        st.warning("Tài liệu rỗng hoặc không đọc được.")
                        return
                    
                    cleaned_text = clean_pdf_text(raw_text)
                    st.info(f"Đã xử lý: {len(cleaned_text):,} ký tự")
                    
                    if st.button(self.t("t1_btn", "🚀 PHÂN TÍCH NGAY"), type="primary"):
                        with st.spinner(self.t("t1_analyzing", "Đang phân tích bằng AI...")):
                            try:
                                # Gọi AI phân tích (dùng method từ ai_engine nếu có)
                                analysis = self.ai.analyze_document_streamlit(
                                    doc_file_uploader.name,
                                    cleaned_text
                                )
                                st.markdown("### Kết quả phân tích")
                                st.markdown(analysis)
                            except AttributeError:
                                st.error("AI engine chưa có method analyze_document_streamlit. Cần migrate từ ai_core.py cũ.")
                            except Exception as e:
                                st.error(f"❌ Lỗi phân tích: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Lỗi đọc tài liệu: {str(e)}")
        
        st.divider()
        
        # 3. Render Knowledge Graph
        st.subheader(self.t("t1_graph_title", "🪐 Vũ trụ Sách (Knowledge Graph)"))
        try:
            graph_component = self.kg.render_graph()
            if graph_component:
                st.components.v1.html(graph_component.to_html(), height=600)
            else:
                st.info("Knowledge Graph chưa có dữ liệu sách. Upload Excel để bắt đầu.")
        except Exception as e:
            st.error(f"❌ Lỗi render graph: {str(e)}")
            st.info("Kiểm tra: streamlit-agraph đã install? Import có đúng 'from streamlit_agraph import agraph, Node, Edge'?")
