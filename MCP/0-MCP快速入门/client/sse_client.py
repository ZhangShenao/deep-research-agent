# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 15:08
@Author  : ZhangShenao
@File    : client.py
@Desc    : 基于SSE协议的MCP Client

执行命令: uv run sse_client.py http://localhost:8000/sse

"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import sys


async def connect_to_sse_server(server_url: str):
    """Connect to an MCP server running with SSE transport"""
    async with sse_client(url=server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # List available tools to verify connection
            print("初始化MCP客户端")

            # 通过list_tools协议,获取MCP工具列表
            response = await session.list_tools()
            tools = response.tools
            print(f"获取到MCP工具列表: \n{tools}")

            # 通过call_tool协议,调用MCP工具
            score = await session.call_tool(
                name="get_performance_by_name", arguments={"name": "张三"}
            )

            print("工具调用结果: \n", score)


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: uv run client.py <URL of SSE MCP server (i.e. http://localhost:8000/sse)>"
        )
        sys.exit(1)

    await connect_to_sse_server(server_url=sys.argv[1])


if __name__ == "__main__":
    asyncio.run(main())
