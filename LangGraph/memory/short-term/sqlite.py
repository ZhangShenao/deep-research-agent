# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : sqlite.py
@Desc    : 使用SQLite作为短期记忆的外部存储
"""

import sqlite3


# 设置数据库文件路径
DB_PATH = "db/memory.db"

# 创建数据库连接
SQLITE_CONN = sqlite3.connect(DB_PATH, check_same_thread=False)

print(f"已连接到持久化SQLite数据库，文件路径: {DB_PATH}")
