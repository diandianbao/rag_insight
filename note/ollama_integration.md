# Google ADK 集成本地Ollama模型

## 修改说明

### 原始代码
```python
from google.adk.agents import LlmAgent
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

greeting_agent = LlmAgent(
   name="Greeter",
   model="gemini-2.0-flash",
   instruction="Generate a short, friendly greeting.",
   output_key="last_greeting"
)
```

### 修改后代码
```python
from google.adk.agents import LlmAgent
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part

# 配置使用本地Ollama提供的Qwen3-coder:30b模型
# 注意：需要确保Ollama服务正在运行，并且已安装qwen3-coder:30b模型

greeting_agent = LlmAgent(
   name="Greeter",
   model="qwen3-coder:30b",  # 使用本地Ollama模型
   instruction="Generate a short, friendly greeting.",
   output_key="last_greeting",
   # 可能需要额外的配置来指定Ollama服务地址
   # base_url="http://localhost:11434"  # 如果ADK支持自定义base_url
)
```

## 主要修改点

1. **模型名称变更**
   - 从 `"gemini-2.0-flash"` 改为 `"qwen3-coder:30b"`
   - 使用本地Ollama服务提供的模型

2. **添加配置说明**
   - 添加了关于Ollama服务运行的注意事项
   - 预留了自定义base_url的配置选项

## 前置条件

### 1. 安装和启动Ollama
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve
```

### 2. 下载Qwen3-coder:30b模型
```bash
# 下载模型
ollama pull qwen3-coder:30b

# 验证模型是否可用
ollama list
```

### 3. 验证Ollama服务
```bash
# 检查服务状态
curl http://localhost:11434/api/tags
```

## 可能遇到的问题

### 1. 模型名称识别
- Google ADK可能无法直接识别Ollama模型名称
- 可能需要额外的配置或适配器

### 2. 服务地址配置
- 如果ADK不支持直接配置base_url，可能需要修改ADK的底层配置
- 可能需要使用Ollama的API兼容层

### 3. 模型兼容性
- 确保Qwen3-coder:30b模型的输入输出格式与ADK兼容
- 可能需要调整prompt格式

## 后续步骤

1. **测试连接**
   - 运行修改后的代码
   - 检查是否能成功连接到本地Ollama服务

2. **功能验证**
   - 测试Agent是否能正常生成问候语
   - 验证模型的响应质量

3. **性能优化**
   - 根据实际使用情况调整模型参数
   - 优化响应时间和资源使用

## 注意事项

- 确保Ollama服务在运行状态
- 本地模型可能需要更多内存和计算资源
- 考虑网络延迟和模型加载时间
- 定期更新模型以获得更好的性能