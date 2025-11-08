#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 detail 命令功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 直接测试 display 功能
from core.display import ResultDisplay
from models.config import DisplayConfig
from models.results import SearchResult

# 创建显示配置
display_config = DisplayConfig()
display = ResultDisplay(display_config)

# 创建测试数据
test_result = SearchResult(
    chunk_id="test-chunk-001",
    title="测试文档标题",
    content="这是一个测试文档的内容。这里包含了详细的文档信息，用于测试detail命令的功能。文档内容应该足够长，以便展示detail命令的显示效果。",
    source_file="/path/to/test/document.pdf",
    similarity_score=0.85,
    metadata={
        "chunk_index": 0,
        "page_number": 1,
        "document_type": "PDF"
    }
)

print("测试 detail 命令显示效果:")
print("=" * 50)
display.show_document_detail(test_result)