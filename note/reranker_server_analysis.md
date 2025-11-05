# Reranker Server 实现分析

## 概述

本文档分析了基于 Qwen3-Reranker-4B 模型的 reranker web 服务实现，以及相应的测试脚本修改。

## Server 实现分析

### 核心组件

1. **模型初始化** (`initialize_model` 函数)
   - 使用 `modelscope` 库加载 Qwen3-Reranker-4B 模型
   - 设置 tokenizer 和特殊 token ID（yes/no）
   - 定义前缀和后缀 tokens 用于格式化输入

2. **输入格式化** (`format_instruction` 函数)
   - 将指令、查询和文档格式化为特定模板
   - 默认指令："Given a web search query, retrieve relevant passages that answer the query"

3. **Tokenization 处理** (`process_inputs` 函数)
   - 使用 tokenizer 对输入进行编码
   - 添加前缀和后缀 tokens
   - 处理 padding 和截断

4. **相关性计算** (`compute_logits` 函数)
   - 计算模型输出的 logits
   - 提取 yes/no token 的分数
   - 使用 softmax 计算相关性概率

### API 设计

- **Reranker 端点**: `POST /v1/reranker`
  - 请求格式：`{"query": "查询文本", "documents": ["文档1", "文档2", ...], "instruction": "可选指令"}`
  - 返回格式：`{"scores": [得分1, 得分2, ...], "status": "success"}`

- **健康检查**: `GET /v1/health`
  - 返回服务状态和模型加载状态

## 测试脚本修改

### 主要变更

1. **移除 embedding 计算**
   - 原测试使用 embedding 相似度计算
   - 新版本直接调用 reranker API

2. **API 调用适配**
   - 请求格式改为符合 server API
   - 处理返回的 scores 数组

3. **新增功能**
   - 健康检查功能 (`check_server_health`)
   - 自定义指令支持
   - 错误处理和降级策略

### 测试用例

1. **基础 reranking 测试**
   - 测试人工智能相关文档的排序
   - 验证相关性分数计算

2. **多查询测试**
   - 针对不同查询测试同一文档集合
   - 验证排序结果的合理性

3. **自定义指令测试**
   - 测试自定义指令对排序结果的影响
   - 验证指令参数的正确传递

## 技术要点

### 模型工作原理

Qwen3-Reranker-4B 是一个基于语言模型的 reranker，它通过以下方式工作：

1. **输入格式化**: 将查询和文档组合成特定格式
2. **二分类判断**: 模型判断文档是否与查询相关
3. **概率计算**: 通过 softmax 计算相关性概率

### 性能考虑

- **批处理**: server 支持批量处理文档
- **GPU 优化**: 使用 PyTorch 的 GPU 加速
- **内存管理**: 处理长文本的截断策略

## 使用说明

### 启动服务

```bash
python reranker_server.py
```

### 运行测试

```bash
python test_reranker.py
```

### API 调用示例

```python
import requests

url = "http://localhost:11435/v1/reranker"
data = {
    "query": "人工智能",
    "documents": ["文档1", "文档2", "文档3"],
    "instruction": "自定义指令"
}

response = requests.post(url, json=data)
print(response.json())
```

## 总结

这个 reranker 实现提供了一个高效的文档排序服务，特别适用于 RAG 系统。通过直接使用语言模型进行相关性判断，相比传统的 embedding 相似度计算，能够提供更准确的相关性评估。