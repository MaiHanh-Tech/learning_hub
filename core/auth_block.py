"""
META-BLOCK: Authentication Block
Phiên bản đơn giản: Chỉ dùng mật khẩu cứng từ secrets.toml, không cần Supabase
"""

import streamlit as st
import hashlib

class AuthBlock:
    def __init__(self, method: str = "password"):
        # Lấy hash mật khẩu admin từ secrets.toml
        self.admin_password_hash = st.secrets.get("admin_password_hash", "")
        if not self.admin_password_hash:
            st.error("❌ Chưa cấu hình admin_password_hash trong secrets.toml")
    
    def check_login(self) -> bool:
        """Kiểm tra đã login chưa qua session"""
        return st.session_state.get("authenticated", False)
    
    def render_login_ui(self):
        """Hiển thị form login chỉ cần mật khẩu"""
        st.title("🔒 Đăng Nhập Admin")
        
        with st.form(key="login_form"):
            password = st.text_input("Mật khẩu Admin", type="password")
            submit = st.form_submit_button("Đăng nhập")
            
            if submit:
                if not password:
                    st.error("Vui lòng nhập mật khẩu")
                    return
                
                input_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if input_hash == self.admin_password_hash:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = "Admin"
                    st.session_state["is_admin"] = True
                    st.success("✅ Đăng nhập thành công! Đang chuyển hướng...")
                    st.rerun()  # Quan trọng: rerurn để load lại app
                else:
                    st.error("❌ Mật khẩu sai")
    
    def logout(self):
        """Đăng xuất"""
        st.session_state.clear()
        st.rerun()
