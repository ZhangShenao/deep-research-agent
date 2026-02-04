# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : checkpointer.py
@Desc    : 基于SQLite的Checkpointer实现
"""

from sqlite import SQLITE_CONN
from langgraph.checkpoint.sqlite import SqliteSaver

CHECKPOINTER = SqliteSaver(SQLITE_CONN)
print("已创建SQLite Checkpointer")
