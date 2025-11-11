# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/11 14:00
@Author  : ZhangShenao
@File    : fusion_video.py
@Desc    : 多主体参考生成视频
"""

import os
import time
import uuid
import requests
import dotenv
from pathlib import Path
from typing import Dict, Optional, Any

# 加载环境变量
dotenv.load_dotenv()

# PixVerse API配置
API_BASE_URL = "https://app-api.pixverse.ai"
API_KEY = os.getenv("PIXVERSE_API_KEY")
if not API_KEY:
    raise ValueError("请设置环境变量 PIXVERSE_API_KEY")

prompt = """
@role and @char are fighting. @role jumps up and punches, while @char pulls out his sword as he steps back.
Use English for all dialogue in the video.
The video should include more than two distinct camera shots or scene transitions.
"""


def upload_image(image_path: str, trace_id: str) -> Optional[int]:
    """
    上传图片到PixVerse并返回img_id

    Args:
        image_path: 图片文件路径
        trace_id: 追踪ID

    Returns:
        图片ID，失败返回None
    """
    try:
        url = f"{API_BASE_URL}/openapi/v2/image/upload"
        headers = {
            "API-KEY": API_KEY,
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
                        if image_path.endswith(".jpeg") or image_path.endswith(".jpg")
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
                print(f"成功上传图片 {image_path}, img_id: {img_id}")
                return int(img_id)
            else:
                print(f"警告: 上传成功但未找到img_id，响应: {result}")
                return None
        else:
            print(f"上传图片失败: HTTP {response.status_code}, 响应: {response.text}")
            return None
    except Exception as e:
        print(f"上传图片异常: {e}")
        return None


def generate_video(
    image_references: list,
    prompt: str,
    trace_id: str,
    model: str = "v4.5",
    duration: int = 5,
    quality: str = "540p",
    aspect_ratio: str = "16:9",
    seed: Optional[int] = None,
) -> Optional[str]:
    """
    调用Fusion API生成视频

    Args:
        image_references: 图片引用列表，格式: [{"type": "subject", "img_id": 0, "ref_name": "char"}, ...]
        prompt: 视频生成提示词
        trace_id: 追踪ID
        model: 模型版本
        duration: 视频时长（秒）
        quality: 视频质量
        aspect_ratio: 宽高比
        seed: 随机种子

    Returns:
        视频任务ID，失败返回None
    """
    try:
        url = f"{API_BASE_URL}/openapi/v2/video/fusion/generate"
        headers = {
            "API-KEY": API_KEY,
            "Ai-trace-id": trace_id,
            "Content-Type": "application/json",
        }

        payload = {
            "image_references": image_references,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "sound_effect_switch": True,
            "lip_sync_switch": True,
        }

        if seed is not None:
            payload["seed"] = seed

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            err_code = result.get("ErrCode", -1)

            if err_code != 0:
                print(
                    f"提交视频生成任务失败: ErrCode={err_code}, ErrMsg={result.get('ErrMsg', '')}"
                )
                return None

            resp = result.get("Resp", {})
            video_id = resp.get("video_id")
            credits = resp.get("credits")

            if video_id is not None:
                credits_info = f", credits: {credits}" if credits else ""
                print(f"成功提交视频生成任务, video_id: {video_id}{credits_info}")
                return str(video_id)
            else:
                print(f"警告: 提交成功但未找到video_id，响应: {result}")
                return None
        else:
            print(
                f"提交视频生成任务失败: HTTP {response.status_code}, 响应: {response.text}"
            )
            return None
    except Exception as e:
        print(f"提交视频生成任务异常: {e}")
        return None


def get_video_status(video_id: str, trace_id: str) -> Dict[str, Any]:
    """
    获取视频生成状态

    Args:
        video_id: 视频任务ID
        trace_id: 追踪ID

    Returns:
        状态字典，包含status、video_url、error等信息
    """
    try:
        url = f"{API_BASE_URL}/openapi/v2/video/result/{video_id}"
        headers = {
            "API-KEY": API_KEY,
            "Ai-trace-id": trace_id,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            data = result.get("Resp", {})
            status_code = data.get("status")
            video_url = data.get("url")

            if status_code == 1:
                return {"status": "completed", "video_url": video_url, "error": None}
            elif status_code == 5:
                return {"status": "processing", "video_url": None, "error": None}
            elif status_code == 7:
                return {"status": "failed", "video_url": None, "error": "内容审核失败"}
            elif status_code == 8:
                return {"status": "failed", "video_url": None, "error": "视频生成失败"}
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


def download_video(video_url: str, save_path: str) -> bool:
    """
    下载视频到本地

    Args:
        video_url: 视频下载URL
        save_path: 保存路径

    Returns:
        是否下载成功
    """
    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"视频下载成功: {save_path}")
            return True
        else:
            print(f"下载视频失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"下载视频异常: {e}")
        return False


def wait_for_video_completion(
    video_id: str, trace_id: str, max_wait_time: int = 600, poll_interval: int = 5
) -> Optional[str]:
    """
    等待视频生成完成

    Args:
        video_id: 视频任务ID
        trace_id: 追踪ID
        max_wait_time: 最大等待时间（秒）
        poll_interval: 轮询间隔（秒）

    Returns:
        视频URL，失败返回None
    """
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        status_result = get_video_status(video_id, trace_id)
        status = status_result.get("status")

        if status == "completed":
            video_url = status_result.get("video_url")
            if video_url:
                print(f"视频生成完成！视频URL: {video_url}")
                return video_url
            else:
                print("警告: 状态显示完成但未找到视频URL")
                return None
        elif status == "failed":
            error = status_result.get("error", "视频生成失败")
            print(f"视频生成失败: {error}")
            return None
        else:
            # 处理中，继续等待
            elapsed = int(time.time() - start_time)
            print(f"视频生成中... (已等待 {elapsed} 秒)")
            time.sleep(poll_interval)

    print(f"等待超时（超过 {max_wait_time} 秒）")
    return None


def main():
    """主函数：执行完整的视频生成流程"""
    # 生成追踪ID
    trace_id = str(uuid.uuid4())
    print(f"开始视频生成流程，追踪ID: {trace_id}")

    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    char_image_path = current_dir / "char.png"
    role_image_path = current_dir / "role.png"

    # 步骤1: 上传两张图片
    print("\n=== 步骤1: 上传参考图片 ===")
    char_img_id = upload_image(str(char_image_path), trace_id)
    role_img_id = upload_image(str(role_image_path), trace_id)

    if char_img_id is None or role_img_id is None:
        print("错误: 图片上传失败，无法继续")
        return

    # 步骤2: 调用Fusion API生成视频
    print("\n=== 步骤2: 提交视频生成任务 ===")
    image_references = [
        {"type": "subject", "img_id": char_img_id, "ref_name": "char"},
        {"type": "subject", "img_id": role_img_id, "ref_name": "role"},
    ]

    video_id = generate_video(
        image_references=image_references,
        prompt=prompt.strip(),
        trace_id=trace_id,
        model="v5",
        duration=8,
        quality="720p",
        aspect_ratio="9:16",
    )

    if video_id is None:
        print("错误: 提交视频生成任务失败")
        return

    # 步骤3: 等待视频生成完成
    print("\n=== 步骤3: 等待视频生成完成 ===")
    video_url = wait_for_video_completion(
        video_id, trace_id, max_wait_time=600, poll_interval=5
    )

    if video_url is None:
        print("错误: 视频生成失败或超时")
        return

    # 步骤4: 下载视频
    print("\n=== 步骤4: 下载视频 ===")
    output_path = current_dir / f"generated_video_{int(time.time())}.mp4"
    success = download_video(video_url, str(output_path))

    if success:
        print(f"\n✅ 视频生成完成并已保存到: {output_path}")
    else:
        print("\n❌ 视频下载失败")


if __name__ == "__main__":
    main()
