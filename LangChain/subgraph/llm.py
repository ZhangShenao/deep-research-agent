# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/09
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM 大模型配置 - 使用 DeepSeek
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 加载环境变量
load_dotenv()


# 创建 DeepSeek 模型实例
LLM = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0.7,
)
