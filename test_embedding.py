"""
Working embedding test for Ollama with qwen3-embedding:4b model

This script demonstrates how to use embedding models with Ollama.
The OpenAI client library has compatibility issues with Ollama's embedding endpoint,
so we use direct HTTP requests instead.
"""

import requests
import json

def test_embedding(text, model="qwen3-embedding:4b"):
    """Test embedding generation with Ollama"""
    url = "http://localhost:11434/v1/embeddings"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "input": text,
        "encoding_format": "float"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        embedding = result['data'][0]['embedding']
        print(f"✓ Success: '{text}'")
        print(f"  Dimensions: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Last 5 values: {embedding[-5:]}")
        return embedding
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

if __name__ == "__main__":
    print("Testing Ollama Embedding Model: qwen3-embedding:4b")
    print("=" * 50)

    # Test with different texts
    test_texts = [
        "你好",
        "Hello world",
        "This is a test sentence for embedding generation",
        "人工智能和机器学习"
    ]

    embeddings = []
    for text in test_texts:
        embedding = test_embedding(text)
        if embedding:
            embeddings.append(embedding)
        print()

    print(f"Generated {len(embeddings)} embeddings successfully!")