# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 20:08
@Author  : ZhangShenao
@File    : main.py
@Desc    : RAG MCP 执行入口,模拟一个MCP Host
"""

from client.client import RagMCPClient

# 标准库导入
import asyncio


async def main():
    """异步主函数"""

    print(">>> 开始初始化 RAG 系统")

    # 创建RAG MCP Client
    client = RagMCPClient()
    await client.connect(
        "/Users/zsa/Desktop/AGI/DeepResearch智能体/deep-research-agent/MCP/3-RAG/server/server.py"
    )
    print(">>> RAG MCP Server 连接成功")

    # 添加医学文档,构建索引
    medical_docs = [
        "糖尿病是一种慢性代谢性疾病，主要特征是血糖水平持续升高。",
        "高血压是指动脉血压持续升高，通常定义为收缩压≥180mmHg和/或舒张压≥60mmHg。",
        "冠心病是由于冠状动脉粥样硬化导致心肌缺血缺氧的疾病。",
        "哮喘是一种慢性气道炎症性疾病，表现为反复发作的喘息、气促、胸闷和咳嗽。",
        "肺炎是由细菌、病毒或其他病原体引起的肺部感染，常见症状包括发热、咳嗽和呼吸困难。",
    ]
    print(">>> 正在索引医学文档...")
    res = await client.session.call_tool("index_docs", {"docs": medical_docs})
    print(f">>> 文档索引完成\n{res}")

    # 开启RAG流程,回答用户提问
    while True:
        print("\n请输入您要查询的医学问题（输入'exit'结束查询）：")
        query = input("> ")

        if query.lower() == "exit":
            break

        print(f"\n正在查询: {query}")
        response = await client.query(query)
        print("\nAI 回答：\n", response)

    # 关闭MCP连接
    await client.close()
    print(">>> 系统已关闭")


if __name__ == "__main__":
    asyncio.run(main())
