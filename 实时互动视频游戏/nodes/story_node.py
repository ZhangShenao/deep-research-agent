# -*- coding: utf-8 -*-
"""
剧情续写节点
"""
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from state import GameState
from llm import DEEPSEEK
from prompts import STORY_CONTINUATION_PROMPT
from utils import save_story, get_next_story_index
from worldview import get_default_worldview


def story_continuation_node_stream(state: GameState, stream_placeholder=None):
    """
    剧情续写节点（流式版本）
    根据用户输入续写剧情，支持流式输出
    """
    try:
        # 获取用户输入（最后一条用户消息）
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            return {**state, "error": "未找到用户输入"}
        
        user_input = user_messages[-1].content
        
        # 获取世界观和故事上下文
        worldview = get_default_worldview() if not state.get("story_context") else state["story_context"]
        story_context = state.get("story_context", worldview)
        
        # 构建提示词
        prompt = STORY_CONTINUATION_PROMPT.format(
            worldview=worldview,
            story_context=story_context,
            user_input=user_input
        )
        
        # 流式调用LLM生成剧情
        latest_story = ""
        if stream_placeholder:
            # 使用流式输出
            for chunk in DEEPSEEK.stream([HumanMessage(content=prompt)]):
                # chunk可能是AIMessage类型，直接获取content
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    latest_story += content
                    # 实时更新显示
                    stream_placeholder.markdown(latest_story)
        else:
            # 非流式输出（备用）
            response = DEEPSEEK.invoke([HumanMessage(content=prompt)])
            latest_story = response.content
        
        # 更新故事上下文（追加新剧情）
        updated_story_context = f"{story_context}\n\n{latest_story}"
        
        # 保存故事
        session_id = state.get("session_id", "default")
        story_index = get_next_story_index(session_id)
        save_story(latest_story, story_index, session_id)
        
        # 更新状态
        return {
            **state,
            "latest_story": latest_story,
            "story_context": updated_story_context,
            "current_step": "storyboard",
            "error": None,
            "messages": state["messages"] + [AIMessage(content=f"剧情已续写：\n{latest_story}")]
        }
    except Exception as e:
        return {
            **state,
            "error": f"剧情续写失败: {str(e)}",
            "current_step": "error"
        }


def story_continuation_node(state: GameState) -> GameState:
    """
    剧情续写节点
    根据用户输入续写剧情
    """
    try:
        # 获取用户输入（最后一条用户消息）
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            return {**state, "error": "未找到用户输入"}
        
        user_input = user_messages[-1].content
        
        # 获取世界观和故事上下文
        worldview = get_default_worldview() if not state.get("story_context") else state["story_context"]
        story_context = state.get("story_context", worldview)
        
        # 构建提示词
        prompt = STORY_CONTINUATION_PROMPT.format(
            worldview=worldview,
            story_context=story_context,
            user_input=user_input
        )
        
        # 调用LLM生成剧情
        response = DEEPSEEK.invoke([HumanMessage(content=prompt)])
        latest_story = response.content
        
        # 更新故事上下文（追加新剧情）
        updated_story_context = f"{story_context}\n\n{latest_story}"
        
        # 保存故事
        session_id = state.get("session_id", "default")
        story_index = get_next_story_index(session_id)
        save_story(latest_story, story_index, session_id)
        
        # 更新状态
        return {
            **state,
            "latest_story": latest_story,
            "story_context": updated_story_context,
            "current_step": "storyboard",
            "error": None,
            "messages": state["messages"] + [AIMessage(content=f"剧情已续写：\n{latest_story}")]
        }
    except Exception as e:
        return {
            **state,
            "error": f"剧情续写失败: {str(e)}",
            "current_step": "error"
        }

