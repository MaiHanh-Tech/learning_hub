def _init_features(self) -> Dict[str, Any]:
    common_kwargs = {
        "ai_engine": self.ai,
        "i18n": self.i18n,
        "config": self.config
    }
    
    features = {}
    
    features["rag"] = RagFeature(
        **common_kwargs,
        embedding_engine=self.embedding_engine,
        kg_engine=self.kg_engine
    )
    
    features["translation"] = TranslationFeature(**common_kwargs)
    features["debate"] = DebateFeature(**common_kwargs)
    
    return features
