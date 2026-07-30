import streamlit as st
import hashlib
import time
from datetime import datetime
try:
    from supabase import create_client, Client
except ImportError:
    st.error("⚠️ Thiếu thư viện supabase. Hãy thêm 'supabase' vào requirements.txt")

# Cấu hình khoá đăng nhập
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 5 * 60  # 5 phút


class AuthBlock:
    def __init__(self):
        # 1. Kết nối Supabase
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.supabase: Client = create_client(url, key)
            self.db_connected = True
        except Exception as e:
            self.db_connected = False
            # st.error(f"Lỗi kết nối DB: {e}")

        # 2. Backdoor (Admin cứng trong secrets để phòng hộ)
        self.hard_admin_hash = st.secrets.get("admin_password_hash", "")

        # Init Session
        if 'user_logged_in' not in st.session_state: 
            st.session_state.user_logged_in = False
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}

    def _hash_password(self, password):
        return hashlib.sha256(str(password).encode()).hexdigest()

    def _get_recent_attempts(self):
        """Lọc bỏ các lần thử đã quá cũ (ngoài cửa sổ khoá), trả về list còn hiệu lực."""
        now = time.time()
        attempts = st.session_state.login_attempts.get('global', [])
        recent = [t for t in attempts if now - t < LOCKOUT_WINDOW_SECONDS]
        st.session_state.login_attempts['global'] = recent
        return recent

    def is_locked_out(self):
        """True nếu đã sai đủ MAX_LOGIN_ATTEMPTS lần trong cửa sổ hiện tại."""
        return len(self._get_recent_attempts()) >= MAX_LOGIN_ATTEMPTS

    def seconds_until_unlock(self):
        attempts = self._get_recent_attempts()
        if len(attempts) < MAX_LOGIN_ATTEMPTS:
            return 0
        oldest = min(attempts)
        remaining = LOCKOUT_WINDOW_SECONDS - (time.time() - oldest)
        return max(0, int(remaining))

    def login(self, password):
        """Logic đăng nhập: Ưu tiên DB, nếu DB sập thì dùng Hard Admin.
        ✅ FIX: chặn brute-force thật sự — trước đây UI hiển thị "còn X lần thử"
        nhưng không hề có logic nào khoá đăng nhập, ai cũng thử được không giới hạn.
        """
        if self.is_locked_out():
            return False

        if not password:
            return False
        input_hash = self._hash_password(password)

        # CÁCH 1: Check Admin cứng (Phòng khi DB lỗi hoặc quên pass DB)
        if input_hash == self.hard_admin_hash:
            self._set_session("SuperAdmin", True, True)
            self._reset_attempts()
            return True

        # CÁCH 2: Check Database Supabase (Chỉ check user = admin vì đây là form login tổng)
        if self.db_connected:
            try:
                # Lấy tất cả user đang active
                response = self.supabase.table("users").select("*").eq("is_active", True).execute()
                users = response.data
                
                for user in users:
                    if user['password_hash'] == input_hash:
                        is_admin = (user['role'] == 'admin')
                        self._set_session(user['username'], is_admin, True)
                        self._reset_attempts()
                        return True
            except Exception:
                pass # Lỗi DB thì thôi, trả về False

        # Đăng nhập thất bại — ghi nhận lần thử
        st.session_state.login_attempts.setdefault('global', []).append(time.time())
        return False

    def _reset_attempts(self):
        st.session_state.login_attempts['global'] = []

    def _set_session(self, u, admin, vip):
        st.session_state.user_logged_in = True
        st.session_state.current_user = u
        st.session_state.is_admin = admin
        st.session_state.is_vip = vip

    # --- CÁC HÀM QUẢN LÝ USER (CHO ADMIN) ---
    def create_user(self, username, password, role="user"):
        if not self.db_connected: return False, "Mất kết nối DB"
        try:
            p_hash = self._hash_password(password)
            data = {"username": username, "password_hash": p_hash, "role": role, "is_active": True}
            self.supabase.table("users").insert(data).execute()
            return True, "Tạo thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_user(self, username):
        if not self.db_connected: return False, "Mất kết nối DB"
        try:
            self.supabase.table("users").delete().eq("username", username).execute()
            return True, "Đã xóa!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
    
    def get_all_users(self):
        if not self.db_connected: return []
        try:
            res = self.supabase.table("users").select("*").execute()
            return res.data
        except: return []
