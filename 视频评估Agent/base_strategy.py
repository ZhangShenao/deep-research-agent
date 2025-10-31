# -*- coding: utf-8 -*-
"""
策略模式基类，定义统一的视频生成接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class VideoGenerationStrategy(ABC):
    """视频生成策略基类"""
    
    @abstractmethod
    def generate_video(
        self, 
        prompt: str, 
        reference_image_path: Optional[str] = None
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        下载视频
        
        Args:
            video_url: 视频URL
            save_path: 保存路径
            
        Returns:
            是否下载成功
        """
        pass

