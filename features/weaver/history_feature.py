"""
META-BLOCK: History Feature
Nguyên tắc: Single Responsibility - Chỉ lo Nhật ký hoạt động
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
from supabase import create_client, Client

class HistoryFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config or {}
        
        # Supabase connection (từ secrets.toml)
        self.db = None
        self.connected = False
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.db: Client = create_client(url, key)
            self.connected = True
        except Exception as e:
            st.warning(f"Lỗi kết nối Supabase: {e}")
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def get_history(self, limit=20):
        if not self.connected:
            return []
        try:
            resp = self.db.table("history_logs").select("*").order("created_at", desc=True).limit(limit).execute()
            return resp.data or []
        except Exception:
            return []
    
    def render(self):
        st.subheader(self.t("weaver_history", "⏳ Nhật Ký Hoạt Động"))
        
        if not self.connected:
            st.error("Không kết nối được Supabase để lấy lịch sử.")
            return
        
        history = self.get_history(limit=50)
        
        if not history:
            st.info(self.t("history_empty", "Chưa có lịch sử hoạt động nào."))
            return
        
        for entry in history:
            with st.expander(f"{entry.get('created_at', 'N/A')} | {entry.get('type', 'Unknown')}"):
                st.write(f"**Tiêu đề**: {entry.get('title', 'N/A')}")
                st.write(f"**Người dùng**: {entry.get('user_name', 'Guest')}")
                st.markdown(entry.get('content', 'N/A'))
