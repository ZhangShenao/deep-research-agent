# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : agent.py
@Desc    : 客服 Agent 主程序
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from tools import ALL_TOOLS
from nodes import chatbot_node, async_chatbot_node


def build_customer_service_agent(
    checkpointer: Optional[BaseCheckpointSaver] = None,
    use_async: bool = False,
) -> CompiledStateGraph:
    """
    构建客服 Agent
    
    创建一个完整的客服 Agent 图，包括：
    - 聊天机器人节点：处理用户消息
    - 工具节点：执行工具调用
    - 条件边：根据是否需要工具调用路由
    
    Args:
        checkpointer: 检查点存储器，用于持久化状态
        use_async: 是否使用异步节点
        
    Returns:
        编译后的 Agent 图
    """
    # 创建状态图
    graph = StateGraph(AgentState)
    
    # 选择同步或异步节点
    chatbot = async_chatbot_node if use_async else chatbot_node
    
    # 添加节点
    graph.add_node("chatbot", chatbot)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    
    # 添加边
    graph.add_edge(START, "chatbot")
    
    # 添加条件边：根据是否有工具调用决定下一步
    # tools_condition 检查最后一条消息是否包含工具调用
    # 如果有工具调用，路由到 "tools" 节点
    # 如果没有，路由到 END
    graph.add_conditional_edges(
        source="chatbot",
        path=tools_condition,
    )
    
    # 工具执行完成后，返回聊天机器人继续处理
    graph.add_edge("tools", "chatbot")
    
    # 如果没有提供 checkpointer，使用内存存储
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    # 编译图
    compiled_graph = graph.compile(checkpointer=checkpointer)
    
    return compiled_graph


def build_agent_with_mongodb(
    mongodb_uri: str = "mongodb://localhost:27017",
    db_name: str = "customer_service",
    use_async: bool = False,
) -> CompiledStateGraph:
    """
    使用 MongoDB 作为检查点存储构建 Agent
    
    Args:
        mongodb_uri: MongoDB 连接字符串
        db_name: 数据库名称
        use_async: 是否使用异步模式
        
    Returns:
        编译后的 Agent 图
    """
    if use_async:
        from mongodb_checkpointer import AsyncMongoDBSaver
        checkpointer = AsyncMongoDBSaver.from_conn_string(
            mongodb_uri,
            db_name=db_name
        )
    else:
        from mongodb_checkpointer import MongoDBSaver
        checkpointer = MongoDBSaver.from_conn_string(
            mongodb_uri,
            db_name=db_name
        )
    
    return build_customer_service_agent(
        checkpointer=checkpointer,
        use_async=use_async
    )


def save_agent_graph_image(agent: CompiledStateGraph, output_path: str = "./agent_graph.png"):
    """
    保存 Agent 图的可视化图像
    
    Args:
        agent: 编译后的 Agent
        output_path: 输出文件路径
    """
    try:
        agent.get_graph().draw_mermaid_png(output_file_path=output_path)
        print(f"Agent 图已保存到: {output_path}")
    except Exception as e:
        print(f"保存 Agent 图失败: {e}")


if __name__ == "__main__":
    # 测试构建 Agent
    agent = build_customer_service_agent()
    print("Agent 构建成功！")
    
    # 保存图像
    save_agent_graph_image(agent)

