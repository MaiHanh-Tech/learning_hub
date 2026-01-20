"""
META-BLOCK: Application Builder
Nguyên tắc: Fluent Interface + Dependency Injection
"""

from typing import Dict, Any, Optional
import streamlit as st
import importlib

# Core blocks
from core.i18n_block import I18nBlock
from core.auth_block import AuthBlock
from core.config_block import ConfigBlock

# Engines
from engines.ai_engine import AIEngine

class AppBuilder:
    """
    Xây dựng App theo kiểu LEGO - Fluent Interface
    
    Cách dùng trong app.py:
        app = (
            AppBuilder()
            .with_config()                  # Thêm config block
            .with_i18n(["vi", "en", "zh"])
            .with_auth("password")
            .with_ai_engine("gemini-pro")
            .with_features("weaver")
            .with_features("cfo")
            .with_sidebar(enabled=True)
            .build()
        )
    """
    
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
            config=config  # Truyền config nếu engine cần
        )
        return self
    
    def with_feature(self, feature_name: str, config: dict = None):
        """Đăng ký một feature module"""
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
        """Feature mặc định khi mới vào app"""
        self.config["default_feature"] = feature_name
        return self
    
    def build(self):
        """
        Lắp ráp và chạy ứng dụng
        """
        # Lưu toàn bộ components vào session_state để các feature truy cập dễ dàng
        st.session_state["components"] = self._components
        
        # 1. Kiểm tra authentication (nếu có)
        if "auth" in self._components:
            auth_block = self._components["auth"]
            if not auth_block.check_login():
                auth_block.render_login_ui()
                st.stop()
        
        # 2. Render sidebar (nếu bật)
        if self.config["sidebar"]:
            self._render_sidebar()
        
        # 3. Load feature được chọn (hoặc default)
        selected_feature = st.session_state.get("selected_feature")
        if not selected_feature and self.config.get("default_feature"):
            selected_feature = self.config["default_feature"]
            st.session_state["selected_feature"] = selected_feature
        
        if selected_feature:
            self._load_feature(selected_feature)
        
        return self
    
    def _render_sidebar(self):
        """Render sidebar chung cho toàn app"""
        with st.sidebar:
            # Language selector
            if "i18n" in st.session_state:
                st.session_state["i18n"].render_language_selector()
            
            st.divider()
            
            # User info
            if "auth" in self._components:
                user = st.session_state.get("current_user", "Guest")
                is_admin = st.session_state.get("is_admin", False)
                role_text = " (Admin)" if is_admin else ""
                st.info(f"👤 {user}{role_text}")
            
            # Menu chọn feature
            st.title("🗂️ MENU")
            
            feature_list = self._components.get("features", [])
            if feature_list:
                feature_names = [f["name"] for f in feature_list]
                selected = st.radio(
                    "Chọn module:",
                    feature_names,
                    format_func=self._get_feature_label,
                    index=feature_names.index(st.session_state.get("selected_feature", feature_names[0]))
                )
                if selected != st.session_state.get("selected_feature"):
                    st.session_state["selected_feature"] = selected
                    st.rerun()
            
            st.divider()
            
            # Logout
            if st.button("🚪 Đăng xuất", type="secondary", use_container_width=True):
                if "auth" in self._components:
                    self._components["auth"].logout()  # Nếu auth_block có hàm logout
                st.session_state.clear()
                st.rerun()
    
    def _get_feature_label(self, feature_name: str) -> str:
        """Map tên feature → label hiển thị đẹp"""
        labels = {
            "weaver": "🧠 Cognitive Weaver",
            "cfo":    "💰 CFO Controller"
            # Thêm các module khác sau này ở đây
        }
        return labels.get(feature_name, feature_name.capitalize())
    
    def _load_feature(self, feature_name: str):
        """Load động feature từ thư mục features"""
        try:
            # Tìm trong features/weaver hoặc features/cfo
            module_path = f"features.weaver.{feature_name}_feature" if feature_name in ["rag", "translation", "debate", "voice", "history"] else \
                          f"features.cfo.{feature_name}_feature"
            
            # Import động
            module = importlib.import_module(module_path)
            feature_class_name = "".join(word.capitalize() for word in feature_name.split("_")) + "Feature"
            feature_class = getattr(module, feature_class_name)
            
            # Khởi tạo với dependencies
            feature_instance = feature_class(
                ai_engine=self._components.get("ai_engine"),
                i18n=self._components.get("i18n"),
                config=self._components.get("config")
                # Thêm các dependency khác nếu feature cần (voice_engine, db_block, ...)
            )
            
            feature_instance.render()
            
        except ImportError as e:
            st.error(f"❌ Không tìm thấy module feature '{feature_name}': {e}")
        except AttributeError as e:
            st.error(f"❌ Không tìm thấy class trong module '{feature_name}': {e}")
        except Exception as e:
            st.error(f"❌ Lỗi khi render feature '{feature_name}': {str(e)}")
            # st.exception(e)  # Bật khi debug, tắt khi production
