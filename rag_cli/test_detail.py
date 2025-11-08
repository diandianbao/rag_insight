#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 detail 命令功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from models.config import SessionConfig
from core.session import InteractiveSession
import yaml

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config_data = yaml.safe_load(f)

config = SessionConfig.from_dict(config_data)
session = InteractiveSession(config)

# 连接数据库
if not session.connect():
    print("❌ 无法连接到数据库")
    sys.exit(1)

# 执行搜索
print("执行搜索: '记忆管理'")
success = session.process_query("记忆管理")

if success and session.current_results:
    print(f"✓ 搜索成功，找到 {len(session.current_results)} 个结果")

    # 测试 detail 命令
    print("\n测试 detail 命令:")

    # 查看第一个文档
    print("\n1. 查看排名第1的文档:")
    session.display.show_document_detail_by_index(0, session.current_results)

    # 查看第三个文档
    print("\n2. 查看排名第3的文档:")
    session.display.show_document_detail_by_index(2, session.current_results)

else:
    print("❌ 搜索失败")

# 清理资源
session.cleanup()