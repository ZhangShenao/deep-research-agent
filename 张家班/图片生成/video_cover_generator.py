# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/08
@Author  : ZhangShenao
@File    : video_cover_generator.py
@Desc    : 基于视频关键帧生成封面图

功能：
1. 从本地视频提取关键帧（每2秒一帧 + 场景变化检测）
2. 将关键帧作为参考图像传给 gemini-3-pro-image-preview
3. 生成符合视频剧情的封面图
"""

import cv2
import numpy as np
from PIL import Image
from google import genai
from google.genai import types
import os
import subprocess
import tempfile
from dotenv import load_dotenv
from typing import List, Tuple
import io

# 加载环境变量
load_dotenv()

# 初始化Gemini客户端
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def detect_scene_change(
    frame1: np.ndarray, frame2: np.ndarray, threshold: float = 0.5
) -> bool:
    """
    检测两帧之间是否发生场景变化
    使用颜色直方图相关性比较

    Args:
        frame1: 第一帧图像 (BGR格式)
        frame2: 第二帧图像 (BGR格式)
        threshold: 相关性阈值，低于此值认为发生场景变化

    Returns:
        bool: 是否发生场景变化
    """
    # 计算两帧的颜色直方图
    hist1 = cv2.calcHist([frame1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([frame2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    # 归一化直方图
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    # 计算相关性
    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return correlation < threshold


def extract_keyframes(
    video_path: str,
    interval_seconds: float = 2.0,
    scene_change_threshold: float = 0.5,
    max_frames: int = 9,
    save_keyframes: bool = False,
    output_dir: str = "keyframes",
) -> List[Image.Image]:
    """
    从视频中提取关键帧
    结合均匀采样和场景变化检测两种策略

    Args:
        video_path: 视频文件路径
        interval_seconds: 均匀采样间隔（秒）
        scene_change_threshold: 场景变化检测阈值
        max_frames: 最大关键帧数量（gemini-3-pro-image-preview 最多支持9张参考图）
        save_keyframes: 是否保存提取的关键帧
        output_dir: 关键帧保存目录

    Returns:
        List[Image.Image]: 关键帧列表（PIL Image格式）
    """
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")

    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"视频信息: {duration:.2f}秒, {fps:.2f}fps, 共{total_frames}帧")

    # 计算均匀采样的帧索引
    interval_frames = int(fps * interval_seconds)
    uniform_indices = set(range(0, total_frames, interval_frames))

    # 存储关键帧
    keyframes: List[Tuple[int, np.ndarray]] = []  # (帧索引, 帧数据)
    scene_change_indices = set()

    # 读取第一帧
    ret, prev_frame = cap.read()
    if not ret:
        raise ValueError("无法读取视频第一帧")

    # 添加第一帧
    keyframes.append((0, prev_frame.copy()))

    frame_idx = 1
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 检测场景变化
        if detect_scene_change(prev_frame, frame, scene_change_threshold):
            scene_change_indices.add(frame_idx)
            # 如果该帧还不在关键帧列表中，添加它
            if frame_idx not in [kf[0] for kf in keyframes]:
                keyframes.append((frame_idx, frame.copy()))

        # 均匀采样
        if frame_idx in uniform_indices and frame_idx not in [
            kf[0] for kf in keyframes
        ]:
            keyframes.append((frame_idx, frame.copy()))

        prev_frame = frame.copy()
        frame_idx += 1

    cap.release()

    print(f"场景变化检测到 {len(scene_change_indices)} 个切换点")
    print(f"共提取 {len(keyframes)} 个关键帧")

    # 按帧索引排序
    keyframes.sort(key=lambda x: x[0])

    # 如果关键帧过多，进行均匀采样
    if len(keyframes) > max_frames:
        step = len(keyframes) / max_frames
        selected_indices = [int(i * step) for i in range(max_frames)]
        keyframes = [keyframes[i] for i in selected_indices]
        print(f"关键帧数量超限，已采样至 {len(keyframes)} 帧")

    # 转换为 PIL Image 格式
    pil_images = []
    for idx, (frame_idx, frame) in enumerate(keyframes):
        # BGR 转 RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        pil_images.append(pil_img)

        # 可选：保存关键帧
        if save_keyframes:
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, f"keyframe_{idx:03d}_f{frame_idx}.jpg")
            pil_img.save(save_path)
            print(f"保存关键帧: {save_path}")

    return pil_images


def generate_cover_from_video(
    video_path: str,
    prompt: str = None,
    interval_seconds: float = 2.0,
    scene_change_threshold: float = 0.5,
    max_frames: int = 9,
    output_path: str = "video_cover.png",
    save_keyframes: bool = False,
    aspect_ratio: str = "9:16",
) -> str:
    """
    基于视频生成封面图

    Args:
        video_path: 视频文件路径
        prompt: 封面生成提示词（可选，不提供则使用默认提示词）
        interval_seconds: 关键帧采样间隔（秒）
        scene_change_threshold: 场景变化检测阈值
        max_frames: 最大关键帧数量
        output_path: 输出封面图路径
        save_keyframes: 是否保存提取的关键帧用于调试
        aspect_ratio: 输出图片宽高比，支持 "1:1", "3:4", "4:3", "9:16", "16:9"

    Returns:
        str: 生成的封面图保存路径
    """
    print(f"正在处理视频: {video_path}")

    # 1. 提取关键帧
    keyframes = extract_keyframes(
        video_path=video_path,
        interval_seconds=interval_seconds,
        scene_change_threshold=scene_change_threshold,
        max_frames=max_frames,
        save_keyframes=save_keyframes,
    )

    if not keyframes:
        raise ValueError("未能提取到任何关键帧")

    print(f"成功提取 {len(keyframes)} 个关键帧")

    # 2. 构建默认提示词
    if prompt is None:
        prompt = """
        基于以上视频关键帧，生成一张极具吸引力的病毒式传播风格视频封面图。

        【核心目标】让观众在0.5秒内产生"必须点击"的冲动！

        【视觉风格要求】
        1. 戏剧性光影：使用电影级的伦勃朗光或轮廓光，营造强烈的明暗对比
        2. 色彩爆发：饱和度拉满，使用互补色或撞色搭配（如青橙对比、紫金对比）
        3. 动态张力：即使是静态图片也要有"即将发生什么"的紧迫感
        4. 焦点突出：主体清晰锐利，背景适度虚化或使用径向模糊增强纵深感

        【构图技巧】
        1. 主体放大：关键元素占据画面60%以上，直击眼球
        2. 情绪捕捉：放大最具张力的表情或动作瞬间
        3. 留白悬念：适当留白制造好奇心和故事感
        4. 黄金分割或中心对称构图，确保视觉平衡

        【氛围增强】
        1. 可添加微妙的光晕、粒子效果增加氛围感
        2. 边缘可加轻微暗角聚焦视线
        3. 整体色调统一但要有亮点突破

        【输出规格】
        - 高清晰度，细节丰富
        - 风格与视频内容高度匹配但更具戏剧性
        """

    # 3. 构建请求内容（关键帧 + 提示词）
    contents = []
    for i, img in enumerate(keyframes):
        contents.append(img)
    contents.append(prompt)

    print(f"正在调用 Gemini API 生成封面图（宽高比: {aspect_ratio}）...")

    # 4. 配置生成参数，设置宽高比
    generation_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
        ),
    )

    # 5. 调用 gemini-3-pro-image-preview 生成封面
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=generation_config,
    )

    # 6. 保存生成的封面图
    for part in response.parts:
        if part.text is not None:
            print(f"模型返回文本: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(output_path)
            print(f"封面图已保存至: {output_path}")
            return output_path

    raise ValueError("模型未返回图像结果")


def check_ffmpeg_available() -> bool:
    """检查系统是否安装了 FFmpeg"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def replace_video_first_frames(
    video_path: str,
    cover_image_path: str,
    output_video_path: str = None,
    frames_to_replace: int = 2,
    preserve_audio: bool = True,
) -> str:
    """
    用封面图替换视频的前N帧，生成新视频

    Args:
        video_path: 原视频文件路径
        cover_image_path: 封面图路径
        output_video_path: 输出视频路径（可选，默认在原视频名后加 _with_cover）
        frames_to_replace: 要替换的帧数（默认2帧）
        preserve_audio: 是否保留原视频音频（默认True，需要FFmpeg）

    Returns:
        str: 生成的新视频路径
    """
    # 设置默认输出路径
    if output_video_path is None:
        base, ext = os.path.splitext(video_path)
        output_video_path = f"{base}_with_cover{ext}"

    # 打开原视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")

    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"原视频信息: {width}x{height}, {fps:.2f}fps, 共{total_frames}帧")
    print(f"替换前 {frames_to_replace} 帧（约 {frames_to_replace/fps:.3f} 秒）")

    # 读取封面图并调整大小以匹配视频尺寸
    cover_img = cv2.imread(cover_image_path)
    if cover_img is None:
        raise ValueError(f"无法读取封面图: {cover_image_path}")

    # 调整封面图大小以匹配视频分辨率
    cover_img_resized = cv2.resize(
        cover_img, (width, height), interpolation=cv2.INTER_LANCZOS4
    )
    print(f"封面图已调整为: {width}x{height}")

    # 检查是否需要保留音频
    use_ffmpeg = preserve_audio and check_ffmpeg_available()
    if preserve_audio and not use_ffmpeg:
        print("警告: FFmpeg 未安装，无法保留音频。输出视频将为静音。")
        print("安装 FFmpeg: brew install ffmpeg (macOS) 或 apt install ffmpeg (Linux)")

    # 确定临时文件或最终输出路径
    if use_ffmpeg:
        # 使用临时文件存储无音频视频
        temp_video_fd, temp_video_path = tempfile.mkstemp(suffix=".mp4")
        os.close(temp_video_fd)
        video_output = temp_video_path
    else:
        video_output = output_video_path

    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_output, fourcc, fps, (width, height))

    # 写入封面帧（替换前N帧）
    for i in range(frames_to_replace):
        out.write(cover_img_resized)
    print(f"已写入 {frames_to_replace} 帧封面图")

    # 跳过原视频的前N帧
    for _ in range(frames_to_replace):
        cap.read()

    # 写入剩余的原视频帧
    frame_count = frames_to_replace
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_count += 1

    # 释放资源
    cap.release()
    out.release()

    print(f"视频帧处理完成，总帧数: {frame_count}")

    # 如果需要保留音频，使用 FFmpeg 合并
    if use_ffmpeg:
        print("正在使用 FFmpeg 合并音频...")
        try:
            # 使用 FFmpeg 将原视频音频与新视频合并
            # -i temp_video_path: 新视频（无音频）
            # -i video_path: 原视频（提取音频）
            # -c:v copy: 复制视频流（不重新编码）
            # -c:a aac: 音频编码为 AAC
            # -map 0:v:0: 使用第一个输入的视频流
            # -map 1:a:0?: 使用第二个输入的音频流（如果存在）
            cmd = [
                "ffmpeg",
                "-y",  # 覆盖输出文件
                "-i",
                temp_video_path,  # 新视频（无音频）
                "-i",
                video_path,  # 原视频（提取音频）
                "-c:v",
                "copy",  # 复制视频流
                "-c:a",
                "aac",  # 音频编码
                "-map",
                "0:v:0",  # 使用新视频的视频流
                "-map",
                "1:a:0?",  # 使用原视频的音频流（如果有）
                "-shortest",  # 以最短的流为准
                output_video_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"FFmpeg 警告: {result.stderr}")
                # 如果 FFmpeg 失败，使用无音频版本
                import shutil

                shutil.move(temp_video_path, output_video_path)
                print("音频合并失败，已保存无音频版本")
            else:
                print("音频合并成功！")
                # 删除临时文件
                os.remove(temp_video_path)

        except Exception as e:
            print(f"FFmpeg 处理失败: {e}")
            # 如果出错，保留无音频版本
            import shutil

            shutil.move(temp_video_path, output_video_path)

    print(f"新视频已生成: {output_video_path}")
    return output_video_path


def generate_cover_and_replace_frames(
    video_path: str,
    prompt: str = None,
    interval_seconds: float = 2.0,
    scene_change_threshold: float = 0.5,
    max_frames: int = 9,
    cover_output_path: str = "video_cover.png",
    video_output_path: str = None,
    frames_to_replace: int = 2,
    save_keyframes: bool = False,
    aspect_ratio: str = "9:16",
) -> Tuple[str, str]:
    """
    完整流程：生成封面图并替换视频前N帧

    Args:
        video_path: 视频文件路径
        prompt: 封面生成提示词（可选）
        interval_seconds: 关键帧采样间隔（秒）
        scene_change_threshold: 场景变化检测阈值
        max_frames: 最大关键帧数量
        cover_output_path: 封面图输出路径
        video_output_path: 新视频输出路径（可选）
        frames_to_replace: 要替换的帧数
        save_keyframes: 是否保存提取的关键帧
        aspect_ratio: 输出图片宽高比，支持 "1:1", "3:4", "4:3", "9:16", "16:9"

    Returns:
        Tuple[str, str]: (封面图路径, 新视频路径)
    """
    # 1. 生成封面图
    cover_path = generate_cover_from_video(
        video_path=video_path,
        prompt=prompt,
        interval_seconds=interval_seconds,
        scene_change_threshold=scene_change_threshold,
        max_frames=max_frames,
        output_path=cover_output_path,
        save_keyframes=save_keyframes,
        aspect_ratio=aspect_ratio,
    )

    # 2. 用封面图替换视频前N帧
    new_video_path = replace_video_first_frames(
        video_path=video_path,
        cover_image_path=cover_path,
        output_video_path=video_output_path,
        frames_to_replace=frames_to_replace,
    )

    return cover_path, new_video_path


# 使用示例
if __name__ == "__main__":
    # 视频文件路径（请替换为实际路径）
    VIDEO_PATH = "/Users/zsa/Desktop/AGI/DeepResearch智能体/deep-research-agent/张家班/图片生成/猫狗抢牛排大战.mp4"

    # 自定义提示词（可选）- 针对宠物/搞笑类视频优化
    CUSTOM_PROMPT = """
    基于以上视频关键帧，生成一张让人忍不住想点击的爆款视频封面！

    【封面风格】萌宠搞笑 + 灾难现场 + 表情包级别的夸张效果

    【必须包含的元素】
    1. 主角特写：将视频中的主角（宠物/人物）放大到画面中心，占据50%以上面积
    2. 夸张表情：捕捉或强化最有戏剧性的表情——惊恐、无辜、得意、崩溃等
    3. 混乱场景：背景展示"灾难现场"的混乱感，但要有美感地呈现
    4. 动态感：添加速度线、冲击波纹或飞溅效果，让静态画面充满动感

    【色彩与光影】
    1. 高饱和度暖色调为主，突出活力和喜感
    2. 主体打亮，背景稍暗，形成强烈对比
    3. 可加入彩色光斑或镜头光晕增加趣味性
    4. 整体明快但不刺眼，适合各平台展示

    【构图要点】
    1. 主体居中或三分法构图
    2. 预留上方空间（给标题党文字留位置）
    3. 画面要有"故事感"——让观众想知道"到底发生了什么？！"
    4. 边缘可添加轻微模糊或暗角聚焦视线

    【氛围】
    - 搞笑但不低俗
    - 可爱但有张力
    - 让人看一眼就想笑或想点进去看完整视频

    【输出】9:16竖版，高清晰度，细节丰富，适合短视频平台
    """

    # 检查视频文件是否存在
    if not os.path.exists(VIDEO_PATH):
        print(f"请将 VIDEO_PATH 变量修改为实际的视频文件路径")
        print(f"当前路径: {VIDEO_PATH}")
    else:
        # 完整流程：生成封面并替换视频前2帧
        cover_path, new_video_path = generate_cover_and_replace_frames(
            video_path=VIDEO_PATH,
            prompt=CUSTOM_PROMPT,
            interval_seconds=2.0,  # 每2秒提取一帧
            scene_change_threshold=0.5,  # 场景变化阈值
            max_frames=9,  # 最多9帧（模型限制）
            cover_output_path="video_cover.png",
            frames_to_replace=2,  # 替换前2帧
            save_keyframes=True,  # 保存关键帧用于调试
            aspect_ratio="9:16",  # 竖版封面，适合短视频平台
        )
        print(f"封面生成完成: {cover_path}")
        print(f"新视频生成完成: {new_video_path}")
