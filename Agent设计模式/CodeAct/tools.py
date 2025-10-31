# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 工具定义
"""


from langchain.agents import tool
from langchain.tools import Tool


# 使用@tool装饰器,将函数转换为LangChain的工具
@tool
def execute_python_code(code: str) -> str:
    """执行Python代码并返回结果。"""
    try:
        print("##执行Python代码:\n", code)
        # 创建本地环境执行代码
        local_vars = {}

        # 使用Python内置的的exec函数,执行Python代码
        exec(code, {}, local_vars)
        result = local_vars.get("result", "执行成功")
        print("##代码执行结果:\n", result)
        return str(result)
    except Exception as e:
        return f"Error executing code: {str(e)}"


# 定义工具列表
TOOLS: list[Tool] = [execute_python_code]

# 定义工具字典
TOOL_DICT: dict[str, Tool] = {
    "execute_python_code": execute_python_code,
}
