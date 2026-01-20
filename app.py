"""
META-BLOCK: Application Entry Point
Nguyên tắc: Single Entry - Toàn bộ app khởi động từ đây
"""

import streamlit as st
from core.app_builder import AppBuilder

def main():
    """
    Khởi động app theo cấu trúc LEGO
    """
    app = (
        AppBuilder()
        .with_i18n(languages=["vi", "en", "zh"], default="vi")
        .with_auth(method="password")
        .with_ai_engine(default_model="gemini-pro")
        .with_feature("weaver")
        .with_feature("cfo")
        .with_sidebar(enabled=True)
        .build()
    )

    # Custom CSS (optional)
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; }
        .sidebar .sidebar-content { background-color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
