# -*- coding: utf-8 -*-
"""
工具函数
"""
import os
import json
from pathlib import Path
from typing import Optional
import cv2


def ensure_data_dir(session_id: str = "default"):
    """确保数据目录存在"""
    base_dir = Path(__file__).parent / "data" / session_id
    dirs = ["story", "videos", "images", "storyboards"]
    for d in dirs:
        (base_dir / d).mkdir(parents=True, exist_ok=True)


def save_story(story: str, index: int, session_id: str = "default") -> str:
    """保存故事到文件"""
    ensure_data_dir(session_id)
    file_path = Path(__file__).parent / "data" / session_id / "story" / f"story_{index:04d}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(story)
    return str(file_path)


def save_storyboard(storyboard: str, index: int, session_id: str = "default") -> str:
    """保存分镜脚本到文件"""
    ensure_data_dir(session_id)
    file_path = Path(__file__).parent / "data" / session_id / "storyboards" / f"storyboard_{index:04d}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json.loads(storyboard), f, ensure_ascii=False, indent=2)
    return str(file_path)


def extract_last_frame(video_path: str, output_path: Optional[str] = None, session_id: str = "default") -> Optional[str]:
    """
    从视频中提取最后一帧作为图片
    
    Args:
        video_path: 视频文件路径
        output_path: 输出图片路径（可选）
        session_id: 会话ID，用于数据隔离
    
    Returns:
        图片路径，如果失败返回None
    """
    try:
        ensure_data_dir(session_id)
        if output_path is None:
            # 自动生成输出路径
            video_name = Path(video_path).stem
            output_path = str(Path(__file__).parent / "data" / session_id / "images" / f"{video_name}_last_frame.jpg")
        
        # 打开视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频文件: {video_path}")
            return None
        
        # 获取视频总帧数
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            print("视频文件为空")
            cap.release()
            return None
        
        # 读取最后一帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("无法读取最后一帧")
            return None
        
        # 保存图片
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, frame)
        return output_path
        
    except Exception as e:
        print(f"提取最后一帧失败: {e}")
        return None


def get_next_video_index(session_id: str = "default") -> int:
    """获取下一个视频索引"""
    ensure_data_dir(session_id)
    video_dir = Path(__file__).parent / "data" / session_id / "videos"
    existing_files = list(video_dir.glob("video_*.mp4"))
    if not existing_files:
        return 0
    indices = []
    for f in existing_files:
        try:
            idx = int(f.stem.split("_")[-1])
            indices.append(idx)
        except:
            pass
    return max(indices) + 1 if indices else 0


def get_next_story_index(session_id: str = "default") -> int:
    """获取下一个故事索引"""
    ensure_data_dir(session_id)
    story_dir = Path(__file__).parent / "data" / session_id / "story"
    existing_files = list(story_dir.glob("story_*.txt"))
    if not existing_files:
        return 0
    indices = []
    for f in existing_files:
        try:
            idx = int(f.stem.split("_")[-1])
            indices.append(idx)
        except:
            pass
    return max(indices) + 1 if indices else 0


def concatenate_videos(video_paths: list, output_path: str) -> bool:
    """
    拼接多个视频文件
    使用ffmpeg进行拼接（如果可用），否则使用OpenCV
    
    Args:
        video_paths: 视频文件路径列表（按顺序）
        output_path: 输出视频路径
    
    Returns:
        是否成功
    """
    try:
        if not video_paths:
            print("没有视频文件需要拼接")
            return False
        
        # 确保所有视频文件都存在
        valid_videos = []
        for vp in video_paths:
            abs_path = Path(vp).resolve()
            if abs_path.exists():
                valid_videos.append(str(abs_path))
            else:
                print(f"警告: 视频文件不存在: {vp}")
        
        if not valid_videos:
            print("没有有效的视频文件")
            return False
        
        # 确保输出目录存在
        output_dir = Path(output_path).parent
        os.makedirs(output_dir, exist_ok=True)
        
        # 尝试使用ffmpeg（更好的浏览器兼容性）
        try:
            import subprocess
            # 创建文件列表用于ffmpeg concat
            list_file = output_dir / "concat_list.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for video in valid_videos:
                    # 转义单引号和特殊字符
                    video_escaped = video.replace("'", "'\"'\"'")
                    f.write(f"file '{video_escaped}'\n")
            
            # 使用ffmpeg拼接视频，确保保留音频
            # 先尝试直接复制流（最快，保留原始音频）
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c:v', 'copy',  # 复制视频流
                '-c:a', 'copy',  # 复制音频流（保留原始音频）
                '-map', '0',  # 映射所有流
                '-y',  # 覆盖输出文件
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # 如果直接复制失败（编码不一致），重新编码但保留音频
            if result.returncode != 0:
                print("直接复制流失败，使用重新编码（保留音频）...")
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(list_file),
                    '-c:v', 'libx264',  # H.264视频编码
                    '-c:a', 'aac',  # AAC音频编码（确保音频存在）
                    '-b:a', '128k',  # 音频比特率
                    '-map', '0:v:0',  # 映射视频流
                    '-map', '0:a:0?',  # 映射音频流（如果存在）
                    '-preset', 'medium',
                    '-crf', '23',  # 质量参数
                    '-shortest',  # 以最短流为准（避免音频视频不同步）
                    '-y',
                    str(output_path)
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
            
            # 清理临时文件
            if list_file.exists():
                list_file.unlink()
            
            if result.returncode == 0:
                print(f"使用ffmpeg拼接视频完成: {output_path}")
                return True
            else:
                print(f"ffmpeg拼接失败: {result.stderr}")
                # 继续使用OpenCV方法
                
        except FileNotFoundError:
            print("未找到ffmpeg，使用OpenCV方法")
        except Exception as e:
            print(f"ffmpeg方法失败: {e}，使用OpenCV方法")
        
        # 使用OpenCV方法（备用方案）
        # 注意：OpenCV只处理视频帧，不处理音频，会丢失音频
        print("警告：使用OpenCV方法，音频将被丢失。建议安装ffmpeg以保留音频。")
        
        # 读取第一个视频获取属性
        first_video = cv2.VideoCapture(valid_videos[0])
        if not first_video.isOpened():
            print(f"无法打开第一个视频: {valid_videos[0]}")
            return False
        
        # 获取视频属性
        fps = int(first_video.get(cv2.CAP_PROP_FPS))
        if fps <= 0:
            fps = 30  # 默认30fps
        width = int(first_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(first_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 尝试多种编码格式
        fourcc_options = [
            ('avc1', 'H.264/AVC1'),
            ('H264', 'H.264'),
            ('mp4v', 'MPEG-4'),
        ]
        
        fourcc = None
        fourcc_name = None
        for codec, name in fourcc_options:
            test_fourcc = cv2.VideoWriter_fourcc(*codec)
            if test_fourcc != -1:
                fourcc = test_fourcc
                fourcc_name = name
                break
        
        if fourcc is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fourcc_name = 'MPEG-4 (fallback)'
        
        first_video.release()
        
        print(f"使用编码: {fourcc_name}")
        
        # 创建视频写入器
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            print("无法创建输出视频文件")
            return False
        
        # 逐个读取并写入视频
        for video_path in valid_videos:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"无法打开视频: {video_path}")
                continue
            
            # 检查分辨率是否一致
            v_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            v_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if v_width != width or v_height != height:
                print(f"警告: 视频 {video_path} 的分辨率 ({v_width}x{v_height}) 与第一个视频 ({width}x{height}) 不一致，将进行缩放")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 如果分辨率不一致，进行缩放
                if v_width != width or v_height != height:
                    frame = cv2.resize(frame, (width, height))
                
                out.write(frame)
            
            cap.release()
        
        out.release()
        print(f"使用OpenCV拼接视频完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"拼接视频失败: {e}")
        import traceback
        traceback.print_exc()
        return False

