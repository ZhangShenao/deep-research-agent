# -*- coding: utf-8 -*-
"""
LTX-2视频生成策略实现
"""
import os
import base64
import tempfile
import shutil
from typing import Dict, Any, Optional
import requests

import dotenv

dotenv.load_dotenv()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_strategy import VideoGenerationStrategy


class LTX2Strategy(VideoGenerationStrategy):
    """LTX-2视频生成策略"""

    def __init__(self):
        """初始化LTX-2策略"""
        self.api_key = os.getenv("LTX_API_KEY")
        if not self.api_key:
            raise ValueError("未找到LTX_API_KEY环境变量")

        self.api_url = "https://api.ltx.video/v1/image-to-video"
        # 用于存储临时文件的字典，key为video_id（临时文件路径），value为文件路径
        self.temp_files = {}

    def _encode_image_to_data_url(self, image_path: str) -> str:
        """将图片编码为data URL格式"""
        try:
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                # 检测图片格式
                ext = os.path.splitext(image_path)[1].lower()
                mime_type = "image/png" if ext == ".png" else "image/jpeg"
                return f"data:{mime_type};base64,{image_base64}"
        except Exception as e:
            raise ValueError(f"编码图片失败: {e}")

    def _upload_image_to_url(self, image_path: str) -> Optional[str]:
        """
        将图片转换为可用的URI格式

        注意：LTX-2 API文档中image_uri示例是HTTP URL。
        如果API不支持base64 data URL格式，可能需要：
        1. 先上传图片到图床服务（如imgur、cloudinary等）获取公网URL
        2. 或者使用文件上传API先上传图片，再使用返回的URL

        目前先尝试base64 data URL格式（许多API都支持），
        如果遇到错误，请修改此方法或使用图片托管服务。
        """
        # 先尝试使用base64 data URL，如果API不支持，再考虑上传到图床
        return self._encode_image_to_data_url(image_path)

    def generate_video(
        self, prompt: str, reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成视频

        注意：LTX-2 API是同步的，直接返回MP4文件。
        为了兼容现有的异步框架，我们将视频保存到临时文件，
        返回临时文件路径作为video_id（带特殊前缀）。
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "prompt": prompt,
                "model": "ltx-2-fast",
                "duration": 8,
                "resolution": "1920x1080",
                "fps": 25,
                "generate_audio": True,
            }

            # 处理参考图片
            if reference_image_path:
                try:
                    # 尝试使用base64 data URL格式
                    # 如果API不支持，可能需要先上传到图床服务
                    image_uri = self._upload_image_to_url(reference_image_path)
                    payload["image_uri"] = image_uri
                except Exception as e:
                    print(f"警告: 图片处理失败，将不使用参考图片: {e}")

            # 调用API（同步调用，直接返回MP4文件）
            response = requests.post(
                self.api_url, headers=headers, json=payload, stream=True
            )

            if response.status_code == 200:
                # API直接返回MP4文件，保存到临时文件
                temp_dir = None
                if reference_image_path and os.path.dirname(reference_image_path):
                    temp_dir = os.path.dirname(reference_image_path)
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp4", dir=temp_dir
                )
                temp_file_path = temp_file.name
                temp_file.close()

                # 写入视频内容
                with open(temp_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # 使用特殊前缀标记这是已完成的临时文件
                video_id = f"ltx2_temp:{temp_file_path}"
                self.temp_files[video_id] = temp_file_path

                return {
                    "video_id": video_id,
                    "status": "pending",  # 返回pending，在poll_status中检查时立即返回completed
                    "error": None,
                }
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", {}).get("message", error_msg)
                except:
                    pass

                return {
                    "video_id": None,
                    "status": "failed",
                    "error": f"API调用失败: HTTP {response.status_code}, {error_msg}",
                }

        except Exception as e:
            return {
                "video_id": None,
                "status": "failed",
                "error": f"创建任务失败: {str(e)}",
            }

    def poll_status(self, video_id: str) -> Dict[str, Any]:
        """
        轮询视频生成状态

        注意：LTX-2 API是同步的，所以如果video_id是临时文件标记，
        直接返回已完成状态。
        """
        try:
            # 检查是否是已完成的临时文件
            if video_id.startswith("ltx2_temp:"):
                temp_file_path = video_id.replace("ltx2_temp:", "")
                if os.path.exists(temp_file_path):
                    return {
                        "status": "completed",
                        "video_url": temp_file_path,  # 返回临时文件路径
                        "error": None,
                    }
                else:
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": "临时文件不存在",
                    }
            else:
                # 不应该到这里，但为了安全起见
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": f"无效的video_id: {video_id}",
                }
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"轮询失败: {str(e)}",
            }

    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        下载视频

        如果video_url是本地文件路径（临时文件），直接复制；
        如果是网络URL，则下载。
        """
        try:
            # 检查是否是本地文件路径
            if os.path.exists(video_url):
                # 是本地文件，直接复制
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                shutil.copy2(video_url, save_path)

                # 清理临时文件
                try:
                    if video_url in self.temp_files.values():
                        os.remove(video_url)
                except:
                    pass  # 忽略清理错误

                return True
            else:
                # 是网络URL，下载
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
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
