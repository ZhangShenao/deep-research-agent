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
帮我创作一幅 Multi-Agent 的系统架构图，描述如下系统：
1. 具体业务为一个旅游规划的多智能体项目：
2. 由一个 Customer Agent 作为 Controller Agent ，引导用户对话，进行意图识别，并调度下面2个子 Agent
3. Weather Sub-Agent ，绑定了 get_weather 工具，用于查询指定城市的天气
4. Ticket Sub-Agent，绑定了 get_train_ticket 工具，用于查询出发地到目的地的火车票价
5. 整体执行过程通过控制台执行，以 Stream 流式方式打印执行效果
6. 整个项目使用共享的 MongoDB 作为 Checkpoint 

整体风格简约大气，强调科技感与未来感。
帮我生成完整的图片。
"""

generation_config = types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    image_config=types.ImageConfig(aspect_ratio="9:16"),
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
        image.save("multi-agent-system-architecture.png")
