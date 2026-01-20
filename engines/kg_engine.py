import networkx as nx
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
# 👇 Import đầy đủ để không bị lỗi 'Node is not defined'
from streamlit_agraph import agraph, Node, Edge, Config

class KnowledgeGraphEngine:
    def __init__(self, embedding_engine, config: Optional[Dict] = None):
        self.graph = nx.DiGraph()
        self.embedding_engine = embedding_engine
        self.config = config or {}
    
    def add_book(self, title: str, content_summary: str, first_principles: str = "", metadata: Optional[Dict] = None):
        if metadata is None: metadata = {}
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
        self._auto_link_node(node_id)
        return node_id
    
    def _auto_link_node(self, node_id: str):
        threshold = self.config.get("similarity_threshold", 0.7)
        new_emb = self.graph.nodes[node_id]["embedding"]
        
        for existing_id in list(self.graph.nodes):
            if existing_id == node_id: continue
            existing_emb = self.graph.nodes[existing_id]["embedding"]
            sim = cosine_similarity([new_emb], [existing_emb])[0][0]
            
            if sim > threshold:
                self.graph.add_edge(existing_id, node_id, weight=sim, type="similar")

    def render_graph(self):
        """Vẽ biểu đồ dùng Agraph"""
        if self.graph.number_of_nodes() == 0:
            return None
        
        nodes = []
        edges = []
        
        for node_id, data in self.graph.nodes(data=True):
            nodes.append(Node(
                id=node_id,
                label=data.get("title", "Unknown")[:20] + "...",
                size=25,
                color="#007bff",
                title=f"Nguyên lý: {data.get('first_principles', 'N/A')}"
            ))
        
        for source, target, data in self.graph.edges(data=True):
            edges.append(Edge(
                source=source,
                target=target,
                label=f"{data.get('weight', 0):.2f}",
                color="#6c757d"
            ))
        
        config = Config(width=800, height=600, directed=True, physics=True, hierarchical=False)
        
        # Trả về component để render trực tiếp
        return agraph(nodes=nodes, edges=edges, config=config)

    def upgrade_from_excel(self, excel_file):
        import pandas as pd
        try:
            df = pd.read_excel(excel_file).dropna(subset=["Tên sách"])
            count = 0
            for _, row in df.iterrows():
                title = str(row["Tên sách"]).strip()
                summary = str(row.get("CẢM NHẬN", title)).strip()
                if not summary or summary == "nan": summary = title
                
                metadata = {"author": str(row.get("Tác giả", "Unknown"))}
                self.add_book(title, summary, first_principles="", metadata=metadata)
                count += 1
            return count
        except Exception as e:
            st.error(f"Excel Error: {e}")
            return 0
