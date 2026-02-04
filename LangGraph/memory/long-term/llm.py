# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : llm.py
@Desc    : 语言模型
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 加载环境变量
load_dotenv()

# 创建qwen3-max模型
LLM = ChatOpenAI(
    model="qwen3-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)
