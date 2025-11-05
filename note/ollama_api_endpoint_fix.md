# Ollama API端点错误分析和解决方案

## 问题描述

运行 `memory.py` 时出现404错误，LiteLLM尝试访问错误的API端点。

## 错误分析

### 主要错误信息
```
httpx.HTTPStatusError: Client error '404 Not Found' for url 'http://localhost:11434/v1/api/generate'
```

### 问题根源
1. **错误的API基础URL**：使用了 `http://localhost:11434/v1` 而不是 `http://localhost:11434`
2. **API端点不匹配**：Ollama的API端点是 `/api/generate`，但LiteLLM尝试访问 `/v1/api/generate`
3. **路径拼接错误**：LiteLLM在基础URL后自动添加了 `/v1/` 前缀

## 解决方案

### 修改后的代码
```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

async def main():
    # 使用LiteLlm正确配置Ollama模型
    greeting_agent = LlmAgent(
       name="Greeter",
       model=LiteLlm(
           model="qwen3-coder:30b",
           api_base="http://localhost:11434",  # 修正API基础URL
           custom_llm_provider="ollama"
       ),
       instruction="Generate a short, friendly greeting.",
       output_key="last_greeting",
    )
```

### 关键修改点

1. **修正API基础URL**：从 `http://localhost:11434/v1` 改为 `http://localhost:11434`
2. **保持提供者配置**：继续使用 `custom_llm_provider="ollama"`

## Ollama API端点说明

### 正确的API端点结构
- **基础URL**: `http://localhost:11434`
- **生成端点**: `/api/generate`
- **完整URL**: `http://localhost:11434/api/generate`

### 错误的API端点结构
- **基础URL**: `http://localhost:11434/v1`
- **生成端点**: `/api/generate`
- **完整URL**: `http://localhost:11434/v1/api/generate` (404错误)

## 验证步骤

### 1. 检查Ollama服务状态
```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 检查模型是否可用
ollama list
```

### 2. 测试API端点
```bash
# 测试正确的API端点
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder:30b",
    "prompt": "Hello, how are you?",
    "stream": false
  }'
```

### 3. 运行修改后的代码
```bash
python memory.py
```

## 预期结果

- Agent应该能够正常连接到Ollama服务
- 不再出现404错误
- Agent应该能够生成问候语并更新状态

## 调试技巧

### 1. 启用LiteLLM调试模式
```python
import litellm
litellm._turn_on_debug()
```

### 2. 手动测试LiteLLM连接
```python
import asyncio
from litellm import acompletion

async def test_ollama():
    try:
        response = await acompletion(
            model="ollama/qwen3-coder:30b",
            messages=[{"role": "user", "content": "Hello"}],
            api_base="http://localhost:11434"
        )
        print("Success:", response)
    except Exception as e:
        print("Error:", e)

asyncio.run(test_ollama())
```

### 3. 检查网络连接
```python
import httpx

async def test_connection():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:11434/api/tags")
        print("Ollama status:", response.status_code)
        print("Response:", response.text)

asyncio.run(test_connection())
```

## 常见问题排查

### 1. 服务未启动
```bash
# 启动Ollama服务
ollama serve
```

### 2. 模型未下载
```bash
# 下载模型
ollama pull qwen3-coder:30b
```

### 3. 端口被占用
```bash
# 检查端口使用情况
lsof -i :11434
```

### 4. 防火墙阻止
- 确保本地连接没有被防火墙阻止
- 检查Ollama服务是否绑定到正确的接口