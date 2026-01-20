"""
META-BLOCK: Embedding Engine
Nguyên tắc: Single Responsibility - Chỉ lo embedding vector
"""

import streamlit as st
from typing import List, Union
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    """
    Quản lý embedding vectors
    
    Features:
    - Auto load multilingual model
    - Cache embeddings
    - Batch processing
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = self._load_model(model_name)
    
    @st.cache_resource
    def _load_model(_self, model_name: str):
        """Load model with cache"""
        return SentenceTransformer(model_name, device='cpu')
    
    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Encode single or batch texts"""
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts).tolist()
    
    def compute_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity([emb1], [emb2])[0][0]
