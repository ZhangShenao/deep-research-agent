# -*- coding: utf-8 -*-
"""
图片抽取节点
"""
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from state import GameState
from utils import extract_last_frame


def extract_frame_node(state: GameState) -> GameState:
    """
    图片抽取节点
    从上一段视频中提取最后一帧作为参考图片
    """
    try:
        # 检查是否有上一段视频
        previous_video_path = state.get("video_path")
        
        if previous_video_path and Path(previous_video_path).exists():
            # 提取最后一帧
            session_id = state.get("session_id", "default")
            reference_image_path = extract_last_frame(previous_video_path, session_id=session_id)
            
            if reference_image_path:
                return {
                    **state,
                    "reference_image_path": reference_image_path,
                    "current_step": "video_generation",
                    "error": None,
                }
            else:
                # 如果提取失败，继续使用None（不使用参考图片）
                return {
                    **state,
                    "reference_image_path": None,
                    "current_step": "video_generation",
                    "error": None,
                }
        else:
            # 没有上一段视频，不使用参考图片
            return {
                **state,
                "reference_image_path": None,
                "current_step": "video_generation",
                "error": None,
            }
    except Exception as e:
        return {
            **state,
            "error": f"图片抽取失败: {str(e)}",
            "current_step": "error"
        }

