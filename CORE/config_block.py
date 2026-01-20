"""
META-BLOCK: Configuration Block
Nguyên tắc: Centralized Config - Toàn bộ settings ở 1 nơi
"""

import streamlit as st
from typing import Any, Dict
import toml

class ConfigBlock:
    """
    Quản lý configuration TOÀN HỆ THỐNG
    
    Sources:
    1. secrets.toml (priority)
    2. Environment variables
    3. Default values
    
    Lợi ích:
    - Dễ migrate (thay đổi env chỉ sửa 1 file)
    - Type-safe access
    - Cache configs
    """
    
    def __init__(self, config_file: str = "secrets.toml"):
        self.config = self._load_config(config_file)
    
    def _load_config(self, file_path: str) -> Dict[str, Any]:
        """Load config from TOML"""
        try:
            with open(file_path, "r") as f:
                return toml.load(f)
        except FileNotFoundError:
            st.warning(f"⚠️ Config file {file_path} not found. Using defaults.")
            return {}
        except Exception as e:
            st.error(f"❌ Error loading config: {e}")
            return {}
    
    def get(self, key: str, default: Any = None, section: Optional[str] = None) -> Any:
        """Get config value"""
        if section:
            return self.config.get(section, {}).get(key, default)
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, section: Optional[str] = None):
        """Set config value (runtime only)"""
        if section:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
        else:
            self.config[key] = value
    
    def render_config_ui(self):
        """Render admin config UI (if needed)"""
        with st.expander("⚙️ Cấu hình hệ thống"):
            for section, values in self.config.items():
                st.subheader(section)
                for key, val in values.items():
                    st.text(f"{key}: {val}")
