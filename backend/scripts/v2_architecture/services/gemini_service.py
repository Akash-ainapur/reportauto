"""
Gemini AI Service for Content Generation

This module provides a centralized service for interacting with Google's Gemini API
to generate AI-powered content for report sections.
"""

import os
import time
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables from .env file in project root
# Find the project root (4 levels up from this file: services -> v2_architecture -> scripts -> backend -> project_root)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)


class RateLimited(Exception):
    """HTTP 429 with the number of seconds the provider asked us to wait."""

    def __init__(self, wait, detail=""):
        super().__init__(detail)
        self.wait = wait


class GeminiService:
    """
    Singleton service for Gemini API interactions.
    Handles content generation with error handling, fallback mechanisms, and caching.
    """
    
    _instance = None
    _initialized = False

    CHAT_ENDPOINTS = {
        'openrouter': "https://openrouter.ai/api/v1/chat/completions",
        'groq': "https://api.groq.com/openai/v1/chat/completions",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Gemini service. Runs only once due to singleton pattern."""
        if not GeminiService._initialized:
            # AI_PROVIDER picks the service: gemini (default), openrouter or groq.
            # OpenRouter and Groq both speak the OpenAI chat-completions API (see CHAT_ENDPOINTS).
            self.provider = os.getenv('AI_PROVIDER', 'gemini').strip().lower()
            if self.provider == 'openrouter':
                self.api_key = os.getenv('OPENROUTER_API_KEY')
                self.model_name = os.getenv('OPENROUTER_MODEL', 'google/gemma-4-31b-it:free,nvidia/nemotron-3-ultra-550b-a55b:free')
            elif self.provider == 'groq':
                self.api_key = os.getenv('GROQ_API_KEY')
                self.model_name = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')
            else:
                self.api_key = os.getenv('GEMINI_API_KEY')
                self.model_name = 'gemini-flash-lite-latest'
            self.model = None
            self.is_configured = False
            self.cache_file = project_root / 'backend' / 'data' / 'ai_cache.json'
            self.cache = self._load_cache()
            self._configure()
            GeminiService._initialized = True
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cached AI responses from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    print(f"📦 Loaded {len(cache_data)} cached AI responses")
                    return cache_data
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def _get_cache_key(self, prompt: str, system_instruction: str, temperature: float) -> str:
        """Generate a unique cache key based on prompt parameters."""
        cache_data = f"{prompt}|{system_instruction}|{temperature}"
        # Keep other providers' answers apart from cached Gemini ones (Gemini keys unchanged)
        if self.provider != 'gemini':
            cache_data = f"{self.provider}:{self.model_name}|{cache_data}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _configure(self):
        """Configure the Gemini API client."""
        if self.provider in self.CHAT_ENDPOINTS:
            self.is_configured = bool(self.api_key)
            if self.is_configured:
                print(f"✅ {self.provider} configured (model: {self.model_name})")
            else:
                print(f"⚠️  {self.provider.upper()}_API_KEY not found in environment variables.")
                print("   AI content generation will use fallback placeholders.")
            return

        if not self.api_key:
            print("⚠️  GEMINI_API_KEY not found in environment variables.")
            print("   AI content generation will use fallback placeholders.")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.is_configured = True
            print("✅ Gemini API configured successfully")
        except Exception as e:
            print(f"⚠️  Failed to configure Gemini API: {str(e)}")
            print("   AI content generation will use fallback placeholders.")
    
    def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 4,
        use_cache: bool = True
    ) -> str:
        """
        Generate content using Gemini API with caching support.
        
        Args:
            prompt: The user prompt for content generation
            system_instruction: System-level instructions for the model
            temperature: Creativity parameter (0.0 - 1.0)
            max_retries: Number of retry attempts on failure
            use_cache: Whether to use cached responses (default: True)
            
        Returns:
            Generated text content or fallback placeholder
        """
        # Check cache first (if enabled)
        if use_cache:
            cache_key = self._get_cache_key(prompt, system_instruction or "", temperature)
            if cache_key in self.cache:
                print("♻️  Using cached AI response")
                return self.cache[cache_key]
        
        if not self.is_configured:
            return self._get_fallback_content(prompt)
        
        for attempt in range(max_retries):
            try:
                if self.provider in self.CHAT_ENDPOINTS:
                    print(f"🤖 Generating AI content via {self.provider} ({self.model_name})...")
                    content = self._chat_completion(prompt, system_instruction, temperature)
                    if use_cache:
                        cache_key = self._get_cache_key(prompt, system_instruction or "", temperature)
                        self.cache[cache_key] = content
                        self._save_cache()
                        print("💾 Cached AI response for future use")
                    # Free OpenRouter models allow ~20 requests/minute
                    if self.provider == 'openrouter':
                        time.sleep(3)
                    return content

                import google.generativeai as genai
                # Create model with system instruction if provided
                if system_instruction:
                    try:
                        model = genai.GenerativeModel(
                            self.model_name,
                            system_instruction=system_instruction
                        )
                    except TypeError:
                        # Fallback for older versions of google-generativeai
                        model = self.model
                        prompt = f"System Instructions:\n{system_instruction}\n\nTask:\n{prompt}"
                else:
                    model = self.model
                
                import google.generativeai as genai
                # Configure generation parameters
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                )
                
                # Generate content
                print("🤖 Generating AI content...")
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                content = response.text
                
                # Save to cache
                if use_cache:
                    cache_key = self._get_cache_key(prompt, system_instruction or "", temperature)
                    self.cache[cache_key] = content
                    self._save_cache()
                    print("💾 Cached AI response for future use")
                
                # Rate Limiting: Sleep to prevent hitting RPM limits
                # Reduced from 5s to 1s as we only make 2 requests now
                print("⏳ Rate Limiting: Waiting 1s...")
                time.sleep(1)
                
                return content
                
            except RateLimited as e:
                # The provider says how long to wait (Groq's free tier caps tokens per minute)
                print(f"⏳ Rate limited, waiting {e.wait:.0f}s (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(e.wait)
                else:
                    print("   Using fallback content.")
                    return self._get_fallback_content(prompt)
            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print("   Using fallback content.")
                    return self._get_fallback_content(prompt)
        
        return self._get_fallback_content(prompt)
    
    def generate_bulk_content(
        self,
        prompt: str,
        temperature: float = 0.5,
        use_cache: bool = True
    ) -> str:
        """
        Generate content for multiple sections in one request.
        Uses a lower temperature for more predictable formatting.
        """
        # Bulk generation is inherently more complex, so we use a lower temperature
        return self.generate_content(
            prompt=prompt,
            system_instruction="You are a meticulous technical writer who follows tagging instructions perfectly.",
            temperature=temperature,
            use_cache=use_cache
        )

    def _chat_completion(self, prompt: str, system_instruction: Optional[str], temperature: float) -> str:
        """One chat completion through an OpenAI-compatible API (OpenRouter, Groq); stdlib only."""
        import urllib.request
        import urllib.error

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        # OPENROUTER_MODEL may list fallbacks ("a:free,b:free"); OpenRouter tries them in order,
        # which rides out the frequent upstream rate limits on free models
        models = [m.strip() for m in self.model_name.split(",") if m.strip()]
        request_body = {"model": models[0], "messages": messages, "temperature": temperature}
        if len(models) > 1 and self.provider == 'openrouter':
            request_body["models"] = models
        if self.provider == 'groq' and models[0].startswith('openai/gpt-oss'):
            # Report prose needs little reasoning; hidden thinking tokens count against the per-minute cap
            request_body["reasoning_effort"] = "low"
        body = json.dumps(request_body).encode("utf-8")
        request = urllib.request.Request(
            self.CHAT_ENDPOINTS[self.provider],
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-OpenRouter-Title": "Automated Report Generator",
                # Groq's edge rejects urllib's default user agent
                "User-Agent": "AutomatedReportGenerator/1.0",
            },
        )
        try:
            # Long chapter batches can take a few minutes on free models
            with urllib.request.urlopen(request, timeout=600) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:300]
            if e.code == 429:
                try:
                    wait = float(e.headers.get('retry-after') or 20)
                except ValueError:
                    wait = 20
                raise RateLimited(min(max(wait, 1), 65), detail)
            raise RuntimeError(f"{self.provider} HTTP {e.code}: {detail}")

        if payload.get("error"):
            raise RuntimeError(f"{self.provider} error: {payload['error']}")
        content = payload["choices"][0]["message"].get("content") or ""
        if not content.strip():
            raise RuntimeError(f"{self.provider} returned an empty response")
        print(f"   answered by: {payload.get('model', models[0])}")
        return content

    def _get_fallback_content(self, prompt: str) -> str:
        """
        Generate fallback placeholder content when AI service is unavailable.
        
        Args:
            prompt: Original prompt (used to determine section type)
            
        Returns:
            Placeholder text
        """
        # Students read this in their report, so it says what to do rather than how to configure the server
        return (
            "[Write this section yourself]\n\n"
            "The AI service was busy when this report was generated, so this section could not be "
            "written automatically. Write it here in your own words, or generate the report again later."
        )
    
    def is_available(self) -> bool:
        """Check if the Gemini service is properly configured and available."""
        return self.is_configured
