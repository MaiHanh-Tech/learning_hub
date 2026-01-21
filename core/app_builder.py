"""
META-BLOCK: Application Builder (Fixed)
Bỏ debug messages, fix i18n, add CFO support
"""

from typing import Dict, Any, Optional
import streamlit as st

# Core blocks
from core.i18n_block import I18nBlock
from core.auth_block import AuthBlock
from core.config_block import ConfigBlock

# Engines
from engines.ai_engine import AIEngine
from engines.embedding_engine import EmbeddingEngine


class AppBuilder:
    def __init__(self):
        self._components: Dict[str, Any] = {}
        self.config = {
            "sidebar": True,
            "theme": "light",
            "default_feature": None
        }
    
    def with_config(self):
        """Block: Centralized Configuration"""
        self._components["config"] = ConfigBlock()
        st.session_state["config"] = self._components["config"]
        return self
    
    def with_i18n(self, languages: list = ["vi", "en", "zh"], default: str = "vi"):
        """Block: Internationalization"""
        self._components["i18n"] = I18nBlock(languages, default)
        st.session_state["i18n"] = self._components["i18n"]
        return self
    
    def with_auth(self, method: str = "password"):
        """Block: Authentication"""
        self._components["auth"] = AuthBlock(method)
        return self
    
    def with_ai_engine(self, default_model: str = "gemini-pro"):
        """Block: AI Engine"""
        config = self._components.get("config")
        self._components["ai_engine"] = AIEngine(
            default_model=default_model,
            config=config
        )
        
        # Auto-create embedding engine
        self._components["embedding_engine"] = EmbeddingEngine()
        
        return self
    
    def with_feature(self, feature_name: str, config: dict = None):
        """Đăng ký feature"""
        if "features" not in self._components:
            self._components["features"] = []
        self._components["features"].append({
            "name": feature_name,
            "config": config or {}
        })
        return self
    
    def with_sidebar(self, enabled: bool = True):
        """Bật/tắt sidebar"""
        self.config["sidebar"] = enabled
        return self
    
    def with_default_feature(self, feature_name: str):
        """Feature mặc định"""
        self.config["default_feature"] = feature_name
        return self
    
    def build(self):
        """Lắp ráp và chạy app"""
        st.session_state["components"] = self._components
        
        # 1. Authentication
        if "auth" in self._components:
            auth_block = self._components["auth"]
            if not auth_block.check_login():
                auth_block.render_login_ui()
                st.stop()
        
        # 2. Sidebar
        if self.config["sidebar"]:
            self._render_sidebar()
        
        # 3. Load feature
        selected_feature = st.session_state.get("selected_feature")
        if not selected_feature and self.config.get("default_feature"):
            selected_feature = self.config["default_feature"]
            st.session_state["selected_feature"] = selected_feature
        
        if selected_feature:
            self._load_feature(selected_feature)
        
        return self
    
    def _render_sidebar(self):
        """Render sidebar"""
        with st.sidebar:
            # Header
            st.markdown("# 🧠 Cognitive Weaver")
            st.caption("*Meta-Blocks Architecture*")
            
            st.divider()
            
            # Language selector
            if "i18n" in st.session_state:
                st.session_state["i18n"].render_language_selector()
            
            st.divider()
            
            # User info
            if "auth" in self._components:
                user = st.session_state.get("current_user", "Guest")
                is_admin = st.session_state.get("is_admin", False)
                role_badge = "🔑 Admin" if is_admin else "👤 User"
                
                st.info(f"{role_badge}\n**{user}**")
            
            st.divider()
            
            # Menu
            st.markdown("### 📂 MODULES")
            
            feature_list = self._components.get("features", [])
            if feature_list:
                feature_names = [f["name"] for f in feature_list]
                
                current = st.session_state.get("selected_feature", feature_names[0])
                try:
                    idx = feature_names.index(current)
                except ValueError:
                    idx = 0
                
                selected = st.radio(
                    "Chọn module:",
                    feature_names,
                    format_func=self._get_feature_label,
                    index=idx,
                    label_visibility="collapsed"
                )
                
                if selected != st.session_state.get("selected_feature"):
                    st.session_state["selected_feature"] = selected
                    st.rerun()
            
            st.divider()
            
            # Logout
            if st.button("🚪 Đăng xuất", type="secondary", use_container_width=True):
                if "auth" in self._components:
                    self._components["auth"].logout()
                st.session_state.clear()
                st.rerun()
    
    def _get_feature_label(self, feature_name: str) -> str:
        """Map feature name to label"""
        labels = {
            "weaver": "🧠 Cognitive Weaver",
            "cfo": "💰 CFO Controller"
        }
        return labels.get(feature_name, feature_name.capitalize())
    
    def _load_feature(self, feature_name: str):
        """Load feature"""
        try:
            # Weaver
            if feature_name == "weaver":
                from features.weaver import WeaverFeature
                
                feature = WeaverFeature(
                    ai_engine=self._components.get("ai_engine"),
                    embedding_engine=self._components.get("embedding_engine"),
                    i18n=self._components.get("i18n"),
                    config=self._components.get("config")
                )
                feature.render()
            
            # CFO
            elif feature_name == "cfo":
                from features.cfo_feature import CFOFeature
                
                feature = CFOFeature(
                    ai_engine=self._components.get("ai_engine"),
                    i18n=self._components.get("i18n"),
                    config=self._components.get("config")
                )
                feature.render()
            
            else:
                st.warning(f"Feature '{feature_name}' chưa được triển khai")
        
        except ImportError as e:
            st.error(f"❌ Import lỗi: {str(e)}")
            st.info("Kiểm tra: folder features/ có file tương ứng?")
        
        except Exception as e:
            st.error(f"❌ Lỗi render feature '{feature_name}': {str(e)}")
