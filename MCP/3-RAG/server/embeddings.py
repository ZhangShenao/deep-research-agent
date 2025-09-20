# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 19:36
@Author  : ZhangShenao
@File    : embeddings.py
@Desc    : Embedding实现
"""

import numpy as np
from dotenv import load_dotenv
import os
from zai import ZhipuAiClient
from typing import List

# 向量维度
EMBEDDING_DIM = 1536

# 加载环境变量
load_dotenv()


# 创建智谱AI客户端
zhipu_client = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))


# 定义异步的embedding函数
async def text_embedding(texts: List[str]) -> np.ndarray:
    """
    异步函数: 对文本进行embedding
    :param text: 待embedding文本
    :return: 文本embedding
    """
    resp = zhipu_client.embeddings.create(
        input=texts,
        model="embedding-3",  # 使用embedding-3模型
        dimensions=EMBEDDING_DIM,  # 指定向量维度
    )
    return np.array([d.embedding for d in resp.data], dtype="float32")
