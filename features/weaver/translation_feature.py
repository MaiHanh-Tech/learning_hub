"""
META-BLOCK: Translation Feature
Nguyên tắc: Single Responsibility - Chỉ lo dịch thuật
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock

class TranslationFeature:
    """
    Translation feature block
    
    Dependencies:
    - AIEngine: Để gọi AI dịch
    - I18nBlock: Để hiển thị UI đa ngôn ngữ
    """
    
    def __init__(self, ai_engine: AIEngine, i18n: Optional[I18nBlock] = None):
        self.ai = ai_engine
        self.i18n = i18n
    
    def t(self, key: str) -> str:
        """Helper để translate UI"""
        if self.i18n:
            return self.i18n.t(key, key)
        return key
    
    def render(self):
        """Render translation UI"""
        st.subheader(self.t("weaver_translator"))
        
        # Configuration
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source_lang = st.selectbox(
                "Ngôn ngữ nguồn:",
                ["Chinese", "English", "Vietnamese"],
                index=0
            )
        
        with col2:
            target_lang = st.selectbox(
                "Ngôn ngữ đích:",
                ["Vietnamese", "English", "Chinese", "French", "Japanese", "Korean"],
                index=0
            )
        
        with col3:
            style = st.selectbox(
                "Phong cách:",
                ["Văn học", "Khoa học", "Đời thường", "Hàn lâm", "Thương mại"],
                index=0
            )
        
        # Mode selection
        if source_lang == "Chinese":
            mode = st.radio(
                "Chế độ dịch:",
                ["Standard (Dịch câu)", "Interactive (Học từ)"],
                horizontal=True
            )
        else:
            mode = "Standard (Dịch câu)"
        
        include_english = st.checkbox("📖 Kèm Tiếng Anh", value=True)
        
        st.divider()
        
        # Input
        text_input = st.text_area(
            "Nhập văn bản cần dịch:",
            height=250,
            placeholder="Nhập hoặc dán văn bản vào đây..."
        )
        
        # Translate button
        if st.button("🚀 Dịch Ngay", type="primary", use_container_width=True):
            if not text_input.strip():
                st.error("❌ Chưa nhập văn bản!")
                return
            
            # Translation process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Call AI
                status_text.text("📄 Đang dịch...")
                
                style_instructions = {
                    "Văn học": "Write in a literary style with rich imagery and elegant phrasing.",
                    "Khoa học": "Write in a scientific/technical style, precise and formal.",
                    "Đời thường": "Write in a casual, conversational everyday style.",
                    "Hàn lâm": "Write in an academic style with formal tone.",
                    "Thương mại": "Write in a business style, concise and professional."
                }
                
                prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Style instructions: {style_instructions.get(style, '')}

Text:
{text_input}"""
                
                response = self.ai.generate(
                    prompt,
                    model_type="pro",
                    progress_callback=lambda msg: status_text.text(msg)
                )
                
                progress_bar.progress(1.0)
                
                if response.success:
                    status_text.success(f"✅ Hoàn thành! (Provider: {response.provider}, {response.latency:.1f}s)")
