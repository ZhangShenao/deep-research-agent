# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : main.py
@Desc    : 客服 Agent 运行入口和演示脚本

本文件演示 LangGraph Checkpoint 的核心功能：
1. 多轮对话记忆（Memory）
2. 人机交互（Human-in-the-Loop）
3. 时间旅行（Time Travel）
4. 状态管理 API
"""

import sys
import io
import asyncio
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agent import build_customer_service_agent, build_agent_with_mongodb
from mongodb_checkpointer import MongoDBSaver


def print_separator(title: str = ""):
    """打印分隔线"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def print_messages(messages: list, last_n: int = None, max_length: int = None):
    """
    打印消息列表
    
    Args:
        messages: 消息列表
        last_n: 只打印最后 n 条消息
        max_length: 最大长度限制，None 表示不限制
    """
    if last_n:
        messages = messages[-last_n:]
    
    for msg in messages:
        role = msg.__class__.__name__.replace("Message", "")
        content = msg.content if hasattr(msg, 'content') else str(msg)
        
        # 可选：截断过长的内容
        if max_length and len(content) > max_length:
            content = content[:max_length] + "..."
        
        print(f"[{role}] {content}")


def demo_memory_feature():
    """
    演示 1：多轮对话记忆（Memory）
    
    展示如何通过 thread_id 实现多轮对话的上下文记忆。
    """
    print_separator("演示 1：多轮对话记忆（Memory）")
    
    # 构建 Agent（使用内存存储）
    agent = build_customer_service_agent()
    
    # 使用同一个 thread_id 进行多轮对话
    config = {"configurable": {"thread_id": "demo-memory-001"}}
    
    # 第一轮对话
    print("\n📝 第一轮对话：")
    result = agent.invoke(
        {"messages": [HumanMessage(content="你好，我想了解一下 iPhone")]},
        config=config
    )
    print_messages(result["messages"], last_n=2)
    
    # 第二轮对话 - Agent 应该记住上下文
    print("\n📝 第二轮对话（Agent 应该记住我们在讨论 iPhone）：")
    result = agent.invoke(
        {"messages": [HumanMessage(content="它多少钱？")]},
        config=config
    )
    print_messages(result["messages"], last_n=2)
    
    # 第三轮对话
    print("\n📝 第三轮对话：")
    result = agent.invoke(
        {"messages": [HumanMessage(content="库存还有多少？")]},
        config=config
    )
    print_messages(result["messages"], last_n=2)
    
    print("\n✅ 演示完成：Agent 成功保持了多轮对话的上下文记忆")


def demo_human_in_the_loop():
    """
    演示 2：人机交互（Human-in-the-Loop）
    
    展示当 Agent 遇到无法处理的问题时，如何暂停执行等待人类输入。
    """
    print_separator("演示 2：人机交互（Human-in-the-Loop）")
    
    # 构建 Agent
    agent = build_customer_service_agent()
    config = {"configurable": {"thread_id": "demo-hitl-001"}}
    
    # 发送一个需要人工介入的问题
    print("\n📝 用户提问（这个问题需要人工介入）：")
    print("[User] 我的订单 ORD999 发货有问题，快递丢了怎么办？")
    
    result = agent.invoke(
        {"messages": [HumanMessage(content="我的订单 ORD999 发货有问题，快递丢了怎么办？")]},
        config=config
    )
    
    # 检查是否有中断（需要人工介入）
    if "__interrupt__" in result and result["__interrupt__"]:
        interrupt_info = result["__interrupt__"][0]
        print(f"\n⏸️ Agent 请求人工介入：{interrupt_info.value}")
        
        # 模拟人工输入
        human_response = "您的订单 ORD999 快递丢失问题已记录，我们会在24小时内联系您处理赔偿事宜，请保持电话畅通。"
        print(f"\n👤 人工客服回复：{human_response}")
        
        # 恢复执行
        result = agent.invoke(
            Command(resume=human_response),
            config=config
        )
        
        print("\n📤 Agent 最终回复：")
        print_messages(result["messages"], last_n=1)
    else:
        print("\n📤 Agent 回复（无需人工介入）：")
        print_messages(result["messages"], last_n=1)
    
    print("\n✅ 演示完成：成功展示了 Human-in-the-Loop 功能")


def demo_time_travel():
    """
    演示 3：时间旅行（Time Travel）
    
    展示如何查看历史状态并从某个历史检查点恢复执行。
    """
    print_separator("演示 3：时间旅行（Time Travel）")
    
    # 构建 Agent
    agent = build_customer_service_agent()
    config = {"configurable": {"thread_id": "demo-timetravel-001"}}
    
    # 进行几轮对话，产生多个检查点
    print("\n📝 进行多轮对话，产生检查点历史...")
    
    conversations = [
        "你好",
        "有什么商品可以买？",
        "MacBook Pro 多少钱？",
        "库存怎么样？",
    ]
    
    for msg in conversations:
        result = agent.invoke(
            {"messages": [HumanMessage(content=msg)]},
            config=config
        )
        print(f"[User] {msg}")
        print(f"[AI] {result['messages'][-1].content[:100]}...")
        print()
    
    # 查看状态历史
    print("\n📜 查看状态历史（get_state_history）：")
    print("-" * 40)
    
    history = list(agent.get_state_history(config))
    for i, state in enumerate(history[:5]):  # 只显示前5个
        msg_count = len(state.values.get("messages", []))
        next_node = state.next
        checkpoint_id = state.config["configurable"]["checkpoint_id"][:16]
        print(f"检查点 {i+1}: 消息数={msg_count}, 下一节点={next_node}, ID={checkpoint_id}...")
    
    if len(history) > 5:
        print(f"... 共 {len(history)} 个检查点")
    
    # 选择一个历史状态进行回放
    if len(history) >= 4:
        print("\n⏪ 时间旅行：回到第 4 个检查点，重新开始对话")
        
        target_state = history[3]  # 选择一个较早的状态
        print(f"目标检查点 ID: {target_state.config['configurable']['checkpoint_id'][:16]}...")
        print(f"当时消息数: {len(target_state.values.get('messages', []))}")
        
        # 从该检查点继续执行，但换一个问题
        result = agent.invoke(
            {"messages": [HumanMessage(content="换个话题，AirPods Pro 怎么样？")]},
            config=target_state.config
        )
        
        print("\n📤 从历史检查点恢复后的新对话：")
        print_messages(result["messages"], last_n=2)
    
    print("\n✅ 演示完成：成功展示了 Time Travel 功能")


def demo_state_management_api():
    """
    演示 4：状态管理 API
    
    展示 get_state、get_state_history 等 API 的使用。
    """
    print_separator("演示 4：状态管理 API")
    
    # 构建 Agent
    agent = build_customer_service_agent()
    config = {"configurable": {"thread_id": "demo-api-001"}}
    
    # 执行一次对话
    print("\n📝 执行对话...")
    result = agent.invoke(
        {"messages": [HumanMessage(content="iPhone 15 Pro 多少钱？")]},
        config=config
    )
    
    # 获取当前状态
    print("\n📊 get_state() - 获取当前状态：")
    print("-" * 40)
    current_state = agent.get_state(config)
    
    print(f"配置: thread_id={current_state.config['configurable']['thread_id']}")
    print(f"检查点 ID: {current_state.config['configurable']['checkpoint_id'][:20]}...")
    print(f"下一节点: {current_state.next}")
    print(f"消息数量: {len(current_state.values.get('messages', []))}")
    print(f"元数据: {current_state.metadata}")
    
    # 获取状态历史
    print("\n📜 get_state_history() - 获取状态历史：")
    print("-" * 40)
    
    for i, state in enumerate(agent.get_state_history(config)):
        step = state.metadata.get("step", "N/A")
        source = state.metadata.get("source", "N/A")
        print(f"步骤 {step}: source={source}, next={state.next}")
        
        if i >= 4:
            print("...")
            break
    
    print("\n✅ 演示完成：成功展示了状态管理 API")


def demo_mongodb_checkpoint():
    """
    演示 5：MongoDB 检查点存储
    
    展示如何使用 MongoDB 作为检查点存储。
    注意：需要本地运行 MongoDB 服务。
    """
    print_separator("演示 5：MongoDB 检查点存储")
    
    mongodb_uri = "mongodb://localhost:27017"
    db_name = "customer_service_demo"
    
    print(f"\n🔌 连接 MongoDB: {mongodb_uri}")
    print(f"📁 数据库: {db_name}")
    
    try:
        # 使用 MongoDB 构建 Agent
        agent = build_agent_with_mongodb(
            mongodb_uri=mongodb_uri,
            db_name=db_name
        )
        
        print("✅ MongoDB 连接成功！")
        
        # 进行对话
        config = {"configurable": {"thread_id": "mongo-demo-001"}}
        
        print("\n📝 使用 MongoDB 存储进行对话...")
        result = agent.invoke(
            {"messages": [HumanMessage(content="帮我查一下 AirPods Pro 的信息")]},
            config=config
        )
        
        print("\n📤 Agent 回复：")
        print_messages(result["messages"], last_n=1)
        
        # 验证状态已保存到 MongoDB
        print("\n📊 验证状态已保存到 MongoDB...")
        current_state = agent.get_state(config)
        print(f"检查点 ID: {current_state.config['configurable']['checkpoint_id'][:20]}...")
        print(f"消息数量: {len(current_state.values.get('messages', []))}")
        
        print("\n✅ 演示完成：MongoDB 检查点存储工作正常")
        
    except Exception as e:
        print(f"\n❌ MongoDB 连接失败: {e}")
        print("请确保本地 MongoDB 服务正在运行")
        print("启动命令: mongod --dbpath /path/to/data")


def interactive_chat():
    """
    交互式聊天模式
    
    允许用户与客服 Agent 进行实时对话。
    """
    print_separator("交互式聊天模式")
    
    print("\n欢迎使用电商客服 Agent！")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'history' 查看对话历史")
    print("输入 'travel' 查看检查点历史")
    print("-" * 40)
    
    # 构建 Agent
    agent = build_customer_service_agent()
    config = {"configurable": {"thread_id": "interactive-001"}}
    
    # 设置输入编码
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 再见！")
                break
            
            if user_input.lower() == "history":
                state = agent.get_state(config)
                print("\n📜 对话历史：")
                print_messages(state.values.get("messages", []))
                continue
            
            if user_input.lower() == "travel":
                print("\n⏪ 检查点历史：")
                for i, state in enumerate(agent.get_state_history(config)):
                    print(f"{i+1}. 消息数={len(state.values.get('messages', []))}, next={state.next}")
                    if i >= 9:
                        print("...")
                        break
                continue
            
            # 发送消息给 Agent
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # 检查是否需要人工介入
            if "__interrupt__" in result and result["__interrupt__"]:
                interrupt_info = result["__interrupt__"][0]
                print(f"\n⏸️ Agent 请求人工帮助：{interrupt_info.value}")
                human_response = input("👤 人工回复: ").strip()
                
                result = agent.invoke(
                    Command(resume=human_response),
                    config=config
                )
            
            # 打印 Agent 回复
            print(f"\n🤖 Agent: {result['messages'][-1].content}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  LangGraph Checkpoint 演示程序")
    print("=" * 60)
    
    print("\n请选择演示模式：")
    print("1. 多轮对话记忆（Memory）")
    print("2. 人机交互（Human-in-the-Loop）")
    print("3. 时间旅行（Time Travel）")
    print("4. 状态管理 API")
    print("5. MongoDB 检查点存储")
    print("6. 交互式聊天")
    print("7. 运行所有演示")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选项 (0-7): ").strip()
        
        if choice == "1":
            demo_memory_feature()
        elif choice == "2":
            demo_human_in_the_loop()
        elif choice == "3":
            demo_time_travel()
        elif choice == "4":
            demo_state_management_api()
        elif choice == "5":
            demo_mongodb_checkpoint()
        elif choice == "6":
            interactive_chat()
        elif choice == "7":
            demo_memory_feature()
            demo_human_in_the_loop()
            demo_time_travel()
            demo_state_management_api()
            demo_mongodb_checkpoint()
        elif choice == "0":
            print("\n👋 再见！")
        else:
            print("\n❌ 无效选项")
            
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

