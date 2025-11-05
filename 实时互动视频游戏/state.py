# -*- coding: utf-8 -*-
"""
LangGraph状态管理
"""
from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages


class GameState(TypedDict):
    """
    游戏状态定义
    """
    session_id: str  # 会话ID，用于数据隔离
    messages: Annotated[list, add_messages]  # 对话历史
    story_context: str  # 当前故事背景和上下文
    latest_story: Optional[str]  # 最新续写的剧情
    storyboard: Optional[str]  # 分镜脚本
    storyboard_shots: Optional[list]  # 分镜列表（每个分镜的详细描述）
    reference_image_path: Optional[str]  # 参考图片路径（上一段视频的最后一帧）
    video_path: Optional[str]  # 生成的视频路径
    last_video_id: Optional[str]  # 上一次生成的视频ID（用于remix）
    current_step: str  # 当前执行的步骤（story_continuation, storyboard, extract_frame, video_generation）
    error: Optional[str]  # 错误信息

