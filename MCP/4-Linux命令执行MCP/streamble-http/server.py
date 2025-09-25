# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 20:08
@Author  : ZhangShenao
@File    : main.py
@Desc    : Streamble-Http MCP服务端
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import uvicorn

# 基于FastMCP库,创建MCP Server
mcp = FastMCP("mcp-server")


# 基于@mcp.tool()装饰器,定义MCP工具
@mcp.tool()
async def exec_linux_command(cmd: str) -> str:
    """
    执行Linux命令

    Args:
        cmd (str): Linux命令

    Returns:
        str: 命令执行结果
    """

    # 使用subprocess库执行Linux命令
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


# 以streamable_http协议,创建MCP Server
app = mcp.streamable_http_app()

if __name__ == "__main__":
    # 启动MCP Server,监听0.0.0.0:8000端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
