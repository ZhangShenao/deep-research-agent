# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 20:08
@Author  : ZhangShenao
@File    : client.py
@Desc    : Streamble-Http MCP客户端
"""

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio
import sys


async def connect_to_streamble_server(server_url: str) -> None:
    """
    连接到Streamble HTTP MCP服务器

    Args:
        server_url (str): Streamble HTTP MCP服务器的URL
    """

    # 创建Streamable HTTP协议的连接
    async with streamablehttp_client(url=server_url) as (
        read_stream,
        write_stream,
        _,
    ):
        # 创建Session
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化Session
            await session.initialize()

            # 使用list_tools协议,获取MCP工具列表
            tools = await session.list_tools()
            print(f"获取到工具列表: \n{tools}\n")

            # 使用call_tool协议,调用MCP工具
            # 这里hard code指定调用exec_linux_command工具
            result = await session.call_tool(
                name="exec_linux_command", arguments={"cmd": "ls -l"}
            )

            print(f"工具调用结果: \n{result}\n")


async def main():
    """异步主函数"""

    # 从命令行参数中获取server_url
    if len(sys.argv) < 2:
        print(
            "Usage: python client.py <URL of Streamble HTTP MCP server (i.e. http://localhost:8000/mcp)>"
        )
        sys.exit(1)

    url = sys.argv[1]
    await connect_to_streamble_server(server_url=url)


if __name__ == "__main__":
    asyncio.run(main())
