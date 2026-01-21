"""
META-BLOCK: Application Entry Point 
No debug messages, proper i18n, CFO enabled
"""

import streamlit as st
from core.app_builder import AppBuilder

# DEBUG: Test Gemini

try:
    import google.generativeai as genai
    
    # Lấy key
    key = st.secrets.get("api_keys", {}).get("gemini_api_key")
    if not key:
        key = st.secrets.get("gemini_api_key")
    
    if key:
        genai.configure(api_key=key)
        
        # Test call
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Say hello in Vietnamese")
        
        st.sidebar.success(f"✅ Gemini OK: {response.text[:50]}")
    else:
        st.sidebar.error("❌ Gemini key not found in secrets")

except Exception as e:
    st.sidebar.error(f"❌ Gemini error: {str(e)}")


def main():
    """
    Khởi động ứng dụng
    
    Features:
    - Weaver: RAG + Debate (Solo + Multi) + History with Bayes
    - CFO: Dashboard + Cost Analysis + Risk + What-If
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
            /* Global Styles */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            
            @media (prefers-color-scheme: dark) {
                .stApp {
                    background: linear-gradient(135deg, #1e1e1e 0%, #2d3748 100%);
                }
            }
            
            /* Sidebar */
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
            
            /* Main Content */
            .block-container {
                padding: 2rem 3rem !important;
                max-width: 1200px !important;
            }
            
            /* Buttons */
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
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background: transparent;
            }
            
            .stTabs [data-baseweb="tab"] {
                border-radius: 8px 8px 0 0;
                padding: 12px 24px;
                font-weight: 600;
            }
            
            /* Expanders */
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
            
            /* Metrics */
            [data-testid="stMetricValue"] {
                font-size: 2rem;
                font-weight: 700;
            }
            
            /* Chat Messages */
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
            
            /* Scrollbar */
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
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .element-container {
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Build app
    (
        AppBuilder()
        .with_config()
        .with_i18n(languages=["vi", "en", "zh"], default="vi")
        .with_auth(method="password")
        .with_ai_engine(default_model="gemini-pro")
        .with_feature("weaver")      # Cognitive Weaver (RAG + Debate + History)
        .with_feature("cfo")          # CFO Controller (Dashboard + Analysis + Risk + What-If)
        .with_sidebar(enabled=True)
        .with_default_feature("weaver")
        .build()
    )


if __name__ == "__main__":
    main()
