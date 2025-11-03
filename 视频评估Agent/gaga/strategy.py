# -*- coding: utf-8 -*-
"""
Gaga视频生成策略实现
"""
import os
from typing import Dict, Any, Optional
import requests

import dotenv

dotenv.load_dotenv()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_strategy import VideoGenerationStrategy


class GagaStrategy(VideoGenerationStrategy):
    """Gaga视频生成策略"""

    def __init__(self):
        """初始化Gaga策略"""
        self.api_key = os.getenv("GAGA_API_KEY")
        if not self.api_key:
            raise ValueError("未找到GAGA_API_KEY环境变量")

        self.base_url = os.getenv("GAGA_BASE_URL")

    def upload_asset(self, file_path: str) -> Dict[str, Any]:
        """
        上传资源文件到 Gaga API

        Args:
            file_path: 本地文件路径

        Returns:
            dict: 包含资源 ID 等信息的响应数据
        """
        try:
            with open(file_path, "rb") as f:
                res = requests.post(
                    f"{self.base_url}/v1/assets",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": f},
                )
            res.raise_for_status()
            return res.json()
        except Exception as e:
            raise ValueError(f"上传资源失败: {e}")

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        获取指定资源的详细信息

        Args:
            asset_id: 资源 ID

        Returns:
            dict: 资源的详细信息
        """
        try:
            res = requests.get(
                f"{self.base_url}/v1/assets/{asset_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            res.raise_for_status()
            return res.json()
        except Exception as e:
            raise ValueError(f"获取资源信息失败: {e}")

    def generate_video(
        self, prompt: str, reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            asset_id = None

            # 如果提供了参考图片，先上传
            if reference_image_path:
                try:
                    upload_res = self.upload_asset(reference_image_path)
                    asset_id = upload_res.get("id")
                    if asset_id:
                        print(f"图片上传成功，资源ID: {asset_id}")
                    else:
                        print(f"警告: 上传响应中未找到资源ID")
                        asset_id = None
                except Exception as e:
                    print(f"警告: 图片上传失败，将不使用参考图片: {e}")
                    asset_id = None

            # 生成视频
            payload = {
                "model": "performer",  # 使用 performer 模型
                "resolution": "720p",  # 视频分辨率
                "aspectRatio": "9:16",  # 视频宽高比
                "chunks": [
                    {
                        "duration": 8,  # 视频时长（秒）
                        "conditions": [
                            {
                                "type": "text",
                                "content": prompt,  # 文本提示词
                            },
                        ],
                        "enablePromptEnhancement": False,  # 启用提示词增强
                    }
                ],
            }

            # 如果有图片资源，添加到source中
            if asset_id:
                payload["source"] = {"type": "image", "content": asset_id}

            res = requests.post(
                f"{self.base_url}/v1/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            res.raise_for_status()
            result = res.json()

            generation_id = result.get("id")
            if not generation_id:
                return {
                    "video_id": None,
                    "status": "failed",
                    "error": "未返回生成任务ID",
                }

            return {"video_id": generation_id, "status": "pending", "error": None}
        except Exception as e:
            return {
                "video_id": None,
                "status": "failed",
                "error": f"创建任务失败: {str(e)}",
            }

    def poll_status(self, video_id: str) -> Dict[str, Any]:
        """轮询视频生成状态"""
        try:
            res = requests.get(
                f"{self.base_url}/v1/generations/{video_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            res.raise_for_status()
            result = res.json()

            status = result.get("status")

            if status == "Success":
                # 查找视频URL，尝试多种可能的响应结构
                video_url = result.get("resultVideoURL")

                if video_url:
                    return {
                        "status": "completed",
                        "video_url": video_url,
                        "error": None,
                    }
                else:
                    # 如果找不到视频URL，打印调试信息
                    print(f"调试: 未找到视频URL，响应结构: {result}")
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": "视频生成成功但未找到视频URL",
                    }
            elif status == "Failed" or status == "Error":
                error_msg = result.get("error") or result.get("message", "未知错误")
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": f"视频生成失败: {error_msg}",
                }
            else:
                # Processing, Pending 等状态
                return {"status": "processing", "video_url": None, "error": None}
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"轮询失败: {str(e)}",
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
