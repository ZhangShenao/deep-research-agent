# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM大模型
"""

# 标准库导入
import os

# 第三方库导入
from dotenv import load_dotenv
from tools import TOOLS
from langchain_openai import ChatOpenAI


# 加载环境变量
load_dotenv()


# 创建DeepSeek模型
LLM = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

# 将LLM绑定工具
LLM_WITH_TOOLS = LLM.bind_tools(TOOLS)
