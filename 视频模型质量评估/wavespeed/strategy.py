# -*- coding: utf-8 -*-
"""
WaveSpeed视频生成策略实现
"""
import os
import json
import base64
from typing import Dict, Any, Optional
import requests

import dotenv
dotenv.load_dotenv()

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_strategy import VideoGenerationStrategy


class WaveSpeedStrategy(VideoGenerationStrategy):
    """WaveSpeed视频生成策略"""
    
    def __init__(self):
        """初始化WaveSpeed策略"""
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        if not self.api_key:
            raise ValueError("未找到WAVESPEED_API_KEY环境变量")
    
    def generate_video(
        self, 
        prompt: str, 
        reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            url = "https://api.wavespeed.ai/api/v3/openai/sora-2/image-to-video"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            
            payload = {
                "size": "720*1280", 
                "duration": 8, 
                "prompt": prompt
            }
            
            if reference_image_path:
                try:
                    with open(reference_image_path, "rb") as image_file:
                        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                        payload["image"] = image_base64
                except Exception as e:
                    print(f"警告: 图片编码失败，将不使用参考图片: {e}")
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                api_result = response.json()["data"]
                request_id = api_result["id"]
                return {
                    "video_id": request_id,
                    "status": "pending",
                    "error": None
                }
            else:
                return {
                    "video_id": None,
                    "status": "failed",
                    "error": f"提交任务失败: {response.status_code}, {response.text}"
                }
        except Exception as e:
            return {
                "video_id": None,
                "status": "failed",
                "error": f"创建任务失败: {str(e)}"
            }
    
    def poll_status(self, video_id: str) -> Dict[str, Any]:
        """轮询视频生成状态"""
        try:
            poll_url = f"https://api.wavespeed.ai/api/v3/predictions/{video_id}/result"
            poll_headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(poll_url, headers=poll_headers)
            if response.status_code == 200:
                api_result = response.json()["data"]
                status = api_result["status"]
                
                if status == "completed":
                    video_url = api_result["outputs"][0]
                    return {
                        "status": "completed",
                        "video_url": video_url,
                        "error": None
                    }
                elif status == "failed":
                    error_msg = api_result.get("error", "未知错误")
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": f"视频生成失败: {error_msg}"
                    }
                else:
                    return {
                        "status": "processing",
                        "video_url": None,
                        "error": None
                    }
            else:
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": f"轮询状态失败: {response.status_code}, {response.text}"
                }
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"轮询失败: {str(e)}"
            }
    
    def download_video(self, video_url: str, save_path: str) -> bool:
        """下载视频"""
        try:
            response = requests.get(video_url)
            if response.status_code == 200:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"下载视频失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"下载视频失败: {e}")
            return False

