# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/26 20:08
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM大模型
"""

# 标准库导入
import os

# 第三方库导入
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 创建DeepSeek模型
DEEPSEEK_CLIENT = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL")
)
