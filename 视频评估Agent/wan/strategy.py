# -*- coding: utf-8 -*-
"""
阿里万象视频生成策略实现
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


class WanStrategy(VideoGenerationStrategy):
    """阿里万象视频生成策略"""
    
    def __init__(self):
        """初始化万象策略"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("未找到DASHSCOPE_API_KEY环境变量")
    
    def _encode_image_to_data_url(self, image_path: str) -> str:
        """将图片编码为data URL格式"""
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/png;base64,{image_base64}"
    
    def generate_video(
        self, 
        prompt: str, 
        reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
            headers = {
                "X-DashScope-Async": "enable",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "wan2.5-i2v-preview",
                "input": {"prompt": prompt},
                "parameters": {
                    "resolution": "720P",
                    "duration": 10,
                    "audio": True,
                },
            }
            
            if reference_image_path:
                try:
                    image_url = self._encode_image_to_data_url(reference_image_path)
                    payload["input"]["img_url"] = image_url
                except Exception as e:
                    print(f"警告: 图片编码失败，将不使用参考图片: {e}")
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("output", {}).get("task_id")
                if task_id:
                    return {
                        "video_id": task_id,
                        "status": "pending",
                        "error": None
                    }
                else:
                    return {
                        "video_id": None,
                        "status": "failed",
                        "error": "未返回任务ID"
                    }
            else:
                return {
                    "video_id": None,
                    "status": "failed",
                    "error": f"创建任务失败: {response.status_code}, {response.text}"
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
            url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{video_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                output = result.get("output", {})
                task_status = output.get("task_status")
                
                if task_status == "SUCCEEDED":
                    video_url = output.get("video_url")
                    return {
                        "status": "completed",
                        "video_url": video_url,
                        "error": None
                    }
                elif task_status == "FAILED":
                    message = output.get("message", "未知错误")
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": f"任务失败: {message}"
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
                    "error": f"查询失败: {response.status_code}, {response.text}"
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
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                print(f"下载视频失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"下载视频失败: {e}")
            return False

