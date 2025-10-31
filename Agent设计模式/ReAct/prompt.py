# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/26 20:08
@Author  : ZhangShenao
@File    : prompt.py
@Desc    : ReAct模式提示词
"""

# ReAct模式提示词
# 这段Prompt是实现ReAct模式的核心,用于指导模型进行思考、行动、行动输入、暂停、观察的循环
REACT_PROMPT = """
You run in a loop of Thought, Action, Action Input, Pause, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you
Use Action Input to indicate the input to the Action- then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:
   
{tools}

Rules:
1- If the input is a greeting or a goodbye, respond directly in a friendly manner without using the Thought-Action loop.
2- Otherwise, follow the Thought-Action Input loop to find the best answer.
3- If you already have the answer to a part or the entire question, use your knowledge without relying on external actions.
4- If you need to execute more than one Action, do it on separate calls.
5- At the end, provide a final answer.

Some examples:

### 1
Question: 今天北京天气怎么样？
Thought: 我需要调用 get_weather 工具获取天气
Action: get_weather
Action Input: {"city": "BeiJing"}

Pause

You will be called again with this:

Observation: 北京的气温是0度.

You then output: 
Final Answer: 北京的气温是0度.

Begin!

"""
