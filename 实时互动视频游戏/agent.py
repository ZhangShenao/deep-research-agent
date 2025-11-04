# -*- coding: utf-8 -*-
"""
主Agent：LangGraph工作流
"""
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from state import GameState
from nodes import (
    story_continuation_node,
    storyboard_node,
    extract_frame_node,
    video_generation_node,
)


def build_agent() -> CompiledStateGraph:
    """
    构建Agent工作流
    流程：续写剧情 -> 构造分镜脚本 -> 抽取图片 -> 创作视频
    """
    # 创建状态图
    graph = StateGraph(GameState)
    
    # 添加节点
    graph.add_node("story_continuation", story_continuation_node)
    graph.add_node("storyboard", storyboard_node)
    graph.add_node("extract_frame", extract_frame_node)
    graph.add_node("video_generation", video_generation_node)
    
    # 添加边（定义工作流）
    graph.add_edge(START, "story_continuation")
    graph.add_edge("story_continuation", "storyboard")
    graph.add_edge("storyboard", "extract_frame")
    graph.add_edge("extract_frame", "video_generation")
    graph.add_edge("video_generation", END)
    
    # 编译并返回
    return graph.compile()


def run_agent_step(agent: CompiledStateGraph, state: GameState, step_name: str) -> dict:
    """
    运行Agent的单个步骤
    用于流式输出，每个步骤完成后立即返回结果
    """
    # 根据步骤名称执行相应的节点
    if step_name == "story_continuation":
        new_state = story_continuation_node(state)
    elif step_name == "storyboard":
        new_state = storyboard_node(state)
    elif step_name == "extract_frame":
        new_state = extract_frame_node(state)
    elif step_name == "video_generation":
        new_state = video_generation_node(state)
    else:
        new_state = state
    
    return new_state

