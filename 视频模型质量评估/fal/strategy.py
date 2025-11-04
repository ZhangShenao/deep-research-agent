# -*- coding: utf-8 -*-
"""
Fal视频生成策略实现
"""
import os
import base64
from typing import Dict, Any, Optional
import requests

import dotenv
dotenv.load_dotenv()

import fal_client

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_strategy import VideoGenerationStrategy


class FalStrategy(VideoGenerationStrategy):
    """Fal视频生成策略"""
    
    def __init__(self):
        """初始化Fal策略"""
        pass
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            raise ValueError(f"编码图片失败: {e}")
    
    def generate_video(
        self, 
        prompt: str, 
        reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            # 构建API调用参数
            create_params = {
                "prompt": prompt,
                "resolution": "720p",
                "aspect_ratio": "9:16",
                "duration": 8,
            }
            
            # 如果找到参考图片，添加到参数中
            if reference_image_path:
                try:
                    image_url = self.encode_image_to_base64(reference_image_path)
                    create_params["image_url"] = image_url
                except Exception as e:
                    print(f"警告: 图片编码失败，将不使用参考图片: {e}")
            
            # 提交视频生成任务
            handler = fal_client.submit(
                "fal-ai/sora-2/image-to-video",
                arguments=create_params,
            )
            
            request_id = handler.request_id
            return {
                "video_id": request_id,
                "status": "pending",
                "error": None
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
            fal_result = fal_client.result(
                "fal-ai/sora-2/image-to-video", 
                video_id
            )
            
            if fal_result and "video" in fal_result:
                video_url = fal_result["video"]["url"]
                return {
                    "status": "completed",
                    "video_url": video_url,
                    "error": None
                }
            else:
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": "视频生成失败: 未返回有效结果"
                }
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"获取结果失败: {str(e)}"
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

