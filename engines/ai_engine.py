"""
META-BLOCK: AI Engine 
Priority: Gemini > DeepSeek 
"""

from typing import Optional, Callable
import streamlit as st
import time
from dataclasses import dataclass
from enum import Enum


class AIProvider(Enum):
    GEMINI = "gemini"
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
        """Check if provider is available"""
        status = self.provider_status.get(provider, {})
        
        # Reset if timeout passed
        if status.get("last_failure"):
            elapsed = time.time() - status["last_failure"]
            if elapsed > self.timeout:
                status["failures"] = 0
                status["last_failure"] = None
                return True
        
        return status.get("failures", 0) < self.failure_threshold
    
    def record_failure(self, provider: str):
        """Record a failure"""
        if provider in self.provider_status:
            self.provider_status[provider]["failures"] += 1
            self.provider_status[provider]["last_failure"] = time.time()
    
    def record_success(self, provider: str):
        """Record a success"""
        if provider in self.provider_status:
            self.provider_status[provider]["failures"] = 0
            self.provider_status[provider]["last_failure"] = None


class AIEngine:
    def __init__(self, default_model: str = "gemini-2.5-flash", config=None):
        self.default_model = default_model
        self.config = config or {}
        self.circuit_breaker = CircuitBreaker()
        self.providers = self._init_providers()
    
    def _init_providers(self) -> dict:
        """Initialize AI providers"""
        providers = {}
        
        # Gemini
        try:
            gemini_key = st.secrets.get("gemini_api_key")
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                providers[AIProvider.GEMINI.value] = "ready"
        except Exception:
            pass
        
        # DeepSeek
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
        model_type: str = "flash",  # "flash" or "pro"
        max_tokens: int = 4000,
        temperature: float = 0.7,
        progress_callback: Optional[Callable] = None
    ) -> AIResponse:
        """
        Generate AI response với auto fallback: Gemini free > DeepSeek
        """
        
        provider_order = [
            AIProvider.GEMINI.value,
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
                
                if provider == AIProvider.GEMINI.value:
                    content = self._call_gemini(prompt, system_instruction, model_type)
                
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
        
        # All failed
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
    
    def _call_gemini(self, prompt: str, system_instruction: Optional[str], model_type: str) -> str:
        """Call Gemini API - thử flash/pro, fallback nếu cần"""
        import google.generativeai as genai
        
        # Ưu tiên model dựa trên type
        model_name = "gemini-2.5-flash" if model_type.lower() == "flash" else "gemini-2.5-pro"
        
        # Fallback models nếu primary fail (thử pro nếu flash fail, hoặc ngược lại)
        fallback_models = [model_name]
        if model_type.lower() == "flash":
            fallback_models.append("gemini-2.5-pro")
        else:
            fallback_models.append("gemini-2.5-flash")
        
        fallback_models.append("gemini-2.0-flash")  # stable fallback
        
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        last_gemini_error = None
        
        for model_name in fallback_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(prompt)
                
                if response and response.text:
                    return response.text.strip()
            
            except Exception as e:
                last_gemini_error = str(e)
                continue
        
        raise Exception(f"Gemini failed all models. Last error: {last_gemini_error or 'Unknown'}")
    
    def _call_deepseek(
        self,
        prompt: str,
        system_instruction: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call DeepSeek API as fallback"""
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
