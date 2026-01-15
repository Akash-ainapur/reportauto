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


class GeminiService:
    """
    Singleton service for Gemini API interactions.
    Handles content generation with error handling, fallback mechanisms, and caching.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Gemini service. Runs only once due to singleton pattern."""
        if not GeminiService._initialized:
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
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _configure(self):
        """Configure the Gemini API client."""
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
        max_retries: int = 3,
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
                import google.generativeai as genai
                # Create model with system instruction if provided
                if system_instruction:
                    model = genai.GenerativeModel(
                        self.model_name,
                        system_instruction=system_instruction
                    )
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

    def _get_fallback_content(self, prompt: str) -> str:
        """
        Generate fallback placeholder content when AI service is unavailable.
        
        Args:
            prompt: Original prompt (used to determine section type)
            
        Returns:
            Placeholder text
        """
        return (
            "[AI-Generated Content Placeholder]\n\n"
            "This section will contain AI-generated content based on your project details. "
            "To enable automatic content generation, please configure your GEMINI_API_KEY "
            "environment variable.\n\n"
            "The content will be tailored to your project requirements and follow "
            "academic writing standards."
        )
    
    def is_available(self) -> bool:
        """Check if the Gemini service is properly configured and available."""
        return self.is_configured
