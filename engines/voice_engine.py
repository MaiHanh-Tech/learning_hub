"""
META-BLOCK: Voice Engine
Nguyên tắc: Single Responsibility - Chỉ lo TTS/STT
"""

import streamlit as st
import edge_tts
import asyncio
import tempfile
import unicodedata
import re
from typing import Optional
from core.config_block import ConfigBlock

class VoiceEngine:
    """
    TTS Engine với multi-language support
    
    Dependencies:
    - ConfigBlock (cho voices config)
    """
    
    def __init__(self, config: ConfigBlock):
        self.voices = config.get("tts_voices", section="voice") or {
            "vi": {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural"},
            "en": {"female": "en-US-EmmaNeural", "male": "en-US-AndrewNeural"},
            "zh": {"female": "zh-CN-XiaoyiNeural", "male": "zh-CN-YunjianNeural"}
        }
        self.voice_options = {
            "🇻🇳 VN - Nữ (Hoài My)": self.voices["vi"]["female"],
            "🇻🇳 VN - Nam (Nam Minh)": self.voices["vi"]["male"],
            "🇺🇸 US - Nữ (Emma)": self.voices["en"]["female"],
            "🇺🇸 US - Nam (Andrew)": self.voices["en"]["male"],
            "🇨🇳 CN - Nữ (Xiaoyi)": self.voices["zh"]["female"],
            "🇨🇳 CN - Nam (Yunjian)": self.voices["zh"]["male"]
        }
    
    async def _generate_audio(self, text: str, voice: str, rate: str) -> Optional[str]:
        """Async TTS generation"""
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                await communicate.save(fp.name)
                return fp.name
        except Exception as e:
            st.error(f"❌ TTS error: {e}")
            return None
    
    def _clean_text(self, text: str, voice_code: str) -> Optional[str]:
        """Clean text for TTS"""
        if not text.strip():
            return None
        # Remove emojis and special chars
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  
            "\U0001F300-\U0001F5FF"  
            "\U0001F680-\U0001F6FF"  
            "\U0001F1E0-\U0001F1FF"  
            "\U0001F900-\U0001F9FF"  
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)
        
        if "zh-CN" in voice_code:
            text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        elif "en-US" in voice_code:
            text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        
        text = re.sub(r'\s+', ' ', text).strip()
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        MAX_LENGTH = 4500
        if len(text) > MAX_LENGTH:
            text = text[:MAX_LENGTH]
            st.warning(f"⚠️ Text too long. Truncating to {MAX_LENGTH} chars.")
        
        return text if text.strip() else None
    
    def generate_tts(self, text: str, voice_key: str, speed: int = 0) -> Optional[str]:
        """Generate TTS file path"""
        if not text:
            return None
        voice_code = self.voice_options.get(voice_key, self.voices["vi"]["female"])
        cleaned_text = self._clean_text(text, voice_code)
        if not cleaned_text:
            return None
        rate_str = f"{'+' if speed >= 0 else ''}{speed}%"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        path = loop.run_until_complete(self._generate_audio(cleaned_text, voice_code, rate_str))
        loop.close()
        return path
