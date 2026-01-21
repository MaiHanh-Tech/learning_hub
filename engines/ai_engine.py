"""
META-BLOCK: AI Engine 
Priority: OpenRouter (Gemini free model) > DeepSeek
"""

from typing import Optional, Callable
import streamlit as st
import time
from dataclasses import dataclass
from enum import Enum


class AIProvider(Enum):
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"


@dataclass
class AIResponse:
    """Standardized AI response"""
    success: bool
    content: str
    provider: str
    latency: float
    tokens: int = 0
    error: Optional[str] = None


class CircuitBreaker:
    """Circuit Breaker Pattern"""
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.provider_status = {
            provider.value: {"failures": 0, "last_failure": None}
            for provider in AIProvider
        }
    
    def is_available(self, provider: str) -> bool:
        status = self.provider_status.get(provider, {})
        
        if status.get("last_failure"):
            elapsed = time.time() - status["last_failure"]
            if elapsed > self.timeout:
                status["failures"] = 0
                status["last_failure"] = None
                return True
        
        return status.get("failures", 0) < self.failure_threshold
    
    def record_failure(self, provider: str):
        if provider in self.provider_status:
            self.provider_status[provider]["failures"] += 1
            self.provider_status[provider]["last_failure"] = time.time()
    
    def record_success(self, provider: str):
        if provider in self.provider_status:
            self.provider_status[provider]["failures"] = 0
            self.provider_status[provider]["last_failure"] = None


class AIEngine:
    def __init__(self, default_model: str = "google/gemini-2.0-flash-exp:free", config=None):
        self.default_model = default_model
        self.config = config or {}
        self.circuit_breaker = CircuitBreaker()
        self.providers = self._init_providers()
    
    def _init_providers(self) -> dict:
        providers = {}
        
        # OpenRouter
        try:
            if "openrouter" in st.secrets and "api_key" in st.secrets["openrouter"]:
                from openai import OpenAI
                providers[AIProvider.OPENROUTER.value] = OpenAI(
                    api_key=st.secrets["openrouter"]["api_key"],
                    base_url="https://openrouter.ai/api/v1",
                    timeout=60  # tăng timeout vì free model đôi khi chậm
                )
        except Exception:
            pass
        
        # DeepSeek (fallback)
        try:
            if "deepseek" in st.secrets and "api_key" in st.secrets["deepseek"]:
                from openai import OpenAI
                providers[AIProvider.DEEPSEEK.value] = OpenAI(
                    api_key=st.secrets["deepseek"]["api_key"],
                    base_url="https://api.deepseek.com/v1",
                    timeout=30
                )
        except Exception:
            pass
        
        return providers
    
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_type: str = "flash",  # không còn pro/flash riêng, giờ dùng model name trực tiếp
        max_tokens: int = 4000,
        temperature: float = 0.7,
        progress_callback: Optional[Callable] = None
    ) -> AIResponse:
        """
        Generate AI response với priority: OpenRouter (Gemini free) → DeepSeek
        """
        
        provider_order = [
            AIProvider.OPENROUTER.value,
            AIProvider.DEEPSEEK.value
        ]
        
        last_error = None
        
        for provider in provider_order:
            if provider not in self.providers:
                continue
            
            if not self.circuit_breaker.is_available(provider):
                continue
            
            if progress_callback:
                progress_callback(f"🤖 Calling {provider.upper()}...")
            
            start_time = time.time()
            
            try:
                content = None
                
                if provider == AIProvider.OPENROUTER.value:
                    content = self._call_openrouter(prompt, system_instruction, max_tokens, temperature)
                
                elif provider == AIProvider.DEEPSEEK.value:
                    content = self._call_deepseek(prompt, system_instruction, max_tokens, temperature)
                
                if content:
                    latency = time.time() - start_time
                    self.circuit_breaker.record_success(provider)
                    
                    return AIResponse(
                        success=True,
                        content=content,
                        provider=provider,
                        latency=latency
                    )
            
            except Exception as e:
                last_error = str(e)
                self.circuit_breaker.record_failure(provider)
                continue
        
        error_msg = "⚠️ Tất cả AI providers không khả dụng."
        if last_error:
            error_msg += f"\nLỗi cuối: {last_error}"
        
        return AIResponse(
            success=False,
            content="",
            provider="none",
            latency=0,
            error=error_msg
        )
    
    def _call_openrouter(
        self,
        prompt: str,
        system_instruction: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call OpenRouter API với Gemini free model"""
        client = self.providers[AIProvider.OPENROUTER.value]
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",  # Gemini free variant (cập nhật nếu deprecate)
            # Nếu muốn thử model free khác: "mistralai/devstral-2512:free" hoặc "xiaomi/mimo-v2-flash:free"
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_headers={
                "HTTP-Referer": "https://your-app-url.com",  # optional, để OpenRouter track
                "X-Title": "Streamlit AI Engine"
            }
        )
        
        return response.choices[0].message.content.strip()
    
    def _call_deepseek(
        self,
        prompt: str,
        system_instruction: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call DeepSeek API (fallback)"""
        client = self.providers[AIProvider.DEEPSEEK.value]
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
