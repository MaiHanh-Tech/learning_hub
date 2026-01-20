"""
META-BLOCK: Translation Feature
Nguyên tắc: Single Responsibility - Chỉ lo dịch thuật
"""

import streamlit as st
from typing import Any, Dict, Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock 

class TranslationFeature:
    """
    Translation feature block
    
    Dependencies:
    - AIEngine: Để gọi AI dịch
    - I18nBlock: Để hiển thị UI đa ngôn ngữ
    """
    
    def __init__(self, ai_engine: AIEngine, i18n: Optional[I18nBlock] = None, config: Optional[ConfigBlock] = None):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config or {} # Lưu config lại (dù chưa dùng ngay)
    
    def t(self, key: str) -> str:
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
                self.t("source_language", "Ngôn ngữ nguồn:"),
                ["Chinese", "English", "Vietnamese", "Japanese", "Korean", "French"],
                index=0
            )
        
        with col2:
            target_lang_options = ["Vietnamese", "English", "Chinese", "French", "Japanese", "Korean"]
            if source_lang in target_lang_options:
                target_lang_options.remove(source_lang)
            
            target_lang = st.selectbox(
                self.t("target_language", "Ngôn ngữ đích:"),
                target_lang_options,
                index=0
            )
        
        with col3:
            style = st.selectbox(
                self.t("style", "Phong cách:"),
                ["Văn học", "Khoa học", "Đời thường", "Hàn lâm", "Thương mại"],
                index=0
            )
        
        # Mode selection
        mode = "Standard (Dịch câu)"
        if source_lang == "Chinese":
            mode = st.radio(
                self.t("mode", "Chế độ dịch:"),
                ["Standard (Dịch câu)", "Interactive (Học từ)"],
                horizontal=True
            )
        
        include_english = st.checkbox(self.t("include_english", "📖 Kèm Tiếng Anh"), value=True)
        
        st.divider()
        
        # Input
        text_input = st.text_area(
            self.t("input_text", "Nhập văn bản cần dịch:"),
            height=250,
            placeholder=self.t("input_placeholder", "Nhập hoặc dán văn bản vào đây...")
        )
        
        # Translate button
        if st.button(self.t("translate_button", "🚀 Dịch Ngay"), type="primary", use_container_width=True):
            if not text_input.strip():
                st.error(self.t("error_empty_input", "❌ Chưa nhập văn bản!"))
                return
            
            # Translation process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Call AI
                status_text.text(self.t("translating", "📄 Đang dịch..."))
                
                style_instructions = {
                    "Văn học": "Write in a literary style with rich imagery and elegant phrasing.",
                    "Khoa học": "Write in a scientific/technical style, precise and formal.",
                    "Đời thường": "Write in a casual, conversational everyday style.",
                    "Hàn lâm": "Write in an academic style with formal tone.",
                    "Thương mại": "Write in a business style, concise and professional."
                }
                
                additional = ""
                if include_english and target_lang != "English":
                    additional = "\nInclude English explanations for complex terms where appropriate."
                
                if mode == "Interactive (Học từ)":
                    additional += "\nFor each key phrase, provide breakdown: original, pinyin, literal translation, contextual meaning."
                
                prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Style instructions: {style_instructions.get(style, '')}
{additional}

Text:
{text_input}"""
                
                response = self.ai.generate(
                    prompt,
                    model_type="pro",
                    progress_callback=lambda msg: status_text.text(msg)
                )
                
                progress_bar.progress(1.0)
                
                if response.success:
                    status_text.success(f"✅ {self.t('success', 'Hoàn thành!')} (Provider: {response.provider}, {response.latency:.1f}s)")
                    st.balloons()
                    
                    # Display result
                    st.divider()
                    st.subheader(self.t("result", "📄 Kết quả dịch thuật"))
                    
                    st.markdown(response.content)
                    
                    # Save to history (optional, using centralized logger/utils if available)
                    try:
                        from utils.logger import AppLogger
                        logger = AppLogger()
                        logger.log_event(
                            "translation",
                            f"{source_lang} → {target_lang} ({style})",
                            text_input[:500]
                        )
                    except ImportError:
                        pass
                
                else:
                    status_text.error(f"❌ {response.error}")
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ {self.t('error_translation', 'Lỗi dịch thuật:')} {str(e)}")
                # st.exception(e)  # Debug only
            
            finally:
                progress_bar.empty()
