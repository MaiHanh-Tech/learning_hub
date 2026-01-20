"""
META-BLOCK: Application Entry Point
Nguyên tắc: Single Entry - Toàn bộ app khởi động từ đây
"""

import streamlit as st
from core.app_builder import AppBuilder

def main():
    """
    Khởi động toàn bộ ứng dụng theo cấu trúc LEGO (Meta-Blocks)
    
    Thứ tự gọi .with_xxx() rất quan trọng:
    - config phải ở đầu tiên (nhiều block phụ thuộc)
    - i18n, auth, ai_engine tiếp theo
    - features cuối cùng
    """
    (
        AppBuilder()
        .with_config()                          # Centralized config - phải gọi đầu tiên
        .with_i18n(languages=["vi", "en", "zh"], default="vi")
        .with_auth(method="password")           # Supabase + hard admin fallback
        .with_ai_engine(default_model="gemini-pro")
        .with_feature("weaver")                 # Cognitive Weaver (RAG, Translation, Debate, Voice, History)
        .with_feature("cfo")                    # CFO Controller (Dashboard, Analysis, Risk)
        .with_sidebar(enabled=True)
        .with_default_feature("weaver")         # Mở mặc định Weaver khi login thành công
        .build()
    )

    # Custom CSS nhẹ (có thể mở rộng sau)
    st.markdown("""
        <style>
            /* Nền app nhẹ nhàng */
            .stApp {
                background-color: #f8f9fa;
            }
            /* Sidebar trắng sạch */
            section[data-testid="stSidebar"] > div:first-child {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
            /* Tăng khoảng cách cho đẹp */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
# Force rebuild 2026-01-20
