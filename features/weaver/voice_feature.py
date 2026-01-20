"""
META-BLOCK: Voice Feature
Nguyên tắc: Single Responsibility - Chỉ lo TTS/STT và Phòng Thu AI
"""

import streamlit as st
from typing import Any, Dict, Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
import edge_tts
import asyncio
import tempfile

class VoiceFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config or {}
        
        # TTS voices từ config (hoặc default nếu chưa có)
        self.voices = self.config.get("voice", "tts_voices") or {
            "vi": {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural"},
            "en": {"female": "en-US-EmmaNeural", "male": "en-US-AndrewNeural"},
            "zh": {"female": "zh-CN-XiaoyiNeural", "male": "zh-CN-YunjianNeural"}
        }
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    async def _generate_tts(self, text: str, voice: str, rate: str = "+0%") -> Optional[str]:
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                await communicate.save(fp.name)
                return fp.name
        except Exception as e:
            st.error(f"❌ Lỗi TTS: {str(e)}")
            return None
    
    def render(self):
        st.subheader(self.t("weaver_voice", "🎙️ Phòng Thu AI"))
        
        text = st.text_area(self.t("voice_input", "Nhập văn bản để chuyển thành giọng nói"), height=150)
        voice_key = st.selectbox(
            self.t("voice_select", "Chọn giọng nói"),
            list(self.voices.keys()),
            format_func=lambda k: f"{k.upper()} - {self.voices[k]['female']}"
        )
        speed = st.slider(self.t("voice_speed", "Tốc độ"), -50, 50, 0, step=5, format="%d%%")
        rate_str = f"{'+' if speed >= 0 else ''}{speed}%"
        
        if st.button(self.t("voice_play", "🔊 Phát")):
            if not text.strip():
                st.warning(self.t("voice_empty", "Vui lòng nhập văn bản"))
            else:
                with st.spinner(self.t("voice_generating", "Đang tạo giọng nói...")):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    path = loop.run_until_complete(self._generate_tts(text, self.voices[voice_key]["female"], rate_str))
                    loop.close()
                    
                    if path:
                        st.audio(path, format="audio/mp3")
                        st.success("Phát thành công!")
                    else:
                        st.error("Không tạo được file âm thanh.")
