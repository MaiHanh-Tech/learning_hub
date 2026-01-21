"""
Weaver Feature - Migrated from module_weaver.py
Tabs: RAG | Debate (Solo + Multi) | History with Bayes
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
from typing import Optional
from datetime import datetime
from engines.ai_engine import AIEngine
from engines.embedding_engine import EmbeddingEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock
from utils.file_processor import doc_file
from prompts import BOOK_ANALYSIS_PROMPT, DEBATE_PERSONAS
from supabase import create_client, Client
import plotly.express as px


class WeaverFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        embedding_engine: EmbeddingEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None,
        **kwargs
    ):
        self.ai = ai_engine
        self.embedding = embedding_engine
        self.i18n = i18n
        self.config = config
        
        # Supabase
        self.db = None
        try:
            url = st.secrets.get("supabase", {}).get("url")
            key = st.secrets.get("supabase", {}).get("key")
            if url and key:
                self.db = create_client(url, key)
        except:
            pass
        
        # Session state
        if "weaver_chat" not in st.session_state:
            st.session_state.weaver_chat = []
    
    def t(self, key: str) -> str:
        """Get translation"""
        if self.i18n:
            return self.i18n.t(key, key)
        # Fallback translations
        trans = {
            "tab1": "📚 Phân Tích Sách",
            "tab2": "🗣️ Tranh Biện", 
            "tab3": "⏳ Nhật Ký",
            "t1_up_doc": "Tải tài liệu (PDF/Docx)",
            "t1_btn": "🚀 PHÂN TÍCH NGAY",
            "t3_persona_label": "Chọn Đối Thủ:",
            "t3_input": "Nhập chủ đề tranh luận...",
            "t3_clear": "🗑️ Xóa Chat"
        }
        return trans.get(key, key)
    
    def render(self):
        st.header("🧠 The Cognitive Weaver")
        
        # 3 TABS (bỏ Dịch & Voice)
        tab1, tab2, tab3 = st.tabs([
            self.t("tab1"),  # Phân Tích Sách
            self.t("tab2"),  # Tranh Biện
            self.t("tab3")   # Nhật Ký
        ])
        
        with tab1:
            self._render_rag()
        
        with tab2:
            self._render_debate()
        
        with tab3:
            self._render_history()
    
    def _render_rag(self):
        """TAB 1: RAG - Phân tích sách"""
        st.subheader("Trợ lý Nghiên cứu")
        
        uploaded_files = st.file_uploader(
            self.t("t1_up_doc"),
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="weaver_rag_files"
        )
        
        if st.button(self.t("t1_btn"), type="primary", use_container_width=True):
            if not uploaded_files:
                st.warning("Vui lòng tải lên tài liệu")
                return
            
            for f in uploaded_files:
                text = doc_file(f)
                if not text:
                    st.warning(f"Không đọc được {f.name}")
                    continue
                
                with st.spinner(f"Đang phân tích {f.name}..."):
                    prompt = f"Phân tích tài liệu '{f.name}'. Nội dung: {text[:30000]}"
                    
                    # Gọi AI với priority Gemini Pro
                    response = self.ai.generate(
                        prompt,
                        system_instruction=BOOK_ANALYSIS_PROMPT,
                        model_type="pro"
                    )
                    
                    if response.success:
                        st.markdown(f"### 📄 {f.name}")
                        st.markdown(response.content)
                        st.markdown("---")
                        
                        # Log
                        self._log_to_supabase(
                            "Phân Tích Sách",
                            f.name,
                            response.content[:500],
                            response.provider
                        )
                    else:
                        st.error(f"❌ {response.error}")
    
    def _render_debate(self):
        """TAB 2: Debate - Solo + Multi-Agent"""
        st.subheader("Đấu Trường Tư Duy")
        
        mode = st.radio(
            "Mode:",
            ["👤 Solo", "⚔️ Multi-Agent"],
            horizontal=True,
            key="weaver_debate_mode"
        )
        
        # Init chat history
        if "weaver_chat" not in st.session_state:
            st.session_state.weaver_chat = []
        
        # ========== MODE 1: SOLO ==========
        if mode == "👤 Solo":
            c1, c2 = st.columns([3, 1])
            
            with c1:
                persona = st.selectbox(
                    self.t("t3_persona_label"),
                    list(DEBATE_PERSONAS.keys()),
                    key="weaver_solo_persona"
                )
            
            with c2:
                if st.button(self.t("t3_clear"), key="weaver_solo_clear"):
                    st.session_state.weaver_chat = []
                    st.rerun()
            
            # Hiển thị history
            for msg in st.session_state.weaver_chat:
                st.chat_message(msg["role"]).write(msg["content"])
            
            # Input
            if prompt := st.chat_input(self.t("t3_input")):
                # Add user message
                st.chat_message("user").write(prompt)
                st.session_state.weaver_chat.append({
                    "role": "user",
                    "content": prompt
                })
                
                # Build context from history
                recent = st.session_state.weaver_chat[-10:]
                context = "\n".join([
                    f"{m['role'].upper()}: {m['content']}"
                    for m in recent
                ])
                
                full_prompt = f"""
LỊCH SỬ HỘI THOẠI:
{context}

NHIỆM VỤ: Dựa vào lịch sử trên, hãy trả lời câu hỏi mới nhất của USER.
Nếu USER hỏi "câu hỏi cũ" hoặc "vừa rồi", hãy tham chiếu đến lịch sử.
"""
                
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Đang suy nghĩ..."):
                        # Ưu tiên Gemini Pro
                        response = self.ai.generate(
                            full_prompt,
                            system_instruction=DEBATE_PERSONAS[persona],
                            model_type="pro"
                        )
                        
                        if response.success:
                            st.write(response.content)
                            
                            # Save assistant response
                            st.session_state.weaver_chat.append({
                                "role": "assistant",
                                "content": response.content
                            })
                            
                            # Log
                            full_log = f"👤 USER: {prompt}\n\n🤖 {persona}: {response.content}"
                            self._log_to_supabase(
                                "Tranh Biện Solo",
                                f"{persona} - {prompt[:50]}...",
                                full_log,
                                response.provider
                            )
                        else:
                            st.error(f"❌ {response.error}")
        
        # ========== MODE 2: MULTI-AGENT ==========
        else:
            st.info("💡 Chọn 2-3 nhân vật để họ tự tranh luận.")
            
            participants = st.multiselect(
                "Chọn Hội đồng Tranh Biện:",
                list(DEBATE_PERSONAS.keys()),
                default=list(DEBATE_PERSONAS.keys())[:2],
                max_selections=3,
                key="weaver_multi_participants"
            )
            
            topic = st.text_input(
                "Chủ đề tranh luận:",
                placeholder="VD: Tiền có mua được hạnh phúc không?",
                key="weaver_multi_topic"
            )
            
            c_start, c_del = st.columns([1, 5])
            
            with c_start:
                start_btn = st.button(
                    "🔥 KHAI CHIẾN",
                    key="weaver_multi_start",
                    disabled=(len(participants) < 2 or not topic),
                    type="primary"
                )
            
            with c_del:
                if st.button("🗑️ Xóa Bàn", key="weaver_multi_clear"):
                    st.session_state.weaver_chat = []
                    st.rerun()
            
            # Hiển thị history cũ
            for msg in st.session_state.weaver_chat:
                if msg["role"] == "system":
                    st.info(msg["content"])
                else:
                    st.chat_message("assistant").write(msg["content"])
            
            # Chạy debate
            if start_btn and topic and len(participants) >= 2:
                # Reset
                st.session_state.weaver_chat = []
                
                # Mở đầu
                start_msg = f"📢 **CHỦ TỌA:** Khai mạc tranh luận về: *'{topic}'*"
                st.session_state.weaver_chat.append({
                    "role": "system",
                    "content": start_msg
                })
                st.info(start_msg)
                
                # Full transcript
                transcript = [start_msg]
                
                with st.status("🔥 Cuộc chiến đang diễn ra (3 vòng)...") as status:
                    for round_num in range(1, 4):
                        status.update(label=f"🔄 Vòng {round_num}/3...")
                        
                        for p_name in participants:
                            # Context
                            if len(st.session_state.weaver_chat) > 1:
                                recent = st.session_state.weaver_chat[-3:]
                                context_str = "\n".join([
                                    f"- {m['content']}"
                                    for m in recent
                                    if m['role'] != 'system'
                                ])
                            else:
                                context_str = topic
                            
                            # Build prompt
                            if round_num == 1:
                                p_prompt = f"""
CHỦ ĐỀ TRANH LUẬN: {topic}

NHIỆM VỤ (Vòng 1 - Khai mạc):
Bạn là {p_name}. Hãy đưa ra quan điểm mở đầu của mình về chủ đề này.
Nêu rõ lập trường và 2-3 lý lẽ chính (dưới 200 từ).
"""
                            else:
                                p_prompt = f"""
CHỦ ĐỀ: {topic}

TÌNH HUỐNG HIỆN TẠI:
{context_str}

NHIỆM VỤ (Vòng {round_num} - Phản biện):
Bạn là {p_name}. Hãy:
1. Chỉ ra điểm yếu trong lập luận của đối thủ
2. Củng cố quan điểm của mình
3. Đưa ra thêm 1 ví dụ minh họa
(Dưới 200 từ, súc tích)
"""
                            
                            # Call AI (Ưu tiên Gemini Pro)
                            try:
                                response = self.ai.generate(
                                    p_prompt,
                                    system_instruction=DEBATE_PERSONAS[p_name],
                                    model_type="pro"
                                )
                                
                                if response.success:
                                    content_fmt = f"**{p_name}:** {response.content}"
                                    
                                    # Save
                                    st.session_state.weaver_chat.append({
                                        "role": "assistant",
                                        "content": content_fmt
                                    })
                                    
                                    transcript.append(content_fmt)
                                    
                                    # Display
                                    with st.chat_message("assistant"):
                                        st.write(content_fmt)
                                    
                                    # Nghỉ tránh rate limit
                                    time.sleep(6)
                            
                            except Exception as e:
                                st.error(f"⚠️ Lỗi {p_name}: {str(e)}")
                    
                    status.update(label="✅ Tranh luận kết thúc!", state="complete")
                
                # Log
                full_log = "\n\n".join(transcript)
                self._log_to_supabase(
                    "Hội đồng Tranh Biện",
                    f"Chủ đề: {topic}",
                    full_log
                )
                
                st.toast("💾 Đã lưu biên bản vào Nhật Ký!", icon="✅")
                
                # Xem toàn bộ
                with st.expander("📄 Xem Toàn Bộ Biên Bản", expanded=False):
                    st.markdown(full_log)
    
    def _render_history(self):
        """TAB 3: Nhật Ký với Bayesian Analysis"""
        st.subheader("⏳ Nhật Ký & Phản Chiếu Tư Duy")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("🔄 Tải lại", key="weaver_history_refresh"):
                if 'history_cloud' in st.session_state:
                    del st.session_state['history_cloud']
                st.rerun()
        
        # Load data
        data = self._load_history()
        
        if data:
            df_h = pd.DataFrame(data)
            
            # Biểu đồ cảm xúc (nếu có)
            if "sentiment_score" in df_h.columns:
                try:
                    df_h["score"] = pd.to_numeric(df_h["sentiment_score"], errors='coerce').fillna(0)
                    
                    st.caption("📉 Biểu đồ dao động trạng thái cảm xúc/tư duy:")
                    fig = px.line(
                        df_h,
                        x="created_at",
                        y="score",
                        markers=True,
                        color_discrete_sequence=["#76FF03"],
                        labels={"score": "Chỉ số Tích cực", "created_at": "Thời gian"}
                    )
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
            
            # Bayesian Analysis
            with st.expander("🔮 Phân tích Tư duy theo Bayes (E.T. Jaynes)", expanded=False):
                st.info("AI sẽ coi Lịch sử hoạt động là 'Evidence' để suy luận ra 'Objective Function' và sự dịch chuyển niềm tin.")
                
                if st.button("🧠 Chạy Mô hình Bayes", key="weaver_bayes_run"):
                    with st.spinner("Đang tính toán xác suất hậu nghiệm (Posterior)..."):
                        # Lấy 10 logs gần nhất
                        recent_logs = df_h.tail(10).to_dict(orient="records")
                        logs_text = json.dumps(recent_logs, ensure_ascii=False, indent=2)
                        
                        bayes_prompt = f"""
Đóng vai một nhà khoa học tư duy theo trường phái E.T. Jaynes (sách 'Probability Theory: The Logic of Science').

DỮ LIỆU QUAN SÁT (EVIDENCE):
Đây là nhật ký hoạt động:
{logs_text}

NHIỆM VỤ:
Hãy phân tích chuỗi hành động này như một bài toán suy luận Bayes.
1. **Xác định Priors (Niềm tin tiên nghiệm):** Dựa trên các hành động đầu, tôi đang quan tâm/tin tưởng điều gì?
2. **Cập nhật Likelihood (Khả năng):** Các hành động tiếp theo củng cố hay làm yếu đi niềm tin đó?
3. **Kết luận Posterior (Hậu nghiệm):** Trạng thái tư duy hiện tại đang hội tụ về đâu? Có mâu thuẫn (Inconsistency) nào trong logic hành động không?

Trả lời ngắn gọn, sâu sắc, dùng thuật ngữ xác suất nhưng dễ hiểu.
"""
                        
                        # Call AI Pro
                        response = self.ai.generate(
                            bayes_prompt,
                            model_type="pro"
                        )
                        
                        if response.success:
                            st.markdown(response.content)
                        else:
                            st.error(f"❌ {response.error}")
            
            # Danh sách chi tiết
            st.divider()
            st.write("📜 **Chi tiết Nhật ký:**")
            
            # Đảo ngược để xem mới nhất trước
            for _, item in df_h.iloc[::-1].iterrows():
                time_str = str(item.get('created_at', ''))[:19]
                type_str = str(item.get('type', ''))
                title_str = str(item.get('title', ''))
                content_str = str(item.get('content', ''))
                provider = str(item.get('provider', ''))
                
                # Icon
                icon = "📕"
                if "Tranh Biện" in type_str:
                    icon = "🗣️"
                elif "Dịch" in type_str:
                    icon = "✍️"
                elif "Audio" in type_str:
                    icon = "🎙️"
                
                # Provider badge
                provider_badge = ""
                if provider:
                    icon_map = {"gemini": "🟡", "grok": "🟢", "deepseek": "🟣"}
                    provider_badge = f" {icon_map.get(provider, '⚫')} {provider.upper()}"
                
                # Truncate content cho preview
                preview = content_str[:100] + "..." if len(content_str) > 100 else content_str
                
                # Expander
                with st.expander(
                    f"{icon} {time_str} | {type_str} | {title_str}{provider_badge}",
                    expanded=False
                ):
                    st.markdown(content_str)
                    
                    # Sentiment nếu có
                    if 'sentiment_label' in item and item['sentiment_label']:
                        st.caption(f"Cảm xúc: {item['sentiment_label']} ({item.get('sentiment_score', 0)})")
        else:
            st.info("📭 Chưa có dữ liệu lịch sử.")
    
    def _load_history(self):
        """Load history từ Supabase"""
        if 'history_cloud' in st.session_state:
            return st.session_state.history_cloud
        
        if not self.db:
            return []
        
        try:
            response = self.db.table("history_logs").select("*").order("created_at", desc=True).limit(50).execute()
            data = response.data or []
            st.session_state.history_cloud = data
            return data
        except:
            return []
    
    def _log_to_supabase(self, type_str, title, content, provider=None):
        """Log vào Supabase"""
        if not self.db:
            return
        
        try:
            data = {
                "type": type_str,
                "title": title,
                "content": content,
                "user_name": st.session_state.get("current_user", "Guest")
            }
            
            if provider:
                data["provider"] = provider
            
            self.db.table("history_logs").insert(data).execute()
        except:
            pass
