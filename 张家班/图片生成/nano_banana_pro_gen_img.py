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

# 生成图片
prompt = """
未来科技风格的数字控制室可视化场景，展示AI Agent的记忆与状态管理系统。画面中央是一条水平延伸的发光全息时间轴，上面标记着多个发光的检查点节点，代表状态快照。多条半透明的数据线程像神经通路一样分支出去，每条都带有飘浮的线程ID标识。画面一侧，一个人类剪影通过悬浮的交互界面与系统进行交互（人机协作）。时间旅行通过弯曲的箭头回溯到之前的检查点节点来呈现。青色和品红色的数据流连接到底部的圆柱形数据库结构。整个场景沐浴在深蓝色和电紫色的环境光中，配有全息HUD元素、背景电路图案和飘浮的JSON代码片段。超现代科幻美学，8K分辨率，电影级光影，数字艺术风格。
"""

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt],
)

# 保存图片
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")
