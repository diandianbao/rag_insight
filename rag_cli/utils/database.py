"""
数据库工具模块
"""

import logging
from typing import Dict, Any, Optional


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            conn.close()
            self.logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            self.logger.error(f"数据库连接测试失败: {e}")
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            # 获取数据库版本
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

            # 获取数据库名称
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]

            # 获取表数量
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return {
                "version": version,
                "database_name": db_name,
                "table_count": table_count
            }

        except Exception as e:
            self.logger.error(f"获取数据库信息失败: {e}")
            return {}

    def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
            """, (table_name,))

            exists = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return exists

        except Exception as e:
            self.logger.error(f"检查表存在性失败: {e}")
            return False