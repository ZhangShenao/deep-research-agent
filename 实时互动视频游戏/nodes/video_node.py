# -*- coding: utf-8 -*-
"""
视频生成节点
"""
import sys
import time
from pathlib import Path
from langchain_core.messages import AIMessage

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from state import GameState
from sora2_client import Sora2Client
from utils import get_next_video_index, ensure_data_dir


def video_generation_node(state: GameState) -> GameState:
    """
    视频生成节点
    根据分镜脚本生成视频
    """
    try:
        storyboard_shots = state.get("storyboard_shots")
        if not storyboard_shots:
            return {
                **state,
                "error": "未找到分镜脚本",
                "current_step": "error"
            }
        
        # 获取参考图片
        reference_image_path = state.get("reference_image_path")
        
        # 构建视频生成的prompt（合并所有分镜描述）
        shot_descriptions = []
        for shot in storyboard_shots:
            desc = shot.get("description", "")
            camera = shot.get("camera_movement", "")
            style = shot.get("style", "暗黑系RPG风格")
            shot_descriptions.append(f"{desc}，{camera}，{style}")
        
        video_prompt = "，".join(shot_descriptions)
        # 添加总体风格描述和内容限制
        video_prompt = f"暗黑系RPG游戏风格，{video_prompt}，8秒视频，流畅连贯，适合全年龄，无暴力血腥内容，安全健康，所有声音和对话均使用中文，人物对话为中文，旁白为中文"
        
        # 初始化Sora2客户端
        sora2_client = Sora2Client()
        
        # 生成视频
        result = sora2_client.generate_video(video_prompt, reference_image_path)
        
        if result["status"] == "failed":
            return {
                **state,
                "error": result.get("error", "视频生成失败"),
                "current_step": "error"
            }
        
        video_id = result["video_id"]
        
        # 轮询视频生成状态
        max_attempts = 120  # 最多轮询120次（20分钟）
        poll_interval = 10  # 每10秒轮询一次
        
        for attempt in range(max_attempts):
            status_result = sora2_client.poll_status(video_id)
            status = status_result["status"]
            
            if status == "completed":
                # 视频生成完成，下载视频
                session_id = state.get("session_id", "default")
                video_index = get_next_video_index(session_id)
                ensure_data_dir(session_id)
                video_path = str(Path(__file__).parent.parent / "data" / session_id / "videos" / f"video_{video_index:04d}.mp4")
                
                success = sora2_client.download_video(status_result["video_url"], video_path)
                
                if success:
                    return {
                        **state,
                        "video_path": video_path,
                        "current_step": "completed",
                        "error": None,
                        "messages": state["messages"] + [AIMessage(content="视频已生成完成！")]
                    }
                else:
                    return {
                        **state,
                        "error": "视频下载失败",
                        "current_step": "error"
                    }
            elif status == "failed":
                return {
                    **state,
                    "error": status_result.get("error", "视频生成失败"),
                    "current_step": "error"
                }
            else:
                # 仍在处理中，等待后继续轮询
                # 注意：在Streamlit中，这里会阻塞，但这是必要的等待
                time.sleep(poll_interval)
        
        # 超时
        return {
            **state,
            "error": "视频生成超时（超过20分钟）",
            "current_step": "error"
        }
        
    except Exception as e:
        return {
            **state,
            "error": f"视频生成失败: {str(e)}",
            "current_step": "error"
        }

