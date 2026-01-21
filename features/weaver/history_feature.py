"""
META-BLOCK: History Feature 
Nguyên tắc: Auto-sync với Supabase + Real-time refresh
"""

import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
from supabase import create_client, Client


class HistoryFeature:
    """
    Nhật ký Hoạt động - Đồng bộ với Supabase
    
    Features:
    - Tự động load logs mới nhất từ Supabase
    - Filter theo loại hoạt động (book_analysis, debate, translation...)
    - Export logs thành CSV
    """
    
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config
        
        # Kết nối Supabase
        self.db: Optional[Client] = None
        self.connected = False
        
        try:
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
            
            if url and key:
                self.db = create_client(url, key)
                self.connected = True
        
        except Exception as e:
            st.warning(f"⚠️ Không kết nối được Supabase: {str(e)}")
    
    def t(self, key: str, default: str = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def get_history(
        self,
        limit: int = 50,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Lấy lịch sử từ Supabase
        
        Args:
            limit: Số lượng log tối đa
            event_type: Filter theo loại (book_analysis, debate, etc.)
        
        Returns:
            List of log entries
        """
        if not self.connected:
            return []
        
        try:
            query = self.db.table("history_logs").select("*")
            
            # Filter nếu có
            if event_type and event_type != "all":
                query = query.eq("type", event_type)
            
            # Order by newest first
            response = query.order("created_at", desc=True).limit(limit).execute()
            
            return response.data or []
        
        except Exception as e:
            st.error(f"❌ Lỗi đọc Supabase: {str(e)}")
            return []
    
    def render(self):
        """Render History UI"""
        st.title("⏳ Nhật Ký Hoạt Động")
        st.caption("Theo dõi lịch sử phân tích & tranh biện")
        
        if not self.connected:
            st.error("❌ Không kết nối được Supabase. Kiểm tra secrets.toml")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            event_filter = st.selectbox(
                "🔍 Lọc theo loại:",
                ["all", "book_analysis", "debate", "translation", "voice"],
                format_func=lambda x: {
                    "all": "📋 Tất cả",
                    "book_analysis": "📚 Phân tích sách",
                    "debate": "🗣️ Tranh biện",
                    "translation": "✍️ Dịch thuật",
                    "voice": "🎙️ Voice"
                }.get(x, x)
            )
        
        with col2:
            limit = st.number_input(
                "📊 Số lượng:",
                min_value=10,
                max_value=200,
                value=50,
                step=10
            )
        
        with col3:
            if st.button("🔄 Tải lại", use_container_width=True):
                st.rerun()
        
        st.divider()
        
        # Load history
        with st.spinner("📡 Đang tải từ Supabase..."):
            history = self.get_history(
                limit=limit,
                event_type=event_filter if event_filter != "all" else None
            )
        
        # Display stats
        if history:
            col1, col2, col3 = st.columns(3)
            col1.metric("📝 Tổng log", len(history))
            
            # Count by type
            types = {}
            for log in history:
                t = log.get("type", "unknown")
                types[t] = types.get(t, 0) + 1
            
            col2.metric("📚 Phân tích sách", types.get("book_analysis", 0))
            col3.metric("🗣️ Tranh biện", types.get("debate", 0))
            
            st.divider()
            
            # Export button
            if st.button("💾 Export CSV", use_container_width=False):
                import pandas as pd
                
                df = pd.DataFrame(history)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Tải xuống",
                    data=csv,
                    file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            st.divider()
            
            # Display logs
            st.markdown("### 📜 Danh sách Log")
            
            for entry in history:
                event_type = entry.get("type", "unknown")
                created_at = entry.get("created_at", "N/A")
                title = entry.get("title", "Untitled")
                user = entry.get("user_name", "Guest")
                content = entry.get("content", "")
                
                # Icon theo loại
                icon = {
                    "book_analysis": "📚",
                    "debate": "🗣️",
                    "translation": "✍️",
                    "voice": "🎙️"
                }.get(event_type, "📄")
                
                # Expander cho mỗi log
                with st.expander(
                    f"{icon} **{title}** • {created_at[:19]} • {user}",
                    expanded=False
                ):
                    st.markdown(f"**Loại:** {event_type}")
                    st.markdown(f"**Người dùng:** {user}")
                    st.markdown(f"**Thời gian:** {created_at}")
                    st.divider()
                    st.markdown("**Nội dung:**")
                    st.markdown(content[:1000] + ("..." if len(content) > 1000 else ""))
        
        else:
            st.info("📭 Chưa có log nào. Hãy bắt đầu phân tích hoặc tranh biện!")
    
    @staticmethod
    def log_event(event_type: str, title: str, content: str):
        """
        Static method để log từ bất kỳ module nào
        
        [Unverified] Method này có thể được gọi từ bất kỳ đâu trong app
        để ghi log vào Supabase mà không cần khởi tạo HistoryFeature
        
        Args:
            event_type: Loại event (book_analysis, debate, etc.)
            title: Tiêu đề log
            content: Nội dung chi tiết
        """
        try:
            from supabase import create_client
            
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
            
            if url and key:
                db = create_client(url, key)
                
                db.table("history_logs").insert({
                    "type": event_type,
                    "title": title,
                    "content": content,
                    "user_name": st.session_state.get("current_user", "Guest")
                }).execute()
        
        except Exception:
            # [Unverified] Không làm gián đoạn flow chính nếu log fail
            pass
