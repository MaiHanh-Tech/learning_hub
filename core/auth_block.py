"""
META-BLOCK: Authentication Block
Nguyên tắc: Single Responsibility - Chỉ lo xác thực người dùng
"""

import streamlit as st
from typing import Optional
import hashlib

class AuthBlock:
    """
    Authentication block
    
    Methods:
    - Password (default)
    - Future: OAuth, JWT, etc.
    
    Lợi ích:
    - Tập trung hóa auth logic
    - Dễ mở rộng (thêm SSO sau này chỉ sửa 1 file)
    - Bảo mật: Hash passwords, session-based
    """
    
    def __init__(self, method: str = "password"):
        self.method = method
        self.users = self._load_users()  # Load from secrets.toml or db
    
    def _load_users(self) -> dict:
        """Load user credentials (from st.secrets or external db)"""
        try:
            return st.secrets["auth"]["users"]  # Expect: {"username": "hashed_password"}
        except KeyError:
            st.warning("⚠️ No users configured in secrets.toml")
            return {}
    
    def check_login(self) -> bool:
        """Check if user is logged in"""
        return st.session_state.get("authenticated", False)
    
    def render_login_ui(self):
        """Render login form"""
        st.title("🔒 Đăng Nhập")
        
        with st.form(key="login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit = st.form_submit_button("Đăng nhập")
            
            if submit:
                if self._verify_credentials(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = username
                    st.success("✅ Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    
    def _verify_credentials(self, username: str, password: str) -> bool:
        """Verify password (hashed)"""
        if username in self.users:
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            return hashed_pw == self.users[username]
        return False
    
    def require_auth(self, func):
        """Decorator to require authentication"""
        def wrapper(*args, **kwargs):
            if not self.check_login():
                self.render_login_ui()
                st.stop()
            return func(*args, **kwargs)
        return wrapper
