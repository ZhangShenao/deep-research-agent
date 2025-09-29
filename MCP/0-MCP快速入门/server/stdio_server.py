# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : server.py
@Desc    : 基于FastMCP SDK,使用stdio协议,实现MCP服务端
"""

from mcp.server.fastmcp import FastMCP

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
