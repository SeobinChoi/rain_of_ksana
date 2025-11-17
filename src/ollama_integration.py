#!/usr/bin/env python3
"""
Ollama Integration Module
Handles text summarization using Ollama LLM models.
"""

import requests
import time
from typing import List, Optional, Dict, Any


class OllamaIntegration:
    """Integrates Ollama for caption summarization"""

    def __init__(self, model: str = "llama3.2:3b",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 30,
                 prompt_template: Optional[str] = None):
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.prompt_template = prompt_template or (
            "Summarize the following scene descriptions into one coherent narrative sentence. "
            "Consider the time order and describe it like a story:\n\n{captions}"
        )
        self._available = None

    def check_ollama_available(self) -> bool:
        """Check if Ollama server is running and accessible"""
        if self._available is not None:
            return self._available

        try:
            response = requests.get(
                f"{self.base_url}/api/version",
                timeout=2
            )
            self._available = response.status_code == 200
            if self._available:
                version = response.json().get('version', 'unknown')
                print(f"✅ Ollama server connected (version: {version})")
            return self._available
        except requests.exceptions.RequestException:
            self._available = False
            print("⚠️  Ollama server not available")
            print(f"   Make sure Ollama is running at {self.base_url}")
            print("   Install: https://ollama.ai/download")
            return False

    def check_model_available(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code != 200:
                return False

            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]

            if self.model in model_names:
                print(f"✅ Model '{self.model}' is available")
                return True
            else:
                print(f"⚠️  Model '{self.model}' not found")
                print(f"   Available models: {', '.join(model_names)}")
                print(f"   To install: ollama pull {self.model}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking model: {e}")
            return False

    def summarize_captions(self, captions: List[str]) -> Optional[str]:
        """Summarize a list of captions into a single coherent text"""
        if not captions:
            return None

        if not self.check_ollama_available():
            return None

        # Format captions for the prompt
        captions_text = "\n".join(f"- {cap}" for cap in captions)
        prompt = self.prompt_template.format(captions=captions_text)

        try:
            print(f"🦙 Summarizing {len(captions)} captions with Ollama...")
            start_time = time.time()

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                print(f"❌ Ollama API error: {response.status_code}")
                return None

            result = response.json()
            summary = result.get('response', '').strip()

            elapsed = time.time() - start_time
            print(f"✅ Summary generated in {elapsed:.1f}s")

            return summary

        except requests.exceptions.Timeout:
            print(f"⏱️  Ollama request timed out after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

    def summarize_captions_streaming(self, captions: List[str],
                                     callback=None) -> Optional[str]:
        """Summarize captions with streaming response"""
        if not captions:
            return None

        if not self.check_ollama_available():
            return None

        captions_text = "\n".join(f"- {cap}" for cap in captions)
        prompt = self.prompt_template.format(captions=captions_text)

        try:
            print(f"🦙 Streaming summary of {len(captions)} captions...")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                },
                timeout=self.timeout,
                stream=True
            )

            if response.status_code != 200:
                print(f"❌ Ollama API error: {response.status_code}")
                return None

            full_response = ""
            for line in response.iter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        token = chunk['response']
                        full_response += token
                        if callback:
                            callback(token)

            return full_response.strip()

        except requests.exceptions.Timeout:
            print(f"⏱️  Ollama request timed out after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama request failed: {e}")
            return None

    def test_connection(self) -> bool:
        """Test Ollama connection and model availability"""
        print("\n" + "=" * 60)
        print("🦙 Ollama Connection Test")
        print("=" * 60)

        # Check server
        if not self.check_ollama_available():
            return False

        # Check model
        if not self.check_model_available():
            return False

        # Test generation
        print("\n🧪 Testing text generation...")
        test_captions = [
            "a person sitting at a desk",
            "a laptop computer on the table",
            "a coffee cup near the keyboard"
        ]

        result = self.summarize_captions(test_captions)

        if result:
            print(f"\n✅ Test successful!")
            print(f"Generated summary: {result}")
            return True
        else:
            print("\n❌ Test failed")
            return False

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get('models', [])
        except requests.exceptions.RequestException:
            pass
        return []

    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """Pull/download a model from Ollama"""
        model = model_name or self.model

        print(f"📥 Pulling model '{model}'...")
        print("This may take a while depending on model size...")

        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True,
                timeout=600  # 10 minutes for download
            )

            if response.status_code != 200:
                print(f"❌ Failed to pull model: {response.status_code}")
                return False

            # Stream progress
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    status = data.get('status', '')
                    if status:
                        print(f"  {status}")

            print(f"✅ Model '{model}' pulled successfully")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ Error pulling model: {e}")
            return False


# Utility function for easy usage
def create_ollama_from_config(config: Dict[str, Any]) -> Optional[OllamaIntegration]:
    """Create OllamaIntegration instance from config dictionary"""
    if not config.get("ollama", {}).get("enabled", False):
        return None

    ollama_config = config.get("ollama", {})

    integration = OllamaIntegration(
        model=ollama_config.get("model", "llama3.2:3b"),
        base_url=ollama_config.get("base_url", "http://localhost:11434"),
        timeout=ollama_config.get("timeout", 30),
        prompt_template=ollama_config.get("prompt_template")
    )

    # Test connection
    if integration.check_ollama_available():
        return integration
    else:
        print("⚠️  Ollama not available, text summarization disabled")
        return None


if __name__ == "__main__":
    # Test Ollama integration
    ollama = OllamaIntegration()
    ollama.test_connection()
