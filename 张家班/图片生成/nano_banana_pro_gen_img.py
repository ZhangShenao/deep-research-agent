# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06 10:00
@Author  : ZhangShenao
@File    : nano_banana_pro_gen_img.py
@Desc    : 使用 Nano Banana Pro 生成图片

参考文档： https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn
"""

from google import genai
from google.genai import types
from PIL import Image

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化Gemini客户端
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 生成图片的Prompt
prompt = """
帮我创作一幅 "Agentic Spectrum" 信息图，展示从 Workflow 到 Agent 的连续光谱：

图片布局：
- 横向渐变光谱设计，从左到右代表 "agentic 程度" 递增
- 左侧标注 "低 agentic 程度"，右侧标注 "高 agentic 程度"
- 使用渐变色条：左侧冷色调（蓝色）渐变到右侧暖色调（橙色/金色）

光谱上的 5 个关键节点（从左到右）：
1. 纯 Workflow - 图标：固定齿轮链条 - 标签："顺序执行，固定步骤"
2. 条件分支 Workflow - 图标：分叉路径 - 标签："if/else 条件判断"
3. LLM 路由 Workflow - 图标：AI 大脑 + 路由器 - 标签："LLM 决定下一步"
4. 受限 Agent - 图标：带边界框的机器人 - 标签："工具调用循环，有约束"
5. 完全自主 Agent - 图标：自由飞翔的机器人/AI - 标签："完全由 LLM 驱动决策"

每个节点下方用小图标和简短文字说明其特点。

底部添加一行说明文字："Most production systems are a combination of workflows and agents"

整体风格：
- 现代科技感信息图风格
- 简洁清晰，配色专业
- 强调"连续光谱"而非"二元对立"的概念
- 适合作为技术博客配图

生成 16:9 横版图片。
"""

generation_config = types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    image_config=types.ImageConfig(aspect_ratio="16:9"),
)
response = client.models.generate_content(
    model="gemini-3-pro-image-preview", contents=[prompt], config=generation_config
)

# 保存图片
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("LumiLumi_architecture.png")
