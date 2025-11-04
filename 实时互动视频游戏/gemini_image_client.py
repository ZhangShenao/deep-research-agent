# -*- coding: utf-8 -*-
"""
Gemini图片生成客户端
参考文档: https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    from PIL import Image
    from io import BytesIO
except ImportError:
    print("警告: 未安装google-genai或Pillow，请运行: pip install google-genai Pillow")
    genai = None
    types = None
    Image = None
    BytesIO = None

load_dotenv()


class GeminiImageClient:
    """Gemini图片生成客户端"""

    def __init__(self):
        """初始化Gemini客户端"""
        if genai is None:
            raise ImportError("请安装google-genai: pip install google-genai")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("未找到GEMINI_API_KEY环境变量，请在.env文件中设置")
        self.client = genai.Client(api_key=api_key)

    def generate_image(
        self, prompt: str, save_path: Optional[str] = None, aspect_ratio: str = "16:9"
    ) -> Optional[str]:
        """
        生成图片
        
        Args:
            prompt: 图片生成提示词
            save_path: 保存路径（可选）
            aspect_ratio: 宽高比，默认16:9
        
        Returns:
            图片路径，如果失败返回None
        """
        try:
            if Image is None or BytesIO is None or types is None:
                raise ImportError("请安装必要的依赖: pip install google-genai Pillow")
            
            # 调用Gemini API生成图片
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    )
                ),
            )

            # 提取图片数据
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # 将base64数据转换为图片
                    image = Image.open(BytesIO(part.inline_data.data))
                    
                    # 如果没有指定保存路径，自动生成
                    if save_path is None:
                        save_path = str(Path(__file__).parent / "data" / "images" / "cover_image.png")
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    
                    # 保存图片
                    image.save(save_path)
                    return save_path
            
            return None
        except Exception as e:
            print(f"生成图片失败: {e}")
            return None

