"""
META-BLOCK: Knowledge Graph Engine
Nguyên tắc: First Principles - Xây dựng từ nguyên tắc cơ bản
"""

import networkx as nx
import numpy as np
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from pyvis.network import Network

def render_graph(self):
    """Render interactive graph with pyvis"""
    if self.graph.number_of_nodes() == 0:
        st.info("Knowledge Graph chưa có dữ liệu. Upload Excel để bắt đầu.")
        return None
    
    net = Network(height="600px", width="100%", directed=True, notebook=True)
    
    for node_id, data in self.graph.nodes(data=True):
        net.add_node(
            node_id,
            label=data.get("title", "Unknown"),
            color="#007bff",
            size=25,
            title=f"First principles: {data.get('first_principles', 'N/A')}"
        )
    
    for source, target, data in self.graph.edges(data=True):
        net.add_edge(
            source, target,
            label=f"{data.get('type', 'similar')}: {data.get('weight', 0):.2f}",
            color="#6c757d",
            width=data.get('weight', 1) * 2
        )
    
    # Render HTML
    html = net.generate_html()
    st.components.v1.html(html, height=600, scrolling=True)
    
    st.caption(f"Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    return html


class KnowledgeGraphEngine:
    """
    Knowledge Universe với Episteme Layers
    
    Dependencies:
    - EmbeddingEngine (cho vector hóa)
    """
    
    def __init__(self, embedding_engine, config: Optional[Dict] = None):
        self.graph = nx.DiGraph()
        self.embedding_engine = embedding_engine
        self.config = config or {}
        self.episteme_layers = {
            "Toán học & Logic": [],
            "Vật lý & Sinh học": [],
            "Văn hóa & Quyền lực": [],
            "Ý thức & Giải phóng": []
        }
    
    def add_book(self, title: str, content_summary: str, first_principles: str = "", metadata: Optional[Dict] = None):
        """Add book node and auto-link"""
        if metadata is None:
            metadata = {}
        node_id = f"book_{len(self.graph.nodes)}"
        embedding = self.embedding_engine.encode(content_summary)[0]
        self.graph.add_node(
            node_id,
            type="book",
            title=title,
            embedding=embedding,
            added_at=datetime.now().isoformat(),
            first_principles=first_principles,
            **metadata
        )
        layer = self._classify_episteme(content_summary, metadata.get("tags", []))
        if layer in self.episteme_layers:
            self.episteme_layers[layer].append(node_id)
        self._auto_link_node(node_id)
        return node_id
    
    def _classify_episteme(self, text: str, tags: List[str]) -> str:
        """Classify into episteme layer"""
        keywords_map = {
            "Toán học & Logic": ["logic", "math", "proof", "toán", "xác suất"],
            "Vật lý & Sinh học": ["physics", "evolution", "brain", "não bộ", "vật lý"],
            "Văn hóa & Quyền lực": ["power", "culture", "society", "quyền lực", "văn hóa"],
            "Ý thức & Giải phóng": ["consciousness", "mindfulness", "thiền", "ý thức"]
        }
        text_lower = text.lower()
        for layer, keywords in keywords_map.items():
            if any(kw in text_lower or kw in tags for kw in keywords):
                return layer
        return "Văn hóa & Quyền lực"
    
    def _auto_link_node(self, node_id: str):
        """Auto link to similar nodes"""
        threshold = self.config.get("similarity_threshold", 0.7)  # Có thể config sau
        new_emb = self.graph.nodes[node_id]["embedding"]
        for existing_id in list(self.graph.nodes):
            if existing_id == node_id or self.graph.nodes[existing_id]["type"] != "book":
                continue
            existing_emb = self.graph.nodes[existing_id]["embedding"]
            sim = cosine_similarity([new_emb], [existing_emb])[0][0]
            if sim > threshold:
                self.graph.add_edge(existing_id, node_id, weight=sim, type="similar")
    
    def render_graph(self):
        """Render interactive graph with streamlit-agraph"""
        if self.graph.number_of_nodes() == 0:
            st.info("Knowledge Graph chưa có dữ liệu sách. Upload Excel để bắt đầu.")
            return None
        
        nodes = []
        edges = []
        
        for node_id, data in self.graph.nodes(data=True):
            nodes.append(Node(
                id=node_id,
                label=data.get("title", "Unknown"),
                size=25,
                color="#007bff",
                title=f"First principles: {data.get('first_principles', 'N/A')}"  # Hover info
            ))
        
        for source, target, data in self.graph.edges(data=True):
            edges.append(Edge(
                source=source,
                target=target,
                label=f"{data.get('type', 'similar')}: {data.get('weight', 0):.2f}",
                color="#6c757d",
                width=data.get('weight', 1) * 2  # Độ dày cạnh theo similarity
            ))
        
        # Config graph (có thể tùy chỉnh sau)
        config_graph = Config(
            width=800,
            height=600,
            directed=True,
            physics=True,
            hierarchical=False
        )
        
        # Render graph
        return_value = agraph(
            nodes=nodes,
            edges=edges,
            config=config_graph
        )
        
        st.caption(f"Graph hiện tại: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return return_value
    
    def seed_knowledge_graph(self):
        """Seed with selected high-quality books (copy từ knowledge_graph_v2.py cũ)"""
        selected_books = [
            {
                "title": "Probability Theory: The Logic of Science",
                "author": "E.T. Jaynes",
                "summary": "Sách dạy suy luận logic dựa trên xác suất Bayes, coi lý thuyết xác suất là mở rộng của logic Aristoteles.",
                "first_principles": "Logic là cơ sở của khoa học; xác suất là công cụ đo lường niềm tin.",
                "tags": ["math", "logic"]
            },
            # ... (chị copy thêm 17 sách còn lại từ knowledge_graph_v2.py cũ vào đây)
            # Ví dụ:
            {
                "title": "Thinking, Fast and Slow",
                "author": "Daniel Kahneman",
                "summary": "Phân tích hai hệ thống tư duy: nhanh (trực giác) và chậm (lý trí).",
                "first_principles": "Hành vi con người bị chi phối bởi bias nhận thức.",
                "tags": ["psychology", "decision-making"]
            },
            # Thêm đầy đủ danh sách 18 sách...
        ]
        success_count = 0
        for book in selected_books:
            try:
                metadata = {"author": book["author"], "tags": book.get("tags", [])}
                self.add_book(
                    title=book["title"],
                    content_summary=book["summary"],
                    first_principles=book.get("first_principles", ""),
                    metadata=metadata
                )
                success_count += 1
            except Exception as e:
                st.warning(f"Lỗi add sách '{book.get('title', 'Unknown')}': {e}")
                continue
        st.success(f"Đã seed {success_count}/{len(selected_books)} sách vào Knowledge Graph")
        return success_count
    
    def upgrade_from_excel(self, excel_file):
        """Nâng cấp KG từ file Excel upload (migrate từ old code)"""
        import pandas as pd
        try:
            df = pd.read_excel(excel_file).dropna(subset=["Tên sách"])
            success_count = 0
            for _, row in df.iterrows():
                title = str(row["Tên sách"]).strip()
                summary = str(row.get("CẢM NHẬN", "")).strip()
                if not summary or summary == "nan":
                    continue
                metadata = {
                    "author": str(row.get("Tác giả", "Unknown")),
                    "tags": [t.strip() for t in str(row.get("Tags", "")).split(",") if t.strip()]
                }
                self.add_book(title, summary, first_principles="", metadata=metadata)
                success_count += 1
            return success_count
        except Exception as e:
            st.error(f"❌ Lỗi đọc Excel: {str(e)}")
            return 0
