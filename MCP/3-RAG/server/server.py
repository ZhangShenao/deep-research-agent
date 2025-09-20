# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 20:08
@Author  : ZhangShenao
@File    : server.py
@Desc    : RAG MCP Server
"""

# 标准库导入
from typing import List

# 第三方库导入
import faiss
import numpy as np
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 本地模块导入
from embeddings import EMBEDDING_DIM, text_embedding

# 加载环境变量
load_dotenv()

# 初始化MCP Server
mcp = FastMCP("rag-server")

# 基于内存版的Faiss,创建向量索引
# 采用L2距离索引类型
_index: faiss.IndexFlatL2 = faiss.IndexFlatL2(EMBEDDING_DIM)

# 保存原始文档
_docs: list[str] = []


# 使用装饰器定义MCP工具
@mcp.tool()
async def index_docs(docs: List[str]) -> str:
    """
    对一批文档构建向量索引

    Args:
        docs (List[str]): 需要建立索引的文档列表，每个元素是一个文档的文本内容

    Returns:
        str: 索引更新结果信息，包含本次更新的文档数量和当前总文档数量

    Raises:
        Exception: 当embedding操作失败时抛出异常

    Note:
        此函数会：
        1. 对输入的文档列表进行向量化处理
        2. 将向量添加到Faiss索引中
        3. 将原始文档保存到内存中
        4. 返回操作结果统计信息
    """
    global _index, _docs

    # 进行text embedding操作
    embeddings = await text_embedding(docs)

    # 更新索引
    _index.add(embeddings.astype("float32"))

    # 更新原始文档
    _docs.extend(docs)

    return f"增量更新 {len(docs)} 条索引，当前文档总数：{len(_docs)}"


@mcp.tool()
async def search_relevant_docs(query: str, top_k: int = 3) -> str:
    """
    根据查询词检索最相关的文档

    Args:
        query (str): 查询文本，用于检索相关文档
        top_k (int, optional): 返回最相关文档的数量，默认为3

    Returns:
        str: 检索结果

    Raises:
        Exception: 当embedding操作失败时抛出异常
        IndexError: 当索引超出文档范围时抛出异常

    Note:
        此函数会：
        1. 将查询文本转换为向量表示
        2. 使用Faiss进行相似性搜索
        3. 根据相似度返回最相关的top_k个文档
        4. 返回格式化的文档列表，包含索引号和文档内容

    Example:
        >>> result = await search_relevant_docs("机器学习", 5)
        >>> print(result)
        ['0 机器学习是人工智能的一个分支', '1 深度学习是机器学习的子领域', ...]
    """
    global _index, _docs

    # 对query进行embedding操作
    q_embedding = await text_embedding([query])

    # 使用Faiss进行相似性检索
    # 返回距离数组和索引数组
    distances, indexes = _index.search(q_embedding.astype("float32"), top_k)

    # 遍历索引数组，获取原始文档
    result = [f"{i+1} {_docs[i]}" for i in indexes[0] if i < len(_docs)]
    if len(result) == 0:
        return "没有检索到相关文档"

    # 返回检索结果
    return "\n\n".join(result)


# 启动MCP Server
if __name__ == "__main__":
    # 以stdio协议,启动MCP Server
    # 它会在当前进程中启动一个基于标准输入/输出(stdio)通道的MCP服务端
    # 此时,MCP服务器会监听从stdin到stdout的消息流,用来接收客户端发过来的JSON-RPC请求并返回响应
    # 这个启动方式适合将服务器作为子进程嵌入到其他程序里,通过管道进行通信
    mcp.run(transport="stdio")
