import streamlit as st
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
from supabase import create_client, Client


class HistoryFeature:
    """
    Nhật ký Hoạt động - Đồng bộ với Supabase + Upload CSV
    
    Features:
    - Upload CSV/Excel history cũ từ Supabase export
    - Auto-sync với logs mới
    - Filter + Search + Export
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
        event_type: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> List[Dict]:
        """Lấy lịch sử từ Supabase"""
        if not self.connected:
            return []
        
        try:
            query = self.db.table("history_logs").select("*")
            
            # Filter by type
            if event_type and event_type != "all":
                query = query.eq("type", event_type)
            
            # Search in title/content
            if search_term:
                query = query.or_(
                    f"title.ilike.%{search_term}%,"
                    f"content.ilike.%{search_term}%"
                )
            
            # Order by newest first
            response = query.order("created_at", desc=True).limit(limit).execute()
            
            return response.data or []
        
        except Exception as e:
            st.error(f"❌ Lỗi đọc Supabase: {str(e)}")
            return []
    
    def upload_csv_to_supabase(self, uploaded_file) -> int:
        """
        Upload CSV/Excel history cũ vào Supabase
        
        Returns:
            Số lượng records đã import thành công
        """
        if not self.connected:
            st.error("❌ Không kết nối Supabase")
            return 0
        
        try:
            # Đọc file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.info(f"📊 Phát hiện {len(df)} dòng trong file")
            
            # Mapping columns (adjust theo export Supabase của chị)
            column_mapping = {
                'id': 'original_id',
                'created_at': 'created_at',
                'type': 'type',
                'title': 'title',
                'content': 'content',
                'user_name': 'user_name',
                'sentiment_score': 'sentiment_score',
                'sentiment_label': 'sentiment_label'
            }
            
            # Rename columns
            df_renamed = df.rename(columns=column_mapping)
            
            # Required columns
            required = ['created_at', 'type', 'title', 'content']
            missing = [col for col in required if col not in df_renamed.columns]
            
            if missing:
                st.error(f"❌ File thiếu cột: {', '.join(missing)}")
                return 0
            
            # Convert to list of dicts
            records = df_renamed[required + ['user_name', 'sentiment_score', 'sentiment_label']].fillna('').to_dict('records')
            
            # Batch insert (Supabase giới hạn ~1000 rows/request)
            batch_size = 500
            success_count = 0
            
            progress_bar = st.progress(0)
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                
                try:
                    # Insert batch
                    response = self.db.table("history_logs").insert(batch).execute()
                    success_count += len(batch)
                    
                    # Update progress
                    progress = min(1.0, (i + batch_size) / len(records))
                    progress_bar.progress(progress)
                
                except Exception as e:
                    st.warning(f"⚠️ Lỗi batch {i//batch_size + 1}: {str(e)}")
                    continue
            
            progress_bar.empty()
            return success_count
        
        except Exception as e:
            st.error(f"❌ Lỗi xử lý file: {str(e)}")
            return 0
    
    def render(self):
        """Render History UI"""
        st.title("⏳ Nhật Ký Hoạt Động")
        st.caption("Quản lý lịch sử phân tích & tranh biện")
        
        if not self.connected:
            st.error("❌ Không kết nối được Supabase. Kiểm tra secrets.toml")
            return
        
        # ===== SECTION 1: UPLOAD CSV =====
        with st.expander("📤 Import Lịch Sử Cũ (CSV/Excel)", expanded=False):
            st.markdown("""
            **Hướng dẫn:**
            1. Export dữ liệu từ Supabase (Table Editor → Export CSV)
            2. Upload file vào đây
            3. Hệ thống sẽ tự động merge với logs mới
            
            **Lưu ý:** File cần có các cột: `created_at`, `type`, `title`, `content`
            """)
            
            uploaded = st.file_uploader(
                "Chọn file CSV hoặc Excel",
                type=["csv", "xlsx"],
                help="File export từ Supabase"
            )
            
            if uploaded:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Preview
                    try:
                        if uploaded.name.endswith('.csv'):
                            preview_df = pd.read_csv(uploaded, nrows=5)
                        else:
                            preview_df = pd.read_excel(uploaded, nrows=5)
                        
                        st.markdown("**Preview 5 dòng đầu:**")
                        st.dataframe(preview_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Không đọc được file: {str(e)}")
                
                with col2:
                    if st.button("🚀 Import", type="primary", use_container_width=True):
                        with st.spinner("⏳ Đang import..."):
                            uploaded.seek(0)  # Reset file pointer
                            success = self.upload_csv_to_supabase(uploaded)
                            
                            if success > 0:
                                st.success(f"✅ Đã import {success} records!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Import thất bại")
        
        st.divider()
        
        # ===== SECTION 2: FILTERS =====
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
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
            search = st.text_input(
                "🔎 Tìm kiếm:",
                placeholder="Tìm trong title/content..."
            )
        
        with col3:
            limit = st.number_input(
                "📊 Số lượng:",
                min_value=10,
                max_value=500,
                value=50,
                step=10
            )
        
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("🔄", use_container_width=True, help="Tải lại"):
                st.rerun()
        
        st.divider()
        
        # ===== SECTION 3: LOAD & DISPLAY =====
        with st.spinner("📡 Đang tải từ Supabase..."):
            history = self.get_history(
                limit=limit,
                event_type=event_filter if event_filter != "all" else None,
                search_term=search if search.strip() else None
            )
        
        if history:
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            # Count by type
            types_count = {}
            for log in history:
                t = log.get("type", "unknown")
                types_count[t] = types_count.get(t, 0) + 1
            
            col1.metric("📝 Tổng", len(history))
            col2.metric("📚 Sách", types_count.get("book_analysis", 0))
            col3.metric("🗣️ Tranh biện", types_count.get("debate", 0))
            col4.metric("✍️ Dịch", types_count.get("translation", 0))
            
            st.divider()
            
            # Export button
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("💾 Export CSV", use_container_width=True):
                    df_export = pd.DataFrame(history)
                    csv = df_export.to_csv(index=False)
                    
                    st.download_button(
                        label="⬇️ Tải xuống",
                        data=csv,
                        file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
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
                sentiment = entry.get("sentiment_label", "")
                
                # Icon theo loại
                icon_map = {
                    "book_analysis": "📚",
                    "debate": "🗣️",
                    "translation": "✍️",
                    "voice": "🎙️"
                }
                icon = icon_map.get(event_type, "📄")
                
                # Sentiment badge
                sentiment_badge = ""
                if sentiment:
                    color_map = {
                        "Hào hứng": "🟢",
                        "Trung tính": "🟡",
                        "Tiêu cực": "🔴"
                    }
                    sentiment_badge = color_map.get(sentiment, "")
                
                # Expander
                with st.expander(
                    f"{icon} **{title}** {sentiment_badge} • {created_at[:16]} • {user}",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Loại:** {event_type}")
                        st.markdown(f"**Người dùng:** {user}")
                        st.markdown(f"**Thời gian:** {created_at}")
                        if sentiment:
                            st.markdown(f"**Cảm xúc:** {sentiment} (score: {entry.get('sentiment_score', 0):.2f})")
                    
                    with col2:
                        # AI Provider badge (nếu có)
                        if "provider" in entry:
                            provider = entry["provider"]
                            provider_icon = {
                                "gemini": "🟡",
                                "grok": "🟢",
                                "deepseek": "🟣"
                            }.get(provider, "⚫")
                            st.info(f"{provider_icon} {provider.upper()}")
                    
                    st.divider()
                    st.markdown("**Nội dung:**")
                    
                    # Truncate long content
                    if len(content) > 2000:
                        st.markdown(content[:2000] + "...")
                        with st.expander("📖 Xem toàn bộ"):
                            st.markdown(content)
                    else:
                        st.markdown(content)
        
        else:
            st.info("📭 Chưa có log nào. Hãy bắt đầu phân tích hoặc tranh biện!")
    
    @staticmethod
    def log_event(
        event_type: str,
        title: str,
        content: str,
        provider: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        sentiment_label: Optional[str] = None
    ):
        """
        Static method để log từ bất kỳ module nào
        
        Args:
            event_type: book_analysis, debate, translation, voice
            title: Tiêu đề
            content: Nội dung chi tiết
            provider: AI provider (gemini, grok, deepseek)
            sentiment_score: Điểm cảm xúc (0-1)
            sentiment_label: Nhãn cảm xúc
        """
        try:
            from supabase import create_client
            
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
            
            if url and key:
                db = create_client(url, key)
                
                data = {
                    "type": event_type,
                    "title": title,
                    "content": content,
                    "user_name": st.session_state.get("current_user", "Guest")
                }
                
                # Optional fields
                if provider:
                    data["provider"] = provider
                if sentiment_score is not None:
                    data["sentiment_score"] = sentiment_score
                if sentiment_label:
                    data["sentiment_label"] = sentiment_label
                
                db.table("history_logs").insert(data).execute()
        
        except Exception:
            pass  # Silent fail
