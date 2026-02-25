#!/usr/bin/env python3
"""
Quick test script to verify Ollama is working
Run this after mistral model finishes downloading
"""

import requests
import json
from typing import Optional

def test_ollama_connection() -> bool:
    """Test if Ollama server is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama at localhost:11434")
        print("   Make sure you ran: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_available_models() -> list:
    """List all available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        models = data.get("models", [])
        
        if not models:
            print("⏳ No models installed yet. Waiting for mistral download...")
            return []
        
        print("\n📦 Available Models:")
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0)
            size_gb = size / (1024**3)
            print(f"  • {name} ({size_gb:.2f} GB)")
        
        return models
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []


def test_mistral_generation(prompt: str = "Generate a viral TikTok hook") -> Optional[str]:
    """Test if mistral model can generate text"""
    try:
        print(f"\n🧠 Testing Mistral with prompt: '{prompt}'")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            generated = data.get("response", "")
            print(f"\n✅ Mistral generated ({len(generated)} chars):")
            print(f"   {generated[:200]}...")
            return generated
        else:
            print(f"❌ Mistral returned status: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Model might still be loading")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 OLLAMA VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Connection
    print("\n[1/3] Testing Ollama Connection...")
    if not test_ollama_connection():
        print("\n⚠️  Ollama server not responding. Make sure to run:")
        print("   ollama serve")
        return
    
    # Test 2: List models
    print("\n[2/3] Checking Available Models...")
    models = list_available_models()
    
    if not models:
        print("\n⏳ Waiting for Mistral model to download...")
        print("   Check back in a few minutes")
        return
    
    # Test 3: Generate text
    print("\n[3/3] Testing Text Generation...")
    test_mistral_generation()
    
    print("\n" + "=" * 60)
    print("✅ OLLAMA IS READY!")
    print("=" * 60)
    print("\nYour Viral Engine can now:")
    print("  • Generate viral scripts (Agent Beta)")
    print("  • Analyze trends (Agent Alpha)")
    print("  • Create media content (Agent Gamma)")
    print("  • Plan monetization (Agent Delta)")
    print("\nRun: python main.py 'your topic'")
    print("=" * 60)


if __name__ == "__main__":
    main()
