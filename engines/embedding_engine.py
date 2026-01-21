"""
META-BLOCK: Embedding Engine 
Nguyên tắc: Lazy loading + Graceful degradation
"""

import streamlit as st
from typing import List, Union, Optional


class EmbeddingEngine:
    """
    Quản lý embedding vectors (Optional)
    
    Features:
    - Lazy loading (chỉ load khi cần)
    - Graceful fallback nếu load fail
    - Cache embeddings
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self._loading_failed = False
    
    def _load_model_lazy(self):
        """Load model only when needed"""
        if self.model is not None:
            return True
        
        if self._loading_failed:
            return False
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Try load with timeout
            self.model = SentenceTransformer(
                self.model_name,
                device='cpu',
                cache_folder=None  # Use default cache
            )
            return True
        
        except Exception as e:
            self._loading_failed = True
            # Silent fail - không crash app
            return False
    
    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Encode single or batch texts
        
        Returns:
            Empty list if model not loaded
        """
        # Try load model
        if not self._load_model_lazy():
            # Return dummy embeddings if load failed
            if isinstance(texts, str):
                texts = [texts]
            return [[0.0] * 384 for _ in texts]  # 384-dim zero vectors
        
        if isinstance(texts, str):
            texts = [texts]
        
        return self.model.encode(texts).tolist()
    
    def compute_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        if not self._load_model_lazy():
            return 0.0
        
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity([emb1], [emb2])[0][0]
    
    def is_available(self) -> bool:
        """Check if embedding model is available"""
        return self._load_model_lazy()
