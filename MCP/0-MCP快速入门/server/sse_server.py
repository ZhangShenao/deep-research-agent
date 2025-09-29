# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 15:08
@Author  : ZhangShenao
@File    : sse_server.py
@Desc    : 基于SSE协议的MCP服务端

Server-Sent Events(SSE, 服务器发送事件)是一种基于HTTP协议的技术
允许服务器向客户端单向、实时地推送数据
在SSE模式下,客户端通过创建一个EventSource对象与服务器建立持久连接
服务器则通过该连接持续发送数据流,而无需客户端反复发送请求
MCP Python SDK使用了Starlette框架来实现SSE

SSE模式下客户端通过访问Server的/messages端点发送JSON-RPC调用
并通过/sse端点获取服务器推送的JSON-RPC消息

启动命令: uv run sse_server.py
"""

from mcp.server.fastmcp import FastMCP
from starlette.routing import Mount, Route
from mcp.server import Server
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
import uvicorn
import argparse


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建一个Starlette应用,用于提供SSE协议的MCP服务"""

    # 创建SseServerTransport对象,并指定基础路径/messages/
    # 用于后续管理SSE连接和消息传递
    sse = SseServerTransport("/messages/")

    # 定义异步请求处理函数
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


# 基于FastMCP SDK,创建MCP Server
mcp = FastMCP("performance-mcp-server")


# 基于@mcp.tool()装饰器,定义MCP Tool
@mcp.tool()
def get_performance_by_name(name: str) -> str:
    """根据员工的姓名获取该员工的绩效得分"""

    if name == "张三":
        return "name: 张三 绩效评分: 85.9"
    if name == "李四":
        return "name: 李四 绩效评分: 92.7"

    return "未搜到该员工的绩效"


# 基于@mcp.resource()装饰器,定义MCP Resource
@mcp.resource("file://info.md")
def get_file() -> str:
    """读取info.md的内容，从而获取员工的信息，例如性别等"""

    with open(
        "/Users/zsa/Desktop/AGI/DeepResearch智能体/deep-research-agent/MCP/0-MCP快速入门/server/info.md",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


# 基于@mcp.prompt()装饰器,定义MCP Prompt
@mcp.prompt()
def prompt(name: str) -> str:
    """创建一个 prompt，用于对员工进行绩效评价"""

    return f"""绩效满分是100分，请获取{name}的绩效评分，并给出评价"""


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    args = parser.parse_args()

    # 将MCP Server与Starlette应用绑定
    starlette_app = create_starlette_app(mcp_server, debug=True)

    # 启动Starlette应用,监听指定端口
    uvicorn.run(starlette_app, host=args.host, port=args.port)
