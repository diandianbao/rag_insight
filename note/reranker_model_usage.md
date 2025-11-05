# Reranker 模型使用指南

## 问题描述
当前 `test_reranker.py` 使用 `dengcao/Qwen3-Reranker-8B:F16` 模型尝试调用 `/v1/embeddings` 接口，但该模型不支持嵌入生成，导致 500 错误：

```
"this model does not support embeddings"
```

## 根本原因
`dengcao/Qwen3-Reranker-8B:F16` 是一个 **reranker 模型**，不是嵌入模型。它不能输出向量，而是接收 **查询-文档对**，输出相关性分数。

## 正确使用方式
1. 使用 `/v1/rerank` 接口，而非 `/v1/embeddings`
2. 传入参数：`query` + `texts`（文档列表）
3. 模型直接返回排序后的相关性分数

## 修复方案
1. 安装支持 rerank 的模型：
   ```bash
   ollama pull qwen2-reranker
   ```
2. 修改代码：移除 `get_embedding` 和 `cosine_similarity`，改用 `rerank` 接口
3. 更新模型名称为 `"qwen2-reranker"`

## 推荐架构
```
[查询] → 嵌入模型（召回 top 50） → Reranker（精排 top 5） → 返回结果
```

## 参考模型
- 嵌入模型：`nomic-embed-text`, `bge-large-zh`
- Reranker 模型：`qwen2-reranker`, `bge-reranker-base`

> ✅ 建议：在生产系统中，先用嵌入模型做粗筛，再用 reranker 做精排，以平衡效率与精度。
