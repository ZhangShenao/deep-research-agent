# -*- coding: utf-8 -*-
"""
Sora2视频生成客户端
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Sora2Client:
    """Sora2视频生成客户端"""

    def __init__(self):
        """初始化Sora2客户端"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_video(
        self, prompt: str, reference_image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成视频"""
        try:
            # 构建API调用参数
            create_params = {
                "prompt": prompt,
                "seconds": "8",
                "size": "720x1280",
            }

            # 如果找到参考图片，添加到参数中
            image_file = None
            try:
                if reference_image_path:
                    image_file = open(reference_image_path, "rb")
                    create_params["input_reference"] = image_file

                video = self.client.videos.create(**create_params)
                video_id = video.id

                return {"video_id": video_id, "status": "pending", "error": None}
            finally:
                # 确保文件总是被关闭
                if image_file:
                    image_file.close()
        except Exception as e:
            return {
                "video_id": None,
                "status": "failed",
                "error": f"创建任务失败: {str(e)}",
            }

    def poll_status(self, video_id: str) -> Dict[str, Any]:
        """轮询视频生成状态"""
        try:
            video = self.client.videos.retrieve(video_id)
            status = video.status

            if status == "completed":
                # 获取视频URL（OpenAI API需要下载）
                return {
                    "status": "completed",
                    "video_url": f"openai_video:{video_id}",  # 特殊标记
                    "error": None,
                }
            elif status == "failed":
                error_msg = getattr(video, "error", None)
                return {
                    "status": "failed",
                    "video_url": None,
                    "error": f"视频生成失败: {error_msg or '未知错误'}",
                }
            else:
                return {"status": "processing", "video_url": None, "error": None}
        except Exception as e:
            return {
                "status": "failed",
                "video_url": None,
                "error": f"获取结果失败: {str(e)}",
            }

    def download_video(self, video_url: str, save_path: str) -> bool:
        """下载视频"""
        try:
            # 检查是否是OpenAI视频的特殊标记
            if video_url.startswith("openai_video:"):
                video_id = video_url.replace("openai_video:", "")
                response = self.client.videos.download_content(video_id=video_id)
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                response.write_to_file(file=save_path)
                return True
            else:
                # 普通URL下载
                import requests

                response = requests.get(video_url)
                if response.status_code == 200:
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    return True
                return False
        except Exception as e:
            print(f"下载视频失败: {e}")
            return False
