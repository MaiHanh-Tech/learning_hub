"""
META-BLOCK: I18n 
"""

import streamlit as st
from typing import Dict, List


class I18nBlock:
    def __init__(self, languages: List[str], default: str = "vi"):
        self.languages = languages
        self.default = default
        self.translations = self._load_translations()
        
        # Init session state
        if "current_language" not in st.session_state:
            st.session_state.current_language = default
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations"""
        return {
            "vi": self._get_vietnamese_dict(),
            "en": self._get_english_dict(),
            "zh": self._get_chinese_dict()
        }
    
    def _get_vietnamese_dict(self) -> Dict[str, str]:
        """Vietnamese translations"""
        return {
            # Common
            "logout": "Đăng xuất",
            "loading": "Đang tải...",
            "error": "Lỗi",
            "success": "Thành công",
            
            # Weaver Module
            "weaver_title": "🧠 Cognitive Weaver",
            "tab1": "📚 Phân Tích Sách",
            "tab2": "🗣️ Tranh Biện",
            "tab3": "⏳ Nhật Ký",
            
            "t1_up_doc": "Tải tài liệu (PDF/Docx)",
            "t1_btn": "🚀 PHÂN TÍCH NGAY",
            "t3_persona_label": "Chọn Đối Thủ:",
            "t3_input": "Nhập chủ đề tranh luận...",
            "t3_clear": "🗑️ Xóa Chat",
            
            # CFO Module
            "cfo_title": "💰 CFO Controller",
            "cfo_kpi": "📊 KPIs",
            "cfo_analysis": "📉 Phân Tích",
            "cfo_risk": "🕵️ Rủi Ro"
        }
    
    def _get_english_dict(self) -> Dict[str, str]:
        """English translations"""
        return {
            "logout": "Logout",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            
            "weaver_title": "🧠 Cognitive Weaver",
            "tab1": "📚 Book Analysis",
            "tab2": "🗣️ Debate Arena",
            "tab3": "⏳ History",
            
            "t1_up_doc": "Upload Document (PDF/Docx)",
            "t1_btn": "🚀 ANALYZE NOW",
            "t3_persona_label": "Choose Opponent:",
            "t3_input": "Enter debate topic...",
            "t3_clear": "🗑️ Clear Chat",
            
            "cfo_title": "💰 CFO Controller",
            "cfo_kpi": "📊 KPIs",
            "cfo_analysis": "📉 Analysis",
            "cfo_risk": "🕵️ Risk Detection"
        }
    
    def _get_chinese_dict(self) -> Dict[str, str]:
        """Chinese translations"""
        return {
            "logout": "登出",
            "loading": "加载中...",
            "error": "错误",
            "success": "成功",
            
            "weaver_title": "🧠 认知编织者",
            "tab1": "📚 书籍分析",
            "tab2": "🗣️ 辩论场",
            "tab3": "⏳ 历史记录",
            
            "t1_up_doc": "上传文档 (PDF/Docx)",
            "t1_btn": "🚀 立即分析",
            "t3_persona_label": "选择对手:",
            "t3_input": "输入辩论主题...",
            "t3_clear": "🗑️ 清除聊天",
            
            "cfo_title": "💰 CFO 控制器",
            "cfo_kpi": "📊 关键指标",
            "cfo_analysis": "📉 分析",
            "cfo_risk": "🕵️ 风险检测"
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
            "vi": "🇻🇳 Tiếng Việt",
            "en": "🇬🇧 English",
            "zh": "🇨🇳 中文"
        }
        
        # Mapping from display name to code
        display_to_code = {v: k for k, v in language_map.items()}
        code_to_display = language_map
        
        # Current selection
        current_display = code_to_display.get(
            st.session_state.current_language,
            language_map["vi"]
        )
        
        selected_display = st.selectbox(
            "🌐 Language",
            [language_map[lang] for lang in self.languages],
            index=[language_map[lang] for lang in self.languages].index(current_display),
            key="i18n_language_selector"
        )
        
        # Convert back to code
        selected_code = display_to_code[selected_display]
        
        if selected_code != st.session_state.current_language:
            st.session_state.current_language = selected_code
            st.rerun()
