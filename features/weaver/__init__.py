"""
META-BLOCK: Weaver Feature Aggregator
Nguyên tắc: Composition - Ghép các sub-features thành module lớn
"""

import streamlit as st
from typing import Optional, Dict
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock  # Thêm dependency config

# Import các sub-feature (tất cả đều ở cùng folder features/weaver/)
from .rag_feature import RagFeature
from .translation_feature import TranslationFeature
from .debate_feature import DebateFeature
from .voice_feature import VoiceFeature
from .history_feature import HistoryFeature


class WeaverFeature:
    """
    Aggregator cho tất cả sub-features của Weaver
    
    Dependencies:
    - AIEngine: dùng chung cho tất cả sub-feature
    - I18nBlock: đa ngôn ngữ UI (optional)
    - ConfigBlock: cấu hình toàn cục (optional, inject vào sub-feature sau này)
    """
    
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config
        
        # Khởi tạo tất cả sub-features (composition)
        self.features: Dict[str, Any] = self._init_features()
    
    def _init_features(self) -> Dict[str, Any]:
        """Khởi tạo các sub-feature, truyền chung dependencies"""
        common_kwargs = {
            "ai_engine": self.ai,
            "i18n": self.i18n,
            "config": self.config
        }
        
        return {
            "rag": RagFeature(**common_kwargs),
            "translation": TranslationFeature(**common_kwargs),
            "debate": DebateFeature(**common_kwargs),
            "voice": VoiceFeature(**common_kwargs),
            "history": HistoryFeature(**common_kwargs)
        }
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """Helper dịch UI"""
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def render(self):
        """Render toàn bộ Weaver UI bằng tabs"""
        st.title(self.t("weaver_title", "🧠 Cognitive Weaver"))
        
        # Tạo tabs theo thứ tự cố định
        tab_labels = [
            self.t("weaver_rag", "📚 RAG & Phân tích sách"),
            self.t("weaver_translator", "✍️ Dịch Giả"),
            self.t("weaver_debate", "🗣️ Tranh Biện"),
            self.t("weaver_voice", "🎙️ Phòng Thu AI"),
            self.t("weaver_history", "⏳ Nhật Ký")
        ]
        
        tabs = st.tabs(tab_labels)
        
        # Render từng tab với try-except để tránh crash nếu một tab lỗi
        with tabs[0]:
            try:
                self.features["rag"].render()
            except Exception as e:
                st.error(f"Lỗi tab RAG: {str(e)}")
        
        with tabs[1]:
            try:
                self.features["translation"].render()
            except Exception as e:
                st.error(f"Lỗi tab Dịch Giả: {str(e)}")
        
        with tabs[2]:
            try:
                self.features["debate"].render()
            except Exception as e:
                st.error(f"Lỗi tab Tranh Biện: {str(e)}")
        
        with tabs[3]:
            try:
                self.features["voice"].render()
            except Exception as e:
                st.error(f"Lỗi tab Voice: {str(e)}")
        
        with tabs[4]:
            try:
                self.features["history"].render()
            except Exception as e:
                st.error(f"Lỗi tab History: {str(e)}")
