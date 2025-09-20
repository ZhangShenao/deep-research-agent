# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/20 20:08
@Author  : ZhangShenao
@File    : client.py
@Desc    : RAG MCP Client
"""

# 标准库导入
import json
import os


# 第三方库导入
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI

# System Prompt
SYSTEM_PROMPT = """
你是一位专业的医学助手，请根据提供的医学文档回答问题。
如果用户的问题需要查询医学知识，请使用列表中的工具来获取相关信息。
"""

# 加载环境变量
load_dotenv()


# 定义RagMCPClient类,作为MCP客户端
class RagMCPClient:
    """
    RAG MCP客户端类

    该类负责与MCP服务器建立连接，管理工具调用，并通过DeepSeek模型
    提供基于检索增强生成(RAG)的问答服务。
    """

    def __init__(self):
        """
        初始化RAG MCP客户端

        初始化MCP连接相关属性、DeepSeek客户端以及工具列表。
        从环境变量中读取API密钥和基础URL配置。
        """
        # 初始化MCP连接
        self.session = None
        self.transport = None  # 用来保存stdio_client的上下文管理器

        # 初始化DeepSeek客户端
        self.deepseek_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
        )

        # 初始化MCP工具,将在connect后从MCP Server获取
        self.tools = []

    async def connect(self, server_script: str) -> None:
        """
        连接到MCP服务器

        通过stdio方式连接到指定的MCP服务器脚本，初始化会话，
        并获取服务器提供的工具列表。

        Args:
            server_script (str): MCP服务器脚本的路径

        Raises:
            Exception: 当连接失败或初始化出错时抛出异常
        """
        # 构造连接参数
        # 通过uv运行MCP Server脚本
        params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                server_script,
            ],
        )

        # 创建stdio_client
        self.transport = stdio_client(params)

        # 进入上下文管理器,拿到stdio和write
        self.stdio, self.write = await self.transport.__aenter__()

        # 初始化MCP Session
        self.session = await ClientSession(self.stdio, self.write).__aenter__()
        await self.session.initialize()  # 必须要手动执行initialize,否则无法初始化对话

        # 执行list_tools消息,从MCP Server获取工具列表
        tools_resp = await self.session.list_tools()

        # 将工具解析为模型的function calling格式
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_resp.tools
        ]

        print(f"MCP工具列表: {self.tools}")

    async def query(self, q: str) -> str:
        """
        执行用户查询

        通过DeepSeek模型处理用户问题，支持工具调用功能。
        如果模型决定使用工具，会自动调用相应的MCP工具获取信息。

        Args:
            q (str): 用户的问题或查询内容

        Returns:
            str: 模型的回答内容，如果出现错误则返回错误提示信息
        """
        # 初始化消息列表
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": q},
        ]

        while True:
            try:
                # 调用DeepSeek,获取结果
                resp = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=0.1,
                    tools=self.tools,
                    tool_choice="auto",  # 让模型自行决策工具调用
                )

                # 保存对话历史
                message = resp.choices[0].message
                messages.append(message)

                # 如果模型没有进行工具调用,则直接返回结果
                if message.tool_calls is None:
                    return message.content

                # 模型生成了工具调用,则解析工具调用参数
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    # 调用工具,获取结果
                    tool_call_result = await self.session.call_tool(name, args)

                    # 在对话历史中添加工具调用结果
                    messages.append(
                        {
                            "role": "tool",
                            "content": str(
                                tool_call_result
                            ),  # 确保工具调用结果为字符串
                            "tool_call_id": tool_call.id,
                        }
                    )

            except Exception as e:
                print(f"调用DeepSeek时出错: {str(e)}")
                return "抱歉，处理您的请求时出现了问题，请稍后重试~"

    async def close(self) -> None:
        """
        关闭MCP连接

        优雅地关闭与MCP服务器的连接，包括关闭会话和传输层连接。
        确保资源得到正确释放。

        Raises:
            Exception: 当关闭连接时出现错误会打印错误信息但不抛出异常
        """
        try:
            # 先关闭Session
            if self.session is not None:
                await self.session.__aexit__(None, None, None)

            # 再退出Stdio client上下文
            if self.transport is not None:
                await self.transport.__aexit__(None, None, None)

        except Exception as e:
            print(f"关闭MCP连接时出错: {str(e)}")
