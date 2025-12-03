# -*- coding: utf-8 -*-
"""
PixVerse V5.5 视频生成策略实现
"""
import os
import uuid
from typing import Dict, Any, Optional
import requests

import dotenv

dotenv.load_dotenv()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_strategy import VideoGenerationStrategy


class PixVerseV55Strategy(VideoGenerationStrategy):
    """PixVerse V5.5 视频生成策略"""

    def __init__(self):
        """初始化PixVerse V5.5策略"""
        self.api_key = os.getenv("PIXVERSE_API_KEY")
        if not self.api_key:
            raise ValueError("未找到PIXVERSE_API_KEY环境变量")

        self.api_base_url = "https://app-api.pixverse.ai"
        # 存储 video_id 到 trace_id 的映射，用于轮询状态
        self._trace_ids: Dict[str, str] = {}

    def upload_image(self, image_path: str, trace_id: str) -> Optional[int]:
        """
        上传图片到PixVerse并返回img_id

        Args:
            image_path: 图片文件路径
            trace_id: 追踪ID

        Returns:
            图片ID，失败返回None
        """
        try:
            url = f"{self.api_base_url}/openapi/v2/image/upload"
            headers = {
                "API-KEY": self.api_key,
                "Ai-trace-id": trace_id,
            }

            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"错误: 图片文件不存在: {image_path}")
                return None

            # 上传图片（使用form-data格式）
            with open(image_path, "rb") as f:
                files = {
                    "image": (
                        os.path.basename(image_path),
                        f,
                        (
                            "image/jpeg"
                            if image_path.endswith(".jpeg")
                            or image_path.endswith(".jpg")
                            else "image/png"
                        ),
                    )
                }
                response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                result = response.json()
                err_code = result.get("ErrCode", -1)

                if err_code != 0:
                    print(
                        f"上传图片失败: ErrCode={err_code}, ErrMsg={result.get('ErrMsg', '')}"
                    )
                    return None

                img_id = result.get("Resp", {}).get("img_id")
                if img_id is not None:
                    return int(img_id)
                else:
                    print(f"警告: 上传成功但未找到img_id，响应: {result}")
                    return None
            else:
                print(
                    f"上传图片失败: HTTP {response.status_code}, 响应: {response.text}"
                )
                return None
        except Exception as e:
            print(f"上传图片异常: {e}")
            return None

    def generate_video(
        self, prompt: str, reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 视频生成的prompt
            reference_image_path: 参考图片路径（可选）

        Returns:
            包含以下字段的字典：
            - video_id: 视频任务ID（用于轮询）
            - status: 初始状态（通常是"pending"）
            - error: 错误信息（如果有）
        """
        try:
            # 生成追踪ID
            trace_id = str(uuid.uuid4())

            # 如果提供了参考图片，先上传获取img_id
            img_id = None
            if reference_image_path:
                img_id = self.upload_image(reference_image_path, trace_id)
                if img_id is None:
                    return {
                        "video_id": None,
                        "status": "failed",
                        "error": "图片上传失败",
                    }

            # 调用视频生成API
            url = f"{self.api_base_url}/openapi/v2/video/img/generate"
            headers = {
                "API-KEY": self.api_key,
                "Ai-trace-id": trace_id,
                "Content-Type": "application/json",
            }

            payload = {
                "prompt": prompt,
                "model": "v5.5",
                "duration": 10,
                "quality": "720p",
                "generate_audio_switch": True,
                "generate_multi_clip_switch": True,
                "thinking_type": "auto",
            }

            # 如果上传了图片，添加img_id
            if img_id is not None:
                payload["img_id"] = img_id

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                err_code = result.get("ErrCode", -1)

                if err_code != 0:
                    return {
                        "video_id": None,
                        "status": "failed",
                        "error": f"提交任务失败: ErrCode={err_code}, ErrMsg={result.get('ErrMsg', '')}",
                    }

                resp = result.get("Resp", {})
                video_id = resp.get("video_id")

                if video_id is not None:
                    video_id_str = str(video_id)
                    # 保存trace_id到字典中，用于后续轮询
                    self._trace_ids[video_id_str] = trace_id
                    return {
                        "video_id": video_id_str,
                        "status": "pending",
                        "error": None,
                    }
                else:
                    return {
                        "video_id": None,
                        "status": "failed",
                        "error": "提交成功但未找到video_id",
                    }
            else:
                return {
                    "video_id": None,
                    "status": "failed",
                    "error": f"提交任务失败: HTTP {response.status_code}, {response.text}",
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

        Args:
            video_id: 视频任务ID

        Returns:
            包含以下字段的字典：
            - status: 状态（"completed", "failed", "processing"等）
            - video_url: 视频URL（如果生成完成）
            - error: 错误信息（如果失败）
        """
        try:
            # 获取保存的trace_id，如果没有则生成新的（理论上不应该发生）
            trace_id = self._trace_ids.get(video_id, str(uuid.uuid4()))

            url = f"{self.api_base_url}/openapi/v2/video/result/{video_id}"
            headers = {
                "API-KEY": self.api_key,
                "Ai-trace-id": trace_id,
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                result = response.json()
                data = result.get("Resp", {})
                status_code = data.get("status")
                video_url = data.get("url")

                if status_code == 1:
                    return {
                        "status": "completed",
                        "video_url": video_url,
                        "error": None,
                    }
                elif status_code == 5:
                    return {"status": "processing", "video_url": None, "error": None}
                elif status_code == 7:
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": "内容审核失败",
                    }
                elif status_code == 8:
                    return {
                        "status": "failed",
                        "video_url": None,
                        "error": "视频生成失败",
                    }
                else:
                    return {"status": "processing", "video_url": None, "error": None}
            else:
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": f"获取状态失败: HTTP {response.status_code}, {response.text}",
                }
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"获取状态异常: {str(e)}",
            }

    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        下载视频

        Args:
            video_url: 视频URL
            save_path: 保存路径

        Returns:
            是否下载成功
        """
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

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
