"""
META-BLOCK: Config Block
Nguyên tắc: Centralized Config - Toàn bộ settings ở 1 nơi
"""

import streamlit as st
from typing import Any, Dict, Optional
import toml
import os

class ConfigBlock:
    """
    Quản lý configuration TOÀN HỆ THỐNG
    
    Sources (ưu tiên giảm dần):
    1. secrets.toml
    2. .env (nếu có)
    3. Default values hard-code
    
    Usage:
        config = ConfigBlock()
        gemini_key = config.get("api_keys", "gemini_api_key")
        tts_voices = config.get("voice", "tts_voices")
    """
    
    def __init__(self):
        self.config: Dict[str, Any] = self._load_all_sources()
    
    def _load_all_sources(self) -> Dict:
        """Load config từ nhiều nguồn"""
        config = {}
        
        # 1. secrets.toml (ưu tiên cao nhất)
        try:
            secrets_path = "secrets.toml"
            if os.path.exists(secrets_path):
                with open(secrets_path, "r", encoding="utf-8") as f:
                    secrets = toml.load(f)
                    config.update(secrets)
        except Exception as e:
            st.warning(f"Không đọc được secrets.toml: {e}")
        
        # 2. Default values (nếu không có trong secrets)
        defaults = {
            "ai": {
                "default_model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            "voice": {
                "tts_voices": {
                    "vi": {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural"},
                    "en": {"female": "en-US-EmmaNeural", "male": "en-US-AndrewNeural"},
                    "zh": {"female": "zh-CN-XiaoyiNeural", "male": "zh-CN-YunjianNeural"}
                }
            },
            "translation": {
                "supported_languages": ["Chinese", "English", "Vietnamese", "French", "Japanese", "Korean"]
            },
            "cache": {
                "ttl_translation": 86400,      # 24h
                "ttl_book_analysis": 3600,     # 1h
                "ttl_embedding": 604800        # 7 ngày
            }
        }
        self._deep_merge(config, defaults)
        
        return config
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Merge source vào target (deep merge)"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                if key not in target:
                    target[key] = value
    
    def get(self, section: Optional[str] = None, key: Optional[str] = None, default: Any = None) -> Any:
        """Lấy giá trị config"""
        if section:
            sec = self.config.get(section, {})
            if key:
                return sec.get(key, default)
            return sec
        if key:
            return self.config.get(key, default)
        return self.config
    
    def render_debug_ui(self):
        """Hiển thị config (cho admin/debug)"""
        with st.expander("⚙️ System Configuration (Debug)", expanded=False):
            st.json(self.config)
