"""
META-BLOCK: History Feature
Nguyên tắc: Single Responsibility - Chỉ lo Nhật ký hoạt động
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
# from core.db_block import DBBlock  # Uncomment khi có

class HistoryFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[dict] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config or {}
        # self.db = DBBlock()  # Uncomment sau

    def t(self, key: str, default: Optional[str] = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key

    def render(self):
        st.subheader(self.t("weaver_history", "⏳ Nhật Ký Hoạt Động"))
        st.info("Lịch sử các tương tác (RAG, Dịch, Tranh biện, Voice) sẽ hiển thị ở đây.")
        
        # Placeholder
        st.write("Chưa có lịch sử. Sẽ migrate từ db_block.py và store_history sau.")
        
        if st.button("Tải lịch sử mới nhất"):
            st.info("Đang tải... (sẽ dùng Supabase sau)")
