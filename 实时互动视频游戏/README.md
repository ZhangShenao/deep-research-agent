# 实时互动视频游戏

一款基于LangGraph和Sora2的实时互动暗黑系RPG视频游戏。

## 功能特点

- 🎮 **暗黑系RPG游戏风格**：完整的游戏世界观和故事背景
- 💬 **聊天式互动**：用户通过对话和指令控制游戏进程
- 📝 **智能剧情续写**：根据用户输入自动续写游戏剧情
- 🎬 **自动分镜脚本**：根据剧情自动生成3-5个分镜
- 🎥 **AI视频生成**：使用Sora2生成8秒游戏视频
- 🔗 **视频连贯性**：自动提取上一段视频的最后一帧作为下一段的参考

## 技术架构

- **后端框架**：Python + LangGraph
- **前端界面**：Streamlit
- **LLM模型**：DeepSeek Chat
- **视频生成**：Sora2 (OpenAI)
- **数据存储**：本地文件系统

## 工作流程

```
用户输入 → 续写剧情 → 生成分镜脚本 → 抽取参考图片 → 生成视频 → 展示结果
```

每个步骤完成后立即在前端展示结果，并提示下一个步骤的进度。

## 安装步骤

1. **克隆或下载项目**

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件，添加以下配置：
```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API配置（用于Sora2）
OPENAI_API_KEY=your_openai_api_key
```

4. **运行应用**
```bash
streamlit run app.py
```

## 使用说明

1. **首次启动**：系统会显示默认的游戏世界观和故事背景
2. **开始游戏**：点击"开始游戏"按钮
3. **输入指令**：在聊天框中输入你的行动或对话（例如："我向前走，探索前方的道路"）
4. **查看结果**：
   - 主界面会显示聊天历史和最新剧情
   - 侧边栏会显示：
     - 最新剧情内容
     - 生成的分镜脚本
     - 参考图片（如果有）
     - 生成的视频
5. **继续游戏**：输入新的指令，系统会续写剧情并生成新的视频

## 数据存储

所有数据保存在 `data/` 目录下：
- `data/story/`：故事文本文件
- `data/storyboards/`：分镜脚本JSON文件
- `data/videos/`：生成的视频文件
- `data/images/`：提取的参考图片

## 注意事项

1. **API密钥**：确保配置了正确的DeepSeek和OpenAI API密钥
2. **视频生成时间**：视频生成可能需要较长时间（通常几分钟），请耐心等待
3. **网络连接**：需要稳定的网络连接来调用API
4. **资源消耗**：视频生成会消耗API配额，请合理使用

## 项目结构

```
实时互动视频游戏/
├── app.py                 # Streamlit前端应用
├── agent.py               # LangGraph Agent主流程
├── state.py               # 状态定义
├── llm.py                 # LLM模型配置
├── sora2_client.py        # Sora2视频生成客户端
├── worldview.py           # 默认世界观和故事背景
├── prompts.py             # 提示词模板
├── utils.py               # 工具函数
├── nodes/                 # LangGraph节点
│   ├── story_node.py      # 剧情续写节点
│   ├── storyboard_node.py # 分镜脚本生成节点
│   ├── extract_frame_node.py # 图片抽取节点
│   └── video_node.py      # 视频生成节点
├── data/                  # 数据目录
│   ├── story/             # 故事文件
│   ├── videos/            # 视频文件
│   ├── images/            # 图片文件
│   └── storyboards/       # 分镜脚本文件
├── requirements.txt       # 依赖列表
└── README.md             # 说明文档
```

## 开发说明

### 工作流节点说明

1. **story_continuation_node**：根据用户输入续写剧情
2. **storyboard_node**：根据剧情生成分镜脚本（3-5个分镜）
3. **extract_frame_node**：从上一段视频提取最后一帧
4. **video_generation_node**：调用Sora2生成视频

### 自定义世界观

可以修改 `worldview.py` 中的 `DEFAULT_WORLDVIEW` 来定制游戏世界观。

### 调整提示词

可以修改 `prompts.py` 中的提示词模板来优化生成效果。

## 许可证

MIT License

