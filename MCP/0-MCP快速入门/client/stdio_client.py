# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 15:08
@Author  : ZhangShenao
@File    : client.py
@Desc    : 基于stdio协议的MCP Client

执行命令: uv run stdio_client.py

在使用stdio方式进行通信时,MCP Server的进程是由MCP Client程序负责拉起的
此时,Server进程只能与启动它的Client进行通信(1:1 关系)

"""

# 引入MCP Client相关库
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio


# 通过StdioServerParameters,配置MCP Server的连接参数
server_params = StdioServerParameters(
    command="uv",  # 启动命令
    args=[
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "/Users/zsa/Desktop/AGI/DeepResearch智能体/deep-research-agent/MCP/0-MCP快速入门/server",
        "mcp",
        "run",
        "/Users/zsa/Desktop/AGI/DeepResearch智能体/deep-research-agent/MCP/0-MCP快速入门/server/stdio_server.py",
    ],  # 启动参数
    env=None,  # 环境变量
)


async def run():
    """启动MCP Client"""

    # 连接到MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 通过initialize协议,初始化Session
            await session.initialize()

            # 通过list_tools协议,获取MCP工具列表
            tools = await session.list_tools()
            print(f"获取到MCP工具列表: \n{tools}")

            # 通过call_tool协议,调用MCP工具
            score = await session.call_tool(
                name="get_performance_by_name",  # 指定工具名称
                arguments={"name": "张三"},  # 指定工具参数
            )
            print(f"工具调用结果: \n{score}")


if __name__ == "__main__":
    asyncio.run(run())
