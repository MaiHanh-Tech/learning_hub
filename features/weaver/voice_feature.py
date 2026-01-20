"""
META-BLOCK: Voice Feature
Nguyên tắc: Single Responsibility - Chỉ lo TTS/STT và Phòng Thu AI
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
# from engines.voice_engine import VoiceEngine  # Uncomment khi migrate xong

class VoiceFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[dict] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config or {}
        # self.voice_engine = VoiceEngine(config)  # Uncomment sau

    def t(self, key: str, default: Optional[str] = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key

    def render(self):
        st.subheader(self.t("weaver_voice", "🎙️ Phòng Thu AI"))
        st.info("Module Voice (TTS/STT) đang trong quá trình hoàn thiện.")
        
        # Placeholder UI
        text = st.text_area("Nhập văn bản để chuyển thành giọng nói", height=150)
        if st.button("🔊 Phát"):
            st.info("TTS sẽ phát âm thanh ở đây (sẽ migrate từ edge-tts sau).")
