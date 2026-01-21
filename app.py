import streamlit as st
from core.app_builder import AppBuilder


def main():
    """
    Khởi động ứng dụng với giao diện cải tiến
    
    Thay đổi:
    1. Page config với layout wide + dark theme support
    2. Custom CSS hiện đại, tối giản
    3. Sidebar thu gọn, chỉ hiện menu cần thiết
    """
    
    # Page config
    st.set_page_config(
        page_title="Cognitive Weaver",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "# Cognitive Weaver\n*Powered by Meta-Blocks Architecture*"
        }
    )
    
    # Custom CSS - Modern & Minimal
    st.markdown("""
        <style>
            /* ===== GLOBAL STYLES ===== */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .stApp {
                    background: linear-gradient(135deg, #1e1e1e 0%, #2d3748 100%);
                }
            }
            
            /* ===== SIDEBAR ===== */
            section[data-testid="stSidebar"] > div:first-child {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-right: 2px solid #e2e8f0;
                box-shadow: 4px 0 12px rgba(0,0,0,0.05);
            }
            
            @media (prefers-color-scheme: dark) {
                section[data-testid="stSidebar"] > div:first-child {
                    background: rgba(30, 30, 30, 0.95);
                    border-right: 2px solid #4a5568;
                }
            }
            
            /* ===== MAIN CONTENT ===== */
            .block-container {
                padding: 2rem 3rem !important;
                max-width: 1200px !important;
            }
            
            /* ===== BUTTONS ===== */
            .stButton > button {
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                border: none;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }
            
            /* ===== TABS ===== */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background: transparent;
            }
            
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
                padding: 12px 24px;
                font-weight: 600;
            }
            
            /* ===== EXPANDERS ===== */
            .streamlit-expanderHeader {
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(5px);
                font-weight: 600;
            }
            
            @media (prefers-color-scheme: dark) {
                .streamlit-expanderHeader {
                    background: rgba(45, 55, 72, 0.7);
                }
            }
            
            /* ===== METRICS ===== */
            [data-testid="stMetricValue"] {
                font-size: 2rem;
                font-weight: 700;
            }
            
            /* ===== CHAT MESSAGES ===== */
            .stChatMessage {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 1rem;
                margin: 0.5rem 0;
                border: 1px solid rgba(0,0,0,0.05);
            }
            
            @media (prefers-color-scheme: dark) {
                .stChatMessage {
                    background: rgba(45, 55, 72, 0.8);
                    border: 1px solid rgba(255,255,255,0.1);
                }
            }
            
            /* ===== SCROLLBAR ===== */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(0,0,0,0.2);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0,0,0,0.3);
            }
            
            /* ===== ANIMATIONS ===== */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .element-container {
                animation: fadeIn 0.3s ease-out;
            }
            
            /* ===== HIDE STREAMLIT BRANDING ===== */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Build app với AppBuilder
    (
        AppBuilder()
        .with_config()
        .with_i18n(languages=["vi", "en", "zh"], default="vi")
        .with_auth(method="password")
        .with_ai_engine(default_model="gemini-pro")
        .with_feature("weaver")      # Cognitive Weaver (RAG + Debate only)
        .with_feature("history")     # History Logs
        .with_sidebar(enabled=True)
        .with_default_feature("weaver")
        .build()
    )


if __name__ == "__main__":
    main()
