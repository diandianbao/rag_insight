# Ollama集成错误分析和解决方案

## 问题描述

运行 `memory.py` 时出现错误，Agent无法正常响应，最终状态为空 `{}`，并抛出异常。

## 错误分析

### 主要错误信息
```
Exception in thread Thread-1 (_asyncio_thread_main):
...
File "/Users/looboo/miniconda3/envs/py313/lib/python3.13/site-packages/litellm/litellm_core_utils/get_llm_provider_logic.py", line 398, in get_llm_provider
    raise litellm.exceptions.BadRequestError(
```

### 问题根源
1. **LiteLLM无法识别模型提供者**：LiteLLM无法自动识别 `qwen3-coder:30b` 模型应该使用哪个提供者
2. **缺少明确配置**：没有明确指定使用Ollama作为模型提供者
3. **API基础URL配置不当**：通过环境变量设置可能没有被正确识别

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
           api_base="http://localhost:11434/v1",
           custom_llm_provider="ollama"
       ),
       instruction="Generate a short, friendly greeting.",
       output_key="last_greeting",
    )
```

### 关键修改点

1. **明确指定提供者**：添加 `custom_llm_provider="ollama"` 参数
2. **直接配置API基础URL**：在LiteLlm构造函数中直接设置 `api_base="http://localhost:11434/v1"`
3. **移除环境变量设置**：不再使用 `os.environ['OPENAI_API_BASE']`

## 验证步骤

### 1. 检查Ollama服务状态
```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 检查模型是否可用
ollama list
```

### 2. 测试模型响应
```bash
# 直接测试模型
ollama run qwen3-coder:30b "Hello, how are you?"
```

### 3. 运行修改后的代码
```bash
python memory.py
```

## 预期结果

- Agent应该能够正常响应
- 最终状态应该包含 `last_greeting` 键值对
- 不再出现线程异常

## 可能的后续问题

### 1. 模型响应格式
- 确保Qwen3-coder:30b模型的输出格式与ADK期望的格式兼容
- 可能需要调整instruction或prompt格式

### 2. 性能问题
- 本地模型可能响应较慢
- 考虑添加超时设置

### 3. 内存使用
- 30B模型需要较多内存
- 监控系统资源使用情况

## 调试技巧

### 1. 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 检查LiteLLM配置
```python
# 测试LiteLLM连接
from litellm import completion
response = completion(
    model="ollama/qwen3-coder:30b",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="http://localhost:11434/v1"
)
print(response)
```

### 3. 验证模型能力
- 确保模型能够理解并执行给定的instruction
- 测试不同的输入和期望输出