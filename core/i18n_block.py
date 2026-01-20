"""
META-BLOCK: I18n (Internationalization)
Chức năng: Quản lý đa ngôn ngữ TOÀN HỆ THỐNG
"""

import streamlit as st
from typing import Dict, List

class I18nBlock:
    """
    [Inference] Block này tập trung hóa việc dịch UI
    
    Lợi ích:
    - Mọi module dùng chung 1 nguồn translation
    - Thêm ngôn ngữ mới chỉ cần sửa 1 file
    - AI dễ dàng generate translation dict
    """
    
    def __init__(self, languages: List[str], default: str = "vi"):
        self.languages = languages
        self.default = default
        
        # Load translation dictionaries
        self.translations = self._load_translations()
        
        # Init session state
        if "current_language" not in st.session_state:
            st.session_state.current_language = default
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Load tất cả translations
        
        Structure:
        {
            "vi": {"header": "Tiêu đề", "button": "Nút bấm"},
            "en": {"header": "Header", "button": "Button"}
        }
        """
        return {
            "vi": self._get_vietnamese_dict(),
            "en": self._get_english_dict(),
            "zh": self._get_chinese_dict()
        }
    
    def _get_vietnamese_dict(self) -> Dict[str, str]:
        """Vietnamese translations (TOÀN HỆ THỐNG)"""
        return {
            # Common
            "logout": "Đăng xuất",
            "loading": "Đang tải...",
            "error": "Lỗi",
            "success": "Thành công",
            
            # Weaver Module
            "weaver_title": "🧠 Cognitive Weaver",
            "weaver_rag": "📚 Phân Tích Sách",
            "weaver_translator": "✍️ Dịch Giả",
            "weaver_debate": "🗣️ Tranh Biện",
            "weaver_voice": "🎙️ Phòng Thu AI",
            "weaver_history": "⏳ Nhật Ký",
            
            # CFO Module
            "cfo_title": "💰 CFO Controller",
            "cfo_kpi": "📊 KPIs",
            "cfo_analysis": "📉 Phân Tích",
            "cfo_risk": "🕵️ Rủi Ro",
            "cfo_forecast": "🔮 Dự Báo"
        }
    
    def _get_english_dict(self) -> Dict[str, str]:
        """English translations"""
        return {
            "logout": "Logout",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            
            "weaver_title": "🧠 Cognitive Weaver",
            "weaver_rag": "📚 Book Analysis",
            "weaver_translator": "✍️ Translator",
            "weaver_debate": "🗣️ Debate Arena",
            "weaver_voice": "🎙️ AI Studio",
            "weaver_history": "⏳ History",
            
            "cfo_title": "💰 CFO Controller",
            "cfo_kpi": "📊 KPIs",
            "cfo_analysis": "📉 Analysis",
            "cfo_risk": "🕵️ Risk Detection",
            "cfo_forecast": "🔮 Forecast"
        }
    
    def _get_chinese_dict(self) -> Dict[str, str]:
        """Chinese translations"""
        return {
            "logout": "登出",
            "loading": "加载中...",
            "error": "错误",
            "success": "成功",
            
            "weaver_title": "🧠 认知编织者",
            "weaver_rag": "📚 书籍分析",
            "weaver_translator": "✍️ 翻译",
            "weaver_debate": "🗣️ 辩论场",
            "weaver_voice": "🎙️ AI 录音室",
            "weaver_history": "⏳ 历史记录"
        }
    
    def t(self, key: str, fallback: str = None) -> str:
        """
        Translate a key
        
        Args:
            key: Translation key
            fallback: Text to show if key not found
        
        Returns:
            Translated string
        """
        lang = st.session_state.current_language
        return self.translations.get(lang, {}).get(key, fallback or key)
    
    def render_language_selector(self):
        """Render language selector widget"""
        language_map = {
            "vi": "Tiếng Việt",
            "en": "English",
            "zh": "中文"
        }
        
        selected = st.selectbox(
            "🌐 Language",
            self.languages,
            format_func=lambda x: language_map.get(x, x),
            index=self.languages.index(st.session_state.current_language)
        )
        
        if selected != st.session_state.current_language:
            st.session_state.current_language = selected
            st.rerun()
