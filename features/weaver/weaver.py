import streamlit as st
from typing import Optional
from engines.ai_engine import AIEngine
from engines.embedding_engine import EmbeddingEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
from utils.file_processor import doc_file, clean_pdf_text
from prompts import BOOK_ANALYSIS_PROMPT, DEBATE_PERSONAS


class WeaverFeature:
    
    def __init__(
        self,
        ai_engine: AIEngine,
        embedding_engine: EmbeddingEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None,
        **kwargs  # Bỏ qua kg_engine nếu truyền vào
    ):
        self.ai = ai_engine
        self.embedding = embedding_engine
        self.i18n = i18n
        self.config = config
        
        # Session state cho Debate
        if "debate_messages" not in st.session_state:
            st.session_state.debate_messages = []
    
    def t(self, key: str, default: str = None) -> str:
        if self.i18n:
            return self.i18n.t(key, default or key)
        return default or key
    
    def render(self):
        """Main render"""
        st.title("🧠 Cognitive Weaver")
        st.caption("Phân tích sách & Tranh biện triết học")
        
        # Tabs cho 2 tính năng
        tab1, tab2 = st.tabs([
            "📚 Phân Tích Sách",
            "🗣️ Đấu Trường Tư Duy"
        ])
        
        with tab1:
            self._render_rag()
        
        with tab2:
            self._render_debate()
    
    def _render_rag(self):
        """RAG - Book Analysis"""
        st.subheader("📚 Phân Tích Sách Thông Minh")
        
        st.markdown("""
        Upload tài liệu (PDF, Docx, TXT) để AI phân tích theo **4 tầng tri thức**:
        - 🔢 Toán học & Logic
        - 🔬 Vật lý & Sinh học  
        - 🏛️ Văn hóa & Quyền lực
        - 🧘 Ý thức & Giải phóng
        """)
        
        # Upload file
        uploaded = st.file_uploader(
            "Chọn tài liệu",
            type=["pdf", "docx", "txt", "md"],
            help="File sẽ được xử lý và phân tích bởi AI"
        )
        
        if uploaded:
            with st.spinner("🔄 Đang xử lý tài liệu..."):
                try:
                    # Đọc file
                    raw_text = doc_file(uploaded)
                    if not raw_text.strip():
                        st.warning("⚠️ Tài liệu rỗng hoặc không đọc được")
                        return
                    
                    # Clean text
                    cleaned = clean_pdf_text(raw_text)
                    
                    # Hiển thị thống kê
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📄 Trang", len(raw_text) // 2000)
                    col2.metric("✍️ Ký tự", f"{len(cleaned):,}")
                    col3.metric("📊 Từ", len(cleaned.split()))
                    
                    st.divider()
                    
                    # Nút phân tích
                    if st.button("🚀 Phân Tích Ngay", type="primary", use_container_width=True):
                        with st.spinner("🤖 AI đang phân tích..."):
                            try:
                                # Gọi AI
                                response = self.ai.generate(
                                    prompt=f"{BOOK_ANALYSIS_PROMPT}\n\n{cleaned[:100000]}",
                                    model_type="pro",
                                    temperature=0.7
                                )
                                
                                if response.success:
                                    st.success(f"✅ Hoàn thành! ({response.provider}, {response.latency:.1f}s)")
                                    st.balloons()
                                    
                                    # Hiển thị kết quả
                                    st.markdown("---")
                                    st.markdown("## 📖 Kết quả Phân tích")
                                    st.markdown(response.content)
                                    
                                    # Log vào Supabase (với provider info)
                                    self._log_to_supabase(
                                        event_type="book_analysis",
                                        title=uploaded.name,
                                        content=response.content,
                                        provider=response.provider
                                    )
                                else:
                                    st.error(f"❌ {response.error}")
                            
                            except Exception as e:
                                st.error(f"❌ Lỗi phân tích: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Lỗi đọc file: {str(e)}")
    
    def _render_debate(self):
        """Debate Arena"""
        st.subheader("🗣️ Đấu Trường Tư Duy")
        
        st.markdown("""
        Tranh luận với các **nhân cách triết học** khác nhau:
        - 🎩 Shushu - Triết gia Hệ thống  
        - 🙏 Phật Tổ - Vô ngã & Duyên khởi
        - 🤔 Logic Master - Socratic + Bayesian
        - 📈 Thực Tế - ROI + Antifragile
        """)
        
        # Chọn đối thủ
        persona_options = list(DEBATE_PERSONAS.keys())
        selected = st.selectbox(
            "Chọn đối thủ:",
            persona_options,
            format_func=lambda x: x
        )
        
        # Hiển thị mô tả persona
        with st.expander("ℹ️ Phong cách của đối thủ", expanded=False):
            st.markdown(DEBATE_PERSONAS[selected])
        
        st.divider()
        
        # Input
        user_input = st.text_area(
            "Nhập chủ đề tranh luận:",
            height=120,
            placeholder="VD: 'AI có thể thay thế hoàn toàn con người không?'"
        )
        
        # Buttons
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🗣️ Bắt đầu", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning("⚠️ Vui lòng nhập chủ đề")
                else:
                    # Thêm message user
                    st.session_state.debate_messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Gọi AI
                    with st.spinner(f"{selected} đang suy nghĩ..."):
                        # Tạo full prompt từ history
                        history = "\n".join([
                            f"{m['role']}: {m['content']}"
                            for m in st.session_state.debate_messages
                        ])
                        
                        response = self.ai.generate(
                            prompt=history,
                            system_instruction=DEBATE_PERSONAS[selected],
                            model_type="pro",
                            temperature=0.8
                        )
                        
                        if response.success:
                            st.session_state.debate_messages.append({
                                "role": "assistant",
                                "content": response.content
                            })
                            
                            # Log (với provider info)
                            self._log_to_supabase(
                                event_type="debate",
                                title=f"Debate with {selected}",
                                content=f"User: {user_input}\n\nAI: {response.content[:500]}",
                                provider=response.provider
                            )
                        else:
                            st.error(f"❌ {response.error}")
        
        with col2:
            if st.button("🗑️ Xóa", use_container_width=True):
                st.session_state.debate_messages = []
                st.rerun()
        
        # Hiển thị chat history
        st.divider()
        st.markdown("### 💬 Lịch sử tranh luận")
        
        for msg in st.session_state.debate_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🗣️"):
                    st.markdown(msg["content"])
    
    def _log_to_supabase(
        self,
        event_type: str,
        title: str,
        content: str,
        provider: Optional[str] = None
    ):
        """Log hoạt động vào Supabase với provider info"""
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
                
                # Thêm provider nếu có
                if provider:
                    data["provider"] = provider
                
                db.table("history_logs").insert(data).execute()
        
        except Exception as e:
            # [Unverified] Không hiển thị lỗi log cho user
            pass
