# -*- coding: utf-8 -*-
"""
分镜脚本生成节点
"""
import sys
import json
import re
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from state import GameState
from llm import DEEPSEEK
from prompts import STORYBOARD_PROMPT
from utils import save_storyboard, get_next_story_index


def extract_and_fix_json(text: str) -> tuple[str, dict]:
    """
    提取并修复JSON内容
    
    Returns:
        tuple: (清理后的文本, 解析后的数据) 或 (None, None) 如果失败
    """
    # 清理文本
    text = text.strip()
    
    # 移除markdown代码块标记
    if text.startswith("```json"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 1 and lines[-1].strip() == "```" else "\n".join(lines[1:])
    elif text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 1 and lines[-1].strip() == "```" else "\n".join(lines[1:])
    
    # 尝试提取JSON对象（如果被其他文本包围）
    json_match = re.search(r'\{[\s\S]*"shots"[\s\S]*\}', text)
    if json_match:
        text = json_match.group(0)
    
    # 尝试修复不完整的JSON（找到最后一个完整的结构）
    def fix_incomplete_json(t):
        t = t.strip()
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False
        last_valid_pos = -1
        
        for i, char in enumerate(t):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if in_string:
                continue
            
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    last_valid_pos = i
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
        
        if last_valid_pos > 0:
            t = t[:last_valid_pos + 1]
        
        return t.strip()
    
    # 尝试解析
    try:
        data = json.loads(text)
        return text, data
    except json.JSONDecodeError:
        # 尝试修复后再次解析
        try:
            fixed_text = fix_incomplete_json(text)
            data = json.loads(fixed_text)
            return fixed_text, data
        except json.JSONDecodeError:
            return None, None


def storyboard_node_stream(state: GameState, stream_placeholder=None):
    """
    分镜脚本生成节点（流式版本）
    根据剧情生成视频分镜脚本，支持流式输出
    """
    try:
        latest_story = state.get("latest_story")
        if not latest_story:
            return {
                **state,
                "error": "未找到最新剧情",
                "current_step": "error"
            }
        
        # 构建提示词
        prompt = STORYBOARD_PROMPT.format(story=latest_story)
        
        # 流式调用LLM生成分镜脚本
        storyboard_text = ""
        if stream_placeholder:
            # 使用流式输出
            for chunk in DEEPSEEK.stream([HumanMessage(content=prompt)]):
                # chunk可能是AIMessage类型，直接获取content
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    storyboard_text += content
                    # 实时更新显示（以代码块形式显示JSON）
                    stream_placeholder.code(storyboard_text, language="json")
        else:
            # 非流式输出（备用）
            response = DEEPSEEK.invoke([HumanMessage(content=prompt)])
            storyboard_text = response.content
        
        # 提取并修复JSON
        cleaned_text, storyboard_data = extract_and_fix_json(storyboard_text)
        
        if not storyboard_data:
            return {
                **state,
                "error": f"分镜脚本JSON解析失败\n原始内容前500字符: {storyboard_text[:500]}\n\n请尝试重新输入。",
                "current_step": "error"
            }
        
        shots = storyboard_data.get("shots", [])
        if not shots:
            return {
                **state,
                "error": "分镜脚本中未找到有效的分镜数据",
                "current_step": "error"
            }
        
        # 保存分镜脚本
        storyboard_index = get_next_story_index()
        save_storyboard(json.dumps(storyboard_data, ensure_ascii=False), storyboard_index)
        
        # 更新状态
        return {
            **state,
            "storyboard": cleaned_text or storyboard_text,
            "storyboard_shots": shots,
            "current_step": "extract_frame",
            "error": None,
            "messages": state["messages"] + [AIMessage(content=f"分镜脚本已生成，共{len(shots)}个分镜")]
        }
    except Exception as e:
        return {
            **state,
            "error": f"分镜脚本生成失败: {str(e)}",
            "current_step": "error"
        }


def storyboard_node(state: GameState) -> GameState:
    """
    分镜脚本生成节点
    根据剧情生成视频分镜脚本
    """
    try:
        latest_story = state.get("latest_story")
        if not latest_story:
            return {
                **state,
                "error": "未找到最新剧情",
                "current_step": "error"
            }
        
        # 构建提示词
        prompt = STORYBOARD_PROMPT.format(story=latest_story)
        
        # 调用LLM生成分镜脚本（非流式版本）
        response = DEEPSEEK.invoke([HumanMessage(content=prompt)])
        storyboard_text = response.content
        
        # 提取并修复JSON
        cleaned_text, storyboard_data = extract_and_fix_json(storyboard_text)
        
        if not storyboard_data:
            return {
                **state,
                "error": f"分镜脚本JSON解析失败\n原始内容前500字符: {storyboard_text[:500]}\n\n请尝试重新输入。",
                "current_step": "error"
            }
        
        shots = storyboard_data.get("shots", [])
        if not shots:
            return {
                **state,
                "error": "分镜脚本中未找到有效的分镜数据",
                "current_step": "error"
            }
        
        # 保存分镜脚本
        storyboard_index = get_next_story_index()
        save_storyboard(json.dumps(storyboard_data, ensure_ascii=False), storyboard_index)
        
        # 更新状态
        return {
            **state,
            "storyboard": cleaned_text or storyboard_text,
            "storyboard_shots": shots,
            "current_step": "extract_frame",
            "error": None,
            "messages": state["messages"] + [AIMessage(content=f"分镜脚本已生成，共{len(shots)}个分镜")]
        }
    except Exception as e:
        return {
            **state,
            "error": f"分镜脚本生成失败: {str(e)}",
            "current_step": "error"
        }

