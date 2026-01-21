"""
META-BLOCK: AI Engine 
Priority: Gemini Pro > DeepSeek > Grok
"""

from typing import Optional, Callable
import streamlit as st
import time
from dataclasses import dataclass
from enum import Enum


class AIProvider(Enum):
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROK = "grok"


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
    def __init__(self, default_model: str = "gemini-pro", config=None):
        self.default_model = default_model
        self.config = config or {}
        self.circuit_breaker = CircuitBreaker()
        self.providers = self._init_providers()
    
    def _init_providers(self) -> dict:
        """Initialize AI providers"""
        providers = {}
        
        # Gemini
        try:
            gemini_key = None
            if "api_keys" in st.secrets and "gemini_api_key" in st.secrets["api_keys"]:
                gemini_key = st.secrets["api_keys"]["gemini_api_key"]
            elif "gemini_api_key" in st.secrets:
                gemini_key = st.secrets["gemini_api_key"]
            
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                providers[AIProvider.GEMINI.value] = "ready"
        except Exception as e:
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
        except Exception as e:
            pass
        
        # Grok
        try:
            if "xai" in st.secrets and "api_key" in st.secrets["xai"]:
                from openai import OpenAI
                providers[AIProvider.GROK.value] = OpenAI(
                    api_key=st.secrets["xai"]["api_key"],
                    base_url="https://api.x.ai/v1",
                    timeout=30
                )
        except Exception as e:
            pass
        
        return providers
    
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_type: str = "pro",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        progress_callback: Optional[Callable] = None
    ) -> AIResponse:
        """
        Generate AI response với auto fallback
        """
        
        # Priority order
        provider_order = [
            AIProvider.GEMINI.value,
            AIProvider.DEEPSEEK.value,
            AIProvider.GROK.value
        ]
        
        last_error = None
        
        for provider in provider_order:
            # Skip if not available
            if provider not in self.providers:
                continue
            
            if not self.circuit_breaker.is_available(provider):
                continue
            
            # Update progress
            if progress_callback:
                progress_callback(f"🤖 Calling {provider.upper()}...")
            
            start_time = time.time()
            
            try:
                content = None
                
                if provider == AIProvider.GEMINI.value:
                    content = self._call_gemini(prompt, system_instruction, model_type)
                
                elif provider == AIProvider.DEEPSEEK.value:
                    content = self._call_deepseek(prompt, system_instruction, max_tokens, temperature)
                
                elif provider == AIProvider.GROK.value:
                    content = self._call_grok(prompt, system_instruction, max_tokens, temperature)
                
                # Success
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
        
        # All providers failed
        error_msg = f"⚠️ Tất cả AI providers không khả dụng."
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
        """Call Gemini API"""
        import google.generativeai as genai
        
        # Use flash model (more stable)
        model_name = "gemini-2.0-flash-exp"
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        
        raise Exception("Gemini returned empty response")
    
    def _call_deepseek(
        self,
        prompt: str,
        system_instruction: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call DeepSeek API"""
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
    
    def _call_grok(
        self,
        prompt: str,
        system_instruction: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call Grok API"""
        client = self.providers[AIProvider.GROK.value]
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="grok-beta",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content.strip()
