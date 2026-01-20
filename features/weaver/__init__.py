"""
META-BLOCK: Weaver Feature Aggregator
Nguyên tắc: Composition - Ghép các sub-features
"""

import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock

from .rag_feature import RagFeature
from .translation_feature import TranslationFeature
from .debate_feature import DebateFeature
from .voice_feature import VoiceFeature
from .history_feature import HistoryFeature

class WeaverFeature:
    """
    Aggregator cho tất cả sub-features của Weaver
    
    Dependencies:
    - AIEngine
    - I18nBlock (optional)
    """
    
    def __init__(self, ai_engine: AIEngine, i18n: Optional[I18nBlock] = None):
        self.ai = ai_engine
        self.i18n = i18n
        self.features = self._init_features()
    
    def _init_features(self):
        return {
            "rag": RagFeature(self.ai, self.i18n),
            "translation": TranslationFeature(self.ai, self.i18n),
            "debate": DebateFeature(self.ai, self.i18n),
            "voice": VoiceFeature(self.ai, self.i18n),
            "history": HistoryFeature(self.ai, self.i18n)
        }
    
    def render(self):
        """Render Weaver UI với tabs"""
        st.title(self.i18n.t("weaver_title", "🧠 Cognitive Weaver") if self.i18n else "🧠 Cognitive Weaver")
        
        tabs = st.tabs([
            self.i18n.t("weaver_rag", "📚 RAG") if self.i18n else "📚 RAG",
            self.i18n.t("weaver_translator", "✍️ Translator") if self.i18n else "✍️ Translator",
            self.i18n.t("weaver_debate", "🗣️ Debate") if self.i18n else "🗣️ Debate",
            self.i18n.t("weaver_voice", "🎙️ Voice") if self.i18n else "🎙️ Voice",
            self.i18n.t("weaver_history", "⏳ History") if self.i18n else "⏳ History"
        ])
        
        with tabs[0]:
            self.features["rag"].render()
        
        with tabs[1]:
            self.features["translation"].render()
        
        with tabs[2]:
            self.features["debate"].render()
        
        with tabs[3]:
            self.features["voice"].render()
        
        with tabs[4]:
            self.features["history"].render()
