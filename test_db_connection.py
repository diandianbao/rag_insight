#!/usr/bin/env python3
"""
数据库连接测试脚本
"""

import os
import psycopg2

def test_database_connection():
    """测试数据库连接"""

    # 从环境变量获取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hello_vector")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    print("=== 数据库连接测试 ===")
    print(f"数据库URL: {database_url.replace(db_password, '***')}")

    try:
        # 测试连接
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # 执行简单查询
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        print(f"✓ 数据库连接成功")
        print(f"PostgreSQL版本: {version}")

        # 检查数据库是否存在
        cursor.execute("SELECT datname FROM pg_database WHERE datname = %s", (db_name,))
        if cursor.fetchone():
            print(f"✓ 数据库 '{db_name}' 存在")
        else:
            print(f"⚠ 数据库 '{db_name}' 不存在")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保PostgreSQL服务正在运行")
        print("2. 检查数据库用户名和密码")
        print("3. 确认数据库名称正确")
        print("4. 使用环境变量设置正确的连接参数:")
        print("   export DB_USER=your_username")
        print("   export DB_PASSWORD=your_password")
        print("   export DB_NAME=your_database")

if __name__ == "__main__":
    test_database_connection()