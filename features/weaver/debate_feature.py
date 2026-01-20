"""
META-BLOCK: Debate Feature
Nguyên tắc: Single Responsibility - Chỉ lo chức năng Tranh Biện / Debate Arena
"""

import streamlit as st
from typing import Optional, Dict
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from prompts import DEBATE_PERSONAS  # migrate từ prompts.py cũ

class DebateFeature:
    """
    Debate / Tranh Biện feature block
    
    Dependencies:
    - AIEngine: để generate phản biện
    - I18nBlock: đa ngôn ngữ UI
    """
    
    def __init__(self, ai_engine: AIEngine, i18n: Optional[I18nBlock] = None):
        self.ai = ai_engine
        self.i18n = i18n
        
        # Migrate DEBATE_PERSONAS từ prompts.py cũ
        self.personas = DEBATE_PERSONAS
        
        # Session state cho chat history
        if "debate_messages" not in st.session_state:
            st.session_state.debate_messages = []
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def render(self):
        """Render Debate UI"""
        st.subheader(self.t("weaver_debate", "🗣️ Đấu Trường Tư Duy"))
        
        # Chọn đối thủ (persona)
        persona_options = list(self.personas.keys())
        selected_persona = st.selectbox(
            self.t("t3_persona_label", "Chọn Đối Thủ:"),
            persona_options,
            index=0
        )
        
        # Hiển thị mô tả persona (tooltip hoặc expander)
        with st.expander("ℹ️ Mô tả phong cách của đối thủ", expanded=False):
            st.markdown(self.personas[selected_persona])
        
        # Input chủ đề tranh luận
        user_input = st.text_area(
            self.t("t3_input", "Nhập chủ đề tranh luận hoặc câu hỏi..."),
            height=120,
            placeholder="Ví dụ: 'AI có thể thay thế hoàn toàn trí tuệ con người không?'"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🗣️ Bắt đầu Tranh Luận", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning(self.t("error_empty_input", "Vui lòng nhập chủ đề tranh luận!"))
                else:
                    # Thêm message user
                    st.session_state.debate_messages.append({"role": "user", "content": user_input})
                    
                    # Tạo system prompt từ persona
                    system_prompt = self.personas[selected_persona]
                    
                    # Gọi AI với lịch sử chat
                    with st.spinner("Đối thủ đang suy nghĩ..."):
                        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.debate_messages])
                        response = self.ai.generate(
                            prompt=full_prompt,
                            system_instruction=system_prompt,
                            model_type="pro",
                            temperature=0.8  # hơi sáng tạo để tranh biện thú vị hơn
                        )
                        
                        if response.success:
                            st.session_state.debate_messages.append({"role": "assistant", "content": response.content})
                        else:
                            st.error(f"❌ Lỗi: {response.error}")
        
        with col2:
            if st.button(self.t("t3_clear", "🗑️ Xóa Chat"), use_container_width=True):
                st.session_state.debate_messages = []
                st.rerun()
        
        # Hiển thị lịch sử chat
        st.divider()
        for message in st.session_state.debate_messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🗣️"):
                    st.markdown(message["content"])
