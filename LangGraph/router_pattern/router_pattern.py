"""
@Time    : 2026/02/03
@Author  : ZhangShenao
@File    : router_pattern.py
@Desc    : Router Pattern 路由器模式

路由器模式是LangGraph中的一个核心概念
它允许LLM根据用户输入智能地决定下一步行动
直接回复：当用户的问题不需要工具时,直接生成自然语言回复
调用工具：当用户的问题需要计算、查询或处理时,调用相应的工具

这种模式是构建Agent基础,让AI能够像人类一样思考和行动
"""
