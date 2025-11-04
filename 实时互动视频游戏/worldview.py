# -*- coding: utf-8 -*-
"""
默认世界观和故事背景
"""
import os
from pathlib import Path
from typing import Optional
import sys

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from gemini_image_client import GeminiImageClient

DEFAULT_WORLDVIEW = """
# 星尘遗境：最后的符文

## 世界观设定

在一个被魔法与科技交织的奇幻世界中，古老的符文之力正在逐渐消散。千年前，伟大的符文法师们创造了维持世界平衡的"星尘之塔"，但如今这些塔正在一座座崩塌。

**核心设定：**
- **符文之力**：一种连接自然元素与魔法的神秘力量，正随着星尘之塔的崩塌而减弱
- **元素领域**：世界分为火、水、风、土四大元素领域，每个领域都有独特的生态和规则
- **最后的希望**：传说只有集齐四枚元素符文，才能重新激活星尘之塔，拯救世界

## 故事背景

你是一名符文学徒，在导师的指引下踏上了寻找元素符文的旅程。你拥有罕见的"全元素亲和"天赋，能够感知和操控所有元素，但也因此成为了各方势力觊觎的目标。

在一个风雨交加的夜晚，你从学院的图书馆中醒来，发现导师留下一张神秘的地图和一句话："当星尘坠落，符文将指引你的道路。"

**你的使命：**
- 穿越四大元素领域，寻找失落的元素符文
- 解开星尘之塔崩塌的真相
- 保护世界免受元素失衡带来的灾难
- 掌握真正的符文之力

**当前状态：**
你站在学院的最高塔楼上，远眺着被元素风暴撕裂的天空。手中的地图闪烁着微弱的符文光芒，指引着通往"风之谷"的方向。空气中充满了不安的元素波动，似乎有什么巨大的变化即将到来...

---

**游戏开始：** 你决定离开学院，踏上寻找符文的旅程。你会选择哪个方向前进？
"""


def get_default_worldview() -> str:
    """获取默认世界观"""
    return DEFAULT_WORLDVIEW


def generate_cover_image(worldview_text: Optional[str] = None) -> Optional[str]:
    """
    生成游戏封面图

    Args:
        worldview_text: 世界观文本（可选），用于生成更匹配的封面图

    Returns:
        封面图路径，如果失败返回None
    """
    try:
        # 构建封面图提示词
        if (
            worldview_text
            and worldview_text.strip()
            and len(worldview_text.strip()) > 50
        ):
            # 如果提供了世界观文本，基于世界观生成提示词
            prompt = f"""根据以下游戏世界观，创建一个RPG游戏封面图：

{worldview_text[:500]}

要求：
- 画面要体现世界观的核心元素和氛围
- 具有史诗感和神秘感
- 适合作为游戏封面
- 高质量，精美细节
- 视觉风格要与世界观匹配"""
        else:
            # 默认提示词（基于当前世界观）
            prompt = """创建一个奇幻RPG游戏封面图，画面包含：
- 一个年轻的符文学徒站在高塔上，手持闪烁着元素光芒的符文
- 背景是被元素风暴撕裂的天空，四大元素（火、水、风、土）在天空中交织
- 远处有崩塌的星尘之塔，散发着神秘的光芒
- 整体风格：奇幻、神秘、史诗感、魔法与科技交织
- 游戏标题风格：星尘遗境：最后的符文
- 适合作为游戏封面，高质量，精美细节"""

        # 初始化客户端
        client = GeminiImageClient()

        # 设置保存路径
        cover_path = str(Path(__file__).parent / "data" / "images" / "cover_image.png")

        # 生成图片（使用16:9宽高比，适合封面）
        image_path = client.generate_image(
            prompt=prompt, save_path=cover_path, aspect_ratio="16:9"
        )

        return image_path
    except Exception as e:
        print(f"生成封面图失败: {e}")
        return None
