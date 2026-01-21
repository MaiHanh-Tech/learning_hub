"""
META-BLOCK: AI Engine
Nguyên tắc: Circuit Breaker + Fallback Chain
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
    """
    Circuit Breaker Pattern implementation
    
    Nguyên tắc (từ *Antifragile*):
    - Không retry provider đã "chết" → Tránh lãng phí thời gian
    - Tự động recovery sau timeout → Self-healing
    """
    
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
        """Record a success (reset counter)"""
        if provider in self.provider_status:
            self.provider_status[provider]["failures"] = 0
            self.provider_status[provider]["last_failure"] = None

class AIEngine:
    def __init__(self, default_model: str = "gemini-pro", config=None):
        self.default_model = default_model
        self.config = config or {} 
        
        
        self.circuit_breaker = CircuitBreaker()
        self.providers = self._init_providers()
        
        
        # Status display
        self._show_status()
    
    def _init_providers(self) -> dict:
        providers = {}
    
        st.caption("--- AI Providers Debug Start ---")
    
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
                st.caption("Gemini: READY ✅")
            else:
                st.caption("Gemini: MISSING KEY ❌")
        except Exception as e:
            st.caption(f"Gemini: ERROR - {str(e)}")
    
        # DeepSeek
        try:
            if "deepseek" in st.secrets and "api_key" in st.secrets["deepseek"]:
                from openai import OpenAI
                providers[AIProvider.DEEPSEEK.value] = OpenAI(
                    api_key=st.secrets["deepseek"]["api_key"],
                    base_url="https://api.deepseek.com/v1",
                    timeout=30
                )
                st.caption("DeepSeek: READY ✅")
            else:
                st.caption("DeepSeek: MISSING KEY ❌")
        except Exception as e:
            st.caption(f"DeepSeek: ERROR - {str(e)}")
    
        # Grok
        try:
            if "xai" in st.secrets and "api_key" in st.secrets["xai"]:
                from openai import OpenAI
                providers[AIProvider.GROK.value] = OpenAI(
                    api_key=st.secrets["xai"]["api_key"],
                    base_url="https://api.x.ai/v1",
                    timeout=30
                )
                st.caption("Grok: READY ✅")
            else:
                st.caption("Grok: MISSING KEY ❌")
        except Exception as e:
            st.caption(f"Grok: ERROR - {str(e)}")
    
        st.caption("--- AI Providers Debug End ---")
    
        return providers
    
    def _show_status(self):
        """Show AI engine status"""
        status_icons = {
            AIProvider.GEMINI.value: "🟡",
            AIProvider.DEEPSEEK.value: "🟣",
            AIProvider.GROK.value: "🟢"
        }
        
        available = [
            f"{status_icons.get(p, '⚫')} {p.upper()}"
            for p in self.providers.keys()
        ]
        
        if available:
            st.caption(f"**AI Engine:** {' → '.join(available)}")
        else:
            st.error("🔴 No AI providers available")
    
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
        
        Args:
            prompt: User prompt
            system_instruction: System instruction
            model_type: "flash" hoặc "pro"
            max_tokens: Max output tokens
            temperature: Temperature (0-1)
            progress_callback: Function để update progress bar
        
        Returns:
            AIResponse object
        """
        
        # Priority order: Gemini → DeepSeek → Grok
        provider_order = [
            AIProvider.GEMINI.value,
            AIProvider.DEEPSEEK.value,
            AIProvider.GROK.value
        ]
        
        for provider in provider_order:
            # Skip if not available or circuit broken
            if provider not in self.providers:
                continue
            
            if not self.circuit_breaker.is_available(provider):
                continue
            
            # Update progress
            if progress_callback:
                progress_callback(f"🤖 Calling {provider.upper()}...")
            
            # Try calling provider
            start_time = time.time()
            
            try:
                if provider == AIProvider.GEMINI.value:
                    content = self._call_gemini(prompt, system_instruction, model_type)
                
                elif provider == AIProvider.DEEPSEEK.value:
                    content = self._call_deepseek(prompt, system_instruction, max_tokens)
                
                elif provider == AIProvider.GROK.value:
                    content = self._call_grok(prompt, system_instruction, max_tokens)
                
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
                self.circuit_breaker.record_failure(provider)
                
                # Log error (optional)
                try:
                    from utils.logger import AppLogger
                    logger = AppLogger()
                    logger.log_error(f"AI_{provider}", str(e), "")
                except:
                    pass
                
                continue
        
        # All providers failed
        return AIResponse(
            success=False,
            content="",
            provider="none",
            latency=0,
            error="⚠️ Tất cả AI providers tạm thời không khả dụng. Thử lại sau!"
        )
    
    def _call_gemini(self, prompt: str, system_instruction: str, model_type: str) -> str:
        """Call Gemini API"""
        import google.generativeai as genai
        
        model_name = "gemini-2.5-flash" if model_type == "flash" else "gemini-2.5-pro"
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        
        raise Exception("Gemini returned empty response")
    
    def _call_deepseek(self, prompt: str, system_instruction: str, max_tokens: int) -> str:
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
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _call_grok(self, prompt: str, system_instruction: str, max_tokens: int) -> str:
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
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def analyze_document(text: str, instruction: str) -> str:
        """
        Static method cho RAG (có cache)
        
        [Inference] Dùng cache để tránh gọi API lại khi analyze cùng 1 doc
        """
        try:
            import google.generativeai as genai
            
            if "api_keys" in st.secrets and "gemini_api_key" in st.secrets["api_keys"]:
                genai.configure(api_key=st.secrets["api_keys"]["gemini_api_key"])
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                response = model.generate_content(f"{instruction}\n\n{text[:150000]}")
                
                if response and response.text:
                    return response.text.strip()
            
            return "❌ Gemini API không khả dụng"
        
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
