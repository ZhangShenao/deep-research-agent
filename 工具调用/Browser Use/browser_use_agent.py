# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/29 20:11
@Author  : ZhangShenao
@File    : browser_use_agent.py
@Desc    : 实现Browser Use Agent

基于开源的Browser Use库: https://github.com/browser-use/browser-use
该项目是基于Playwright框架
构建的一个python库,可以通过代码的方式让AI对浏览器进行操作

pip install browser-use

"""

import asyncio
from dotenv import load_dotenv

from browser_use import Agent, BrowserProfile, Controller, BrowserSession
from model import WeatherInfo
from llm import DEEPSEEK
from prompt import SYSTEM_PROMPT


# 加载环境变量
load_dotenv()

# 创建指令控制器,格式化模型输出
controller = Controller(
    output_model=WeatherInfo,
)

# 创建浏览器配置
config = BrowserProfile(
    headless=True,  # 无头模式，不显示浏览器窗口
    disable_security=True,  # 禁用浏览器安全控制
    enable_default_extensions=False,  # 禁止下载扩展
    chromium_sandbox=False,  # 禁用沙盒
)

# 创建浏览器会话
session = BrowserSession(browser_profile=config)


async def run(query: str) -> None:
    """
    运行Agent
    """

    agent = Agent(
        task=SYSTEM_PROMPT.format(query=query),
        llm=DEEPSEEK,
        browser_session=session,
        controller=controller,
        use_vision=False,
    )

    result = await agent.run()
    print(f"Agent 执行结果: \n{result}\n")


if __name__ == "__main__":
    asyncio.run(run("今天北京天气怎么样？"))
