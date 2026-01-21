"""
CFO Feature - Migrated from module_cfo.py
Tabs: KPIs | Cost Analysis | Risk Detection | What-If
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from typing import Optional
from engines.ai_engine import AIEngine
from core.i18n_block import I18nBlock
from core.config_block import ConfigBlock


class CFOFeature:
    def __init__(
        self,
        ai_engine: AIEngine,
        i18n: Optional[I18nBlock] = None,
        config: Optional[ConfigBlock] = None
    ):
        self.ai = ai_engine
        self.i18n = i18n
        self.config = config
        
        # Init data
        if 'df_fin' not in st.session_state:
            st.session_state.df_fin = self._create_sample_data()
    
    def _create_sample_data(self):
        """Tạo dữ liệu mẫu KPI"""
        dates = pd.date_range(start="2023-01-01", periods=24, freq="ME")
        df = pd.DataFrame({"Tháng": dates})
        
        np.random.seed(42)
        df["Doanh Thu"] = np.random.randint(5000, 8000, 24) * 1000000
        df["Giá Vốn"] = df["Doanh Thu"] * 0.6
        df["CP Lương"] = np.random.randint(500, 800, 24) * 1000000
        df["CP Marketing"] = df["Doanh Thu"] * 0.1
        df["CP Khác"] = np.random.randint(100, 200, 24) * 1000000
        df["Chi Phí VH"] = df["CP Lương"] + df["CP Marketing"] + df["CP Khác"]
        df["Lợi Nhuận ST"] = df["Doanh Thu"] - df["Giá Vốn"] - df["Chi Phí VH"]
        df["Dòng Tiền Thực"] = df["Lợi Nhuận ST"] * 0.8
        df["Công Nợ Phải Thu"] = np.random.randint(1000, 2000, 24) * 1000000
        df["Hàng Tồn Kho Tổng"] = np.random.randint(1000, 2000, 24) * 1000000
        df["TS Ngắn Hạn"] = np.random.randint(2000, 3000, 24) * 1000000
        df["Nợ Ngắn Hạn"] = np.random.randint(1000, 1500, 24) * 1000000
        df["Vốn Chủ Sở Hữu"] = np.random.randint(5000, 6000, 24) * 1000000
        
        # Gài bẫy cho ML
        df.loc[20, "Chi Phí VH"] = 3000000000
        
        return df
    
    def _calculate_kpi(self, df):
        """Tính các chỉ số tài chính"""
        try:
            df["Current Ratio"] = df["TS Ngắn Hạn"] / df["Nợ Ngắn Hạn"].replace(0, 1)
            df["Gross Margin"] = (df["Doanh Thu"] - df["Giá Vốn"]) / df["Doanh Thu"].replace(0, 1) * 100
            df["ROS"] = df["Lợi Nhuận ST"] / df["Doanh Thu"].replace(0, 1) * 100
        except:
            pass
        return df
    
    def _detect_fraud(self, df):
        """Phát hiện gian lận bằng Isolation Forest"""
        iso = IsolationForest(contamination=0.05, random_state=42)
        col = "Chi Phí VH" if "Chi Phí VH" in df.columns else df.columns[1]
        df['Anomaly'] = iso.fit_predict(df[[col]])
        return df[df['Anomaly'] == -1]
    
    def render(self):
        # Get current language
        lang = st.session_state.get("current_language", "vi")
        
        # Translations
        trans = {
            "vi": {
                "title": "💰 CFO Controller Dashboard",
                "tab1": "📊 KPIs & Sức Khỏe",
                "tab2": "📉 Phân Tích Chi Phí",
                "tab3": "🕵️ Rủi Ro & Check",
                "tab4": "🔮 Dự Báo & What-If",
                "health": "Sức khỏe Tài chính Tháng gần nhất",
                "revenue": "Doanh Thu",
                "profit": "Lợi Nhuận ST",
                "cashflow": "Dòng Tiền",
                "cost_structure": "Cấu trúc Chi phí",
                "ai_assistant": "🤖 Trợ lý Phân tích:",
                "ask_about": "Hỏi về chi phí...",
                "fraud_scan": "Quét Gian Lận (ML)",
                "scan_now": "🔍 Quét ngay",
                "cross_check": "Cross-Check (Đối chiếu)",
                "tax_form": "Số liệu Thuế (Tờ khai):",
                "erp_ledger": "Số liệu Sổ cái (ERP):",
                "compare": "So khớp",
                "whatif": "🎛️ What-If Analysis",
                "whatif_desc": "Giả lập kịch bản: Nếu thay đổi đầu vào thì Lợi nhuận ra sao?",
                "price_change": "Tăng/Giảm Giá Bán (%)",
                "cost_change": "Tăng/Giảm Chi Phí (%)",
                "base_profit": "Lợi Nhuận Gốc",
                "new_profit": "Lợi Nhuận Mới",
                "found_anomaly": "Phát hiện {n} tháng bất thường!",
                "data_clean": "Dữ liệu sạch.",
                "mismatch": "Lệch: {diff}. Rủi ro truy thu thuế!",
                "matched": "Khớp!"
            },
            "en": {
                "title": "💰 CFO Controller Dashboard",
                "tab1": "📊 KPIs & Health",
                "tab2": "📉 Cost Analysis",
                "tab3": "🕵️ Risk & Check",
                "tab4": "🔮 Forecast & What-If",
                "health": "Financial Health (Latest Month)",
                "revenue": "Revenue",
                "profit": "Net Profit",
                "cashflow": "Cash Flow",
                "cost_structure": "Cost Structure",
                "ai_assistant": "🤖 AI Assistant:",
                "ask_about": "Ask about costs...",
                "fraud_scan": "Fraud Detection (ML)",
                "scan_now": "🔍 Scan Now",
                "cross_check": "Cross-Check",
                "tax_form": "Tax Filing Data:",
                "erp_ledger": "ERP Ledger Data:",
                "compare": "Compare",
                "whatif": "🎛️ What-If Analysis",
                "whatif_desc": "Simulate scenarios: How profit changes with different inputs?",
                "price_change": "Price Change (%)",
                "cost_change": "Cost Change (%)",
                "base_profit": "Base Profit",
                "new_profit": "New Profit",
                "found_anomaly": "Found {n} anomalous months!",
                "data_clean": "Data is clean.",
                "mismatch": "Mismatch: {diff}. Tax audit risk!",
                "matched": "Matched!"
            },
            "zh": {
                "title": "💰 CFO 控制器仪表板",
                "tab1": "📊 关键指标 & 健康",
                "tab2": "📉 成本分析",
                "tab3": "🕵️ 风险 & 检查",
                "tab4": "🔮 预测 & 假设分析",
                "health": "财务健康状况（最近月份）",
                "revenue": "收入",
                "profit": "净利润",
                "cashflow": "现金流",
                "cost_structure": "成本结构",
                "ai_assistant": "🤖 AI 助手:",
                "ask_about": "询问成本...",
                "fraud_scan": "欺诈检测 (ML)",
                "scan_now": "🔍 立即扫描",
                "cross_check": "交叉检查",
                "tax_form": "税务申报数据:",
                "erp_ledger": "ERP 账本数据:",
                "compare": "比较",
                "whatif": "🎛️ 假设分析",
                "whatif_desc": "模拟场景：不同输入如何影响利润？",
                "price_change": "价格变化 (%)",
                "cost_change": "成本变化 (%)",
                "base_profit": "基准利润",
                "new_profit": "新利润",
                "found_anomaly": "发现 {n} 个异常月份!",
                "data_clean": "数据干净。",
                "mismatch": "不匹配: {diff}。税务审计风险!",
                "matched": "匹配!"
            }
        }
        
        t = trans.get(lang, trans["vi"])
        
        st.header(t["title"])
        
        # Get data
        df = self._calculate_kpi(st.session_state.df_fin.copy())
        last = df.iloc[-1]
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            t["tab1"],
            t["tab2"],
            t["tab3"],
            t["tab4"]
        ])
        
        # TAB 1: KPIs
        with tab1:
            st.subheader(t["health"])
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(t["revenue"], f"{last['Doanh Thu']/1e9:.1f} tỷ")
            k2.metric(t["profit"], f"{last['Lợi Nhuận ST']/1e9:.1f} tỷ")
            k3.metric("ROS", f"{last.get('ROS',0):.1f}%")
            k4.metric(t["cashflow"], f"{last['Dòng Tiền Thực']/1e9:.1f} tỷ")
            
            st.line_chart(df.set_index("Tháng")[["Doanh Thu", "Lợi Nhuận ST"]])
        
        # TAB 2: Chi Phí & AI
        with tab2:
            c1, c2 = st.columns([2, 1])
            
            with c1:
                fig = px.bar(
                    df,
                    x="Tháng",
                    y=["Giá Vốn", "Chi Phí VH"],
                    title=t["cost_structure"]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.write(t["ai_assistant"])
                q = st.text_input(t["ask_about"], key="cfo_ai_question")
                
                if q:
                    with st.spinner("AI đang soi số liệu..."):
                        context = f"Dữ liệu tháng cuối: Doanh thu {last['Doanh Thu']}, Giá vốn {last['Giá Vốn']}, CP {last['Chi Phí VH']}."
                        
                        response = self.ai.generate(
                            q,
                            system_instruction=f"Bạn là Kế toán trưởng. Phân tích dựa trên: {context}",
                            model_type="flash"
                        )
                        
                        if response.success:
                            st.write(response.content)
                        else:
                            st.error(f"❌ {response.error}")
        
        # TAB 3: Rủi ro & Cross-check
        with tab3:
            c_risk, c_check = st.columns(2)
            
            with c_risk:
                st.subheader(t["fraud_scan"])
                
                if st.button(t["scan_now"], key="cfo_fraud_scan"):
                    bad = self._detect_fraud(df)
                    
                    if not bad.empty:
                        st.error(t["found_anomaly"].format(n=len(bad)))
                        st.dataframe(bad[["Tháng", "Chi Phí VH"]])
                    else:
                        st.success(t["data_clean"])
            
            with c_check:
                st.subheader(t["cross_check"])
                
                val_a = st.number_input(
                    t["tax_form"],
                    value=100.0,
                    key="cfo_tax_a"
                )
                val_b = st.number_input(
                    t["erp_ledger"],
                    value=105.0,
                    key="cfo_tax_b"
                )
                
                if st.button(t["compare"], key="cfo_cross_check"):
                    diff = val_b - val_a
                    
                    if diff != 0:
                        st.warning(t["mismatch"].format(diff=diff))
                    else:
                        st.success(t["matched"])
        
        # TAB 4: What-If Analysis
        with tab4:
            st.subheader(t["whatif"])
            st.caption(t["whatif_desc"])
            
            base_rev = last['Doanh Thu']
            base_profit = last['Lợi Nhuận ST']
            
            c_s1, c_s2 = st.columns(2)
            
            with c_s1:
                delta_price = st.slider(
                    t["price_change"],
                    -20, 20, 0,
                    key="cfo_price_delta"
                )
            
            with c_s2:
                delta_cost = st.slider(
                    t["cost_change"],
                    -20, 20, 0,
                    key="cfo_cost_delta"
                )
            
            # Calculate new profit
            new_rev = base_rev * (1 + delta_price/100)
            new_profit = base_profit + (new_rev - base_rev) - (last['Chi Phí VH'] * delta_cost/100)
            
            col_res1, col_res2 = st.columns(2)
            col_res1.metric(t["base_profit"], f"{base_profit/1e9:.2f} tỷ")
            col_res2.metric(
                t["new_profit"],
                f"{new_profit/1e9:.2f} tỷ",
                delta=f"{(new_profit - base_profit)/1e9:.2f} tỷ"
            )
