"""
META-BLOCK: Translation Feature
Nguyên tắc: Single Responsibility - Chỉ lo dịch thuật
"""

import streamlit as st
from typing import Optional

from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock


class TranslationFeature:
    """
    Translation feature block

    Dependencies:
    - AIEngine: Để gọi AI dịch
    - I18nBlock: Để hiển thị UI đa ngôn ngữ (optional)
    """

    def __init__(self, ai_engine: AIEngine, i18n: Optional[I18nBlock] = None):
        self.ai = ai_engine
        self.i18n = i18n

    def t(self, key: str, default: Optional[str] = None) -> str:
        """Helper để translate UI"""
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key

    def _get_style_instruction(self, style: str) -> str:
        style_map = {
            "Văn học": "Write in a literary style with rich imagery and elegant phrasing.",
            "Khoa học": "Write in a scientific/technical style, precise and formal.",
            "Đời thường": "Write in a casual, conversational everyday style.",
            "Hàn lâm": "Write in an academic style with formal tone and sophisticated vocabulary.",
            "Thương mại": "Write in a business style, concise, professional and persuasive.",
        }
        return style_map.get(style, "")

    def render(self):
        """Render translation UI"""
        st.subheader(self.t("weaver_translator", "🌐 Dịch Thuật"))

        # ── Configuration ───────────────────────────────────────
        col1, col2, col3 = st.columns([2, 2, 1.6])

        with col1:
            source_lang = st.selectbox(
                self.t("source_language", "Ngôn ngữ nguồn"),
                ["Chinese", "English", "Vietnamese", "Japanese", "Korean", "French"],
                index=0,
                key="trans_source_lang"
            )

        with col2:
            target_lang_options = ["Vietnamese", "English", "Chinese", "Japanese", "Korean", "French"]
            if source_lang in target_lang_options:
                target_lang_options.remove(source_lang)

            target_lang = st.selectbox(
                self.t("target_language", "Ngôn ngữ đích"),
                target_lang_options,
                index=0,
                key="trans_target_lang"
            )

        with col3:
            style = st.selectbox(
                self.t("translation_style", "Phong cách"),
                ["Đời thường", "Văn học", "Khoa học", "Hàn lâm", "Thương mại"],
                index=0,
                key="trans_style"
            )

        # ── Mode (chỉ hiện khi dịch từ tiếng Trung) ─────────────
        mode = "Standard (Dịch câu)"
        if source_lang == "Chinese":
            mode = st.radio(
                self.t("translation_mode", "Chế độ dịch"),
                ["Standard (Dịch câu)", "Interactive (Học từ)"],
                horizontal=True,
                key="trans_mode"
            )

        include_english = st.checkbox(
            self.t("include_english", "📖 Kèm giải thích Tiếng Anh"),
            value=True,
            key="trans_include_en"
        )

        st.divider()

        # ── Input Area ──────────────────────────────────────────
        text_input = st.text_area(
            self.t("input_text_placeholder", "Nhập hoặc dán văn bản cần dịch..."),
            height=240,
            placeholder=self.t("input_text_placeholder", "Nhập hoặc dán văn bản cần dịch..."),
            key="trans_input_text"
        )

        # ── Action Button ───────────────────────────────────────
        if st.button(
            self.t("translate_now", "🚀 Dịch Ngay"),
            type="primary",
            use_container_width=True,
            key="trans_button"
        ):
            if not text_input.strip():
                st.error(self.t("error_empty_input", "❌ Chưa nhập văn bản!"))
                st.stop()

            with st.spinner(self.t("translating", "Đang dịch...")):
                try:
                    style_instruction = self._get_style_instruction(style)

                    additional = ""
                    if include_english and target_lang != "English":
                        additional = "\nProvide an English explanation/translation of difficult terms right after each segment if necessary."

                    prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Style instructions: {style_instruction}
{additional.strip()}

Text to translate:
{text_input.strip()}
"""

                    response = self.ai.generate(
                        prompt=prompt,
                        model_type="pro",
                        # progress_callback=...  (nếu engine hỗ trợ thì thêm lại)
                    )

                    if response.success:
                        st.success(
                            f"✅ Hoàn thành! ({response.provider} • {response.latency:.1f}s)"
                        )
                        st.balloons()

                        st.divider()
                        st.subheader(self.t("translation_result", "📄 Kết quả dịch"))

                        st.markdown(response.content)

                        # Lưu lịch sử (không bắt buộc, nên try-except)
                        try:
                            from services.blocks.rag_orchestrator import store_history
                            store_history(
                                action="Dịch Thuật",
                                metadata=f"{source_lang} → {target_lang} ({style})",
                                content=text_input[:600]
                            )
                        except (ImportError, Exception):
                            pass

                    else:
                        st.error(f"❌ {response.error or 'Lỗi từ AI engine'}")

                except Exception as e:
                    st.error(f"❌ Lỗi dịch thuật: {str(e)}")
                    # st.exception(e)   # chỉ nên dùng khi debug, production nên comment
                    # Có thể log error ở đây nếu có logging system
