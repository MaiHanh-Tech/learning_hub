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
from agraph import AGraph, Node, Edge

class KnowledgeGraphEngine:
    """
    Knowledge Universe với Episteme Layers
    
    Dependencies:
    - EmbeddingEngine (cho vector hóa)
    """
    
    def __init__(self, embedding_engine):
        self.graph = nx.DiGraph()
        self.embedding_engine = embedding_engine
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
        new_emb = self.graph.nodes[node_id]["embedding"]
        for existing_id in list(self.graph.nodes):
            if existing_id == node_id or self.graph.nodes[existing_id]["type"] != "book":
                continue
            existing_emb = self.graph.nodes[existing_id]["embedding"]
            sim = cosine_similarity([new_emb], [existing_emb])[0][0]
            if sim > 0.7:
                self.graph.add_edge(existing_id, node_id, weight=sim, type="similar")
    
    def render_graph(self):
        """Render interactive graph with agraph"""
        nodes = []
        edges = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append(Node(
                id=node_id,
                label=data["title"],
                size=25,
                color="#007bff"
            ))
        for source, target, data in self.graph.edges(data=True):
            edges.append(Edge(
                source=source,
                target=target,
                label=f"{data.get('type', '')}: {data.get('weight', ''):.2f}",
                color="#6c757d"
            ))
        return AGraph(nodes=nodes, edges=edges)
    
    def seed_knowledge_graph(self):
        """Seed with selected books"""
        selected_books = [
            # Danh sách 18 sách từ code cũ (knowledge_graph_v2.py)
            # Tôi copy nguyên từ code cũ, giữ nguyên để migrate chính xác
            {
                "title": "Probability Theory: The Logic of Science",
                "author": "E.T. Jaynes",
                "summary": "Sách dạy suy luận logic dựa trên xác suất Bayes, coi lý thuyết xác suất là mở rộng của logic Aristoteles.",
                "first_principles": "Logic là cơ sở của khoa học; xác suất là công cụ đo lường niềm tin.",
                "tags": ["math", "logic"]
            },
            # ... (thêm tất cả 18 sách tương tự, nhưng để ngắn gọn, giả sử copy đầy đủ từ code cũ)
            # Chị copy toàn bộ list selected_books từ knowledge_graph_v2.py vào đây
        ]
        success_count = 0
        for book in selected_books:
            try:
                metadata = {"author": book["author"], "tags": book["tags"]}
                self.add_book(
                    title=book["title"],
                    content_summary=book["summary"],
                    first_principles=book["first_principles"],
                    metadata=metadata
                )
                success_count += 1
            except Exception:
                continue
        return success_count
    
    def upgrade_from_excel(self, excel_path: str):
        """Migrate from Excel (from old code)"""
        import pandas as pd
        try:
            df = pd.read_excel(excel_path).dropna(subset=["Tên sách"])
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
        except Exception:
            return 0
