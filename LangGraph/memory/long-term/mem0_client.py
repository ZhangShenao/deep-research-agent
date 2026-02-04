# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : mem0_client.py
@Desc    : mem0客户端
"""

import os
import dotenv
from mem0 import Memory

# 加载环境变量
dotenv.load_dotenv()

# 配置 mem0
config = {
    # 配置语言模型,使用qwen3-max
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen3-max",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "openai_base_url": os.getenv("DASHSCOPE_BASE_URL"),
        },
    },
    # 配置embedding模型,使用text-embedding-v4
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-v4",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "openai_base_url": os.getenv("DASHSCOPE_BASE_URL"),
        },
    },
    # 配置向量存储,使用本地的qdrant
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",  # 指定collection空间
            "host": "127.0.0.1",
            "port": 6333,
            # "embedding_model_dims": 1536  # 指定embedding向量维度
        },
    },
}

# 基于配置, 创建 mem0 客户端
mem0_client = Memory.from_config(config)
