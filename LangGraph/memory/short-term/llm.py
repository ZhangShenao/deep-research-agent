# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/03
@Author  : ZhangShenao
@File    : llm.py
@Desc    : LLM 节点
"""

import dotenv
import os
from langchain_openai import ChatOpenAI
from tools import tools

# 加载环境变量
dotenv.load_dotenv()

# 创建智谱LLM
LLM = ChatOpenAI(
    model="GLM-4.7-Flash",
    openai_api_key=os.getenv("ZHIPU_API_KEY"),
    openai_api_base=os.getenv("ZHIPU_BASE_URL"),
)

LLM_WITH_TOOLS = LLM.bind_tools(tools)
