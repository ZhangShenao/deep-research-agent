# 快速开始指南

## 1. 环境准备

### 安装Python依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API配置（用于Sora2）
OPENAI_API_KEY=your_openai_api_key_here
```

## 2. 启动应用

### 方式1：使用启动脚本（推荐）

```bash
chmod +x run.sh
./run.sh
```

### 方式2：直接运行

```bash
streamlit run app.py
```

## 3. 使用流程

1. **首次启动**：查看游戏世界观和故事背景
2. **点击"开始游戏"**：进入游戏界面
3. **输入指令**：例如：
   - "我向前走，探索前方的道路"
   - "我拔出剑，准备战斗"
   - "我检查地上的物品"
4. **等待处理**：系统会依次执行：
   - 📝 续写剧情
   - 🎬 生成分镜脚本
   - 🖼️ 抽取参考图片（如果有上一段视频）
   - 🎥 生成视频
5. **查看结果**：在侧边栏查看：
   - 最新剧情
   - 分镜脚本
   - 参考图片
   - 生成的视频
6. **继续游戏**：输入新的指令继续冒险

## 4. 测试导入

运行测试脚本验证环境配置：

```bash
python test_imports.py
```

## 5. 数据存储位置

- 故事文件：`data/story/story_XXXX.txt`
- 分镜脚本：`data/storyboards/storyboard_XXXX.json`
- 视频文件：`data/videos/video_XXXX.mp4`
- 参考图片：`data/images/video_XXXX_last_frame.jpg`

## 6. 常见问题

### Q: 视频生成失败怎么办？
A: 检查：
- OpenAI API密钥是否正确
- 网络连接是否正常
- API配额是否充足

### Q: 分镜脚本生成失败？
A: 检查：
- DeepSeek API密钥是否正确
- LLM返回的JSON格式是否正确
- 查看错误信息中的原始内容

### Q: 图片提取失败？
A: 检查：
- 是否安装了opencv-python
- 视频文件是否存在
- 视频文件格式是否支持

## 7. 自定义配置

### 修改世界观

编辑 `worldview.py` 中的 `DEFAULT_WORLDVIEW` 变量。

### 调整提示词

编辑 `prompts.py` 中的提示词模板。

### 修改视频参数

编辑 `sora2_client.py` 中的视频生成参数：
- `seconds`: 视频时长（默认8秒）
- `size`: 视频尺寸（默认720x1280）

## 8. 开发建议

- 使用虚拟环境管理依赖
- 定期备份 `data/` 目录
- 监控API使用情况
- 根据实际需求调整轮询间隔和超时时间

