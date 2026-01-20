"""
META-BLOCK: Application Builder
Nguyên tắc: Fluent Interface + Dependency Injection
"""

from typing import Dict, Any, Optional
import streamlit as st
from core.i18n_block import I18nBlock
from core.auth_block import AuthBlock
from engines.ai_engine import AIEngine

class AppBuilder:
    """
    Xây dựng App theo kiểu LEGO
    
    Example:
        app = (
            AppBuilder()
            .with_i18n(["vi", "en", "zh"])
            .with_auth("password")
            .with_ai_engine()
            .with_feature("weaver")
            .with_feature("cfo")
            .build()
        )
    """
    
    def __init__(self):
        self.config = {
            "i18n": None,
            "auth": None,
            "ai_engine": None,
            "features": [],
            "sidebar": True,
            "theme": "light"
        }
        self._components = {}
    
    def with_i18n(self, languages: list, default: str = "vi"):
        """Block: Internationalization"""
        self._components["i18n"] = I18nBlock(languages, default)
        return self
    
    def with_auth(self, method: str = "password"):
        """Block: Authentication"""
        self._components["auth"] = AuthBlock(method)
        return self
    
    def with_ai_engine(self, default_model: str = "gemini-pro"):
        """Block: AI Engine"""
        self._components["ai_engine"] = AIEngine(default_model)
        return self
    
    def with_feature(self, feature_name: str, config: dict = None):
        """Block: Feature Module"""
        if "features" not in self._components:
            self._components["features"] = []
        self._components["features"].append({
            "name": feature_name,
            "config": config or {}
        })
        return self
    
    def with_sidebar(self, enabled: bool = True):
        """Block: Sidebar"""
        self.config["sidebar"] = enabled
        return self
    
    def build(self):
        """
        Lắp ráp toàn bộ blocks → Chạy App
        """
        # 1. Init core components
        if self._components.get("i18n"):
            st.session_state["i18n"] = self._components["i18n"]
        
        # 2. Auth check
        if self._components.get("auth"):
            auth_block = self._components["auth"]
            if not auth_block.check_login():
                auth_block.render_login_ui()
                st.stop()
        
        # 3. Render sidebar
        if self.config["sidebar"]:
            self._render_sidebar()
        
        # 4. Load selected feature
        selected_feature = st.session_state.get("selected_feature")
        if selected_feature:
            self._load_feature(selected_feature)
        
        return self
    
    def _render_sidebar(self):
        """Render sidebar với language selector + feature menu"""
        with st.sidebar:
            # Language selector (nếu có i18n block)
            if "i18n" in st.session_state:
                i18n = st.session_state["i18n"]
                i18n.render_language_selector()
            
            st.divider()
            
            # Feature menu
            st.title("🗂️ MENU")
            
            # User info (nếu có auth block)
            if "auth" in self._components:
                user = st.session_state.get("current_user", "Guest")
                st.info(f"👤 {user}")
            
            # Feature selection
            feature_names = [f["name"] for f in self._components.get("features", [])]
            if feature_names:
                selected = st.radio(
                    "Chọn công việc:",
                    feature_names,
                    format_func=lambda x: self._get_feature_label(x)
                )
                st.session_state["selected_feature"] = selected
            
            st.divider()
            
            # Logout button
            if st.button("Đăng xuất", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    
    def _get_feature_label(self, feature_name: str) -> str:
        """Map feature name → display label"""
        labels = {
            "weaver": "🧠 Cognitive Weaver",
            "cfo": "💰 CFO Controller"
        }
        return labels.get(feature_name, feature_name)
    
    def _load_feature(self, feature_name: str):
        """Dynamically load feature module"""
        try:
            if feature_name == "weaver":
                from features.weaver import WeaverFeature
                WeaverFeature(
                    ai_engine=self._components["ai_engine"],
                    i18n=self._components.get("i18n")
                ).render()
            
            elif feature_name == "cfo":
                from features.cfo import CFOFeature
                CFOFeature(
                    ai_engine=self._components["ai_engine"],
                    i18n=self._components.get("i18n")
                ).render()
        
        except Exception as e:
            st.error(f"❌ Lỗi load feature: {e}")
            st.exception(e)
