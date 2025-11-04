# 视频模型质量评估

采用策略模式设计，调用多个视频模型生成视频，并且评估生成视频的效果。

## 目录结构

```
视频评估Agent/
├── base_strategy.py          # 策略模式基类
├── core_executor.py          # 核心执行流程
├── main.py                   # 生成测试主入口
├── video_evaluator.py        # 对视频进行效果评估
├── prompt.txt                # 测试数据（角色名称和Prompt）
├── pics/                     # 参考图片目录
├── fal/                      # Fal模型策略实现
│   └── strategy.py
├── sora2/                    # Sora2模型策略实现
│   └── strategy.py
├── wan/                      # 阿里万象模型策略实现
│   └── strategy.py
├── wavespeed/                # WaveSpeed模型策略实现
│   └── strategy.py
├── ltx2/                     # LTX-2模型策略实现
│   └── strategy.py
└── gaga/                     # Gaga模型策略实现
    └── strategy.py
```

## 生成测试 - 使用方法

```bash
# 使用Fal模型，保留角色名
python main.py --model fal

# 使用Fal模型，隐藏角色名（替换为"this character"）
python main.py --model fal --hide-name

# 使用Sora2模型
python main.py --model sora2

# 使用阿里万象模型
python main.py --model wan

# 使用WaveSpeed模型
python main.py --model wavespeed

# 使用LTX-2模型
python main.py --model ltx2

# 使用Gaga模型
python main.py --model gaga
```

### 参数说明

- `--model`: 选择视频生成模型，可选值：`fal`、`sora2`、`wan`、`wavespeed`、`ltx2`、`gaga`
- `--hide-name`: 可选参数，如果指定则隐藏角色名（替换为"this character"）

### 环境变量配置（生成）

- Fal: `FAL_KEY`
- Sora2: `OPENAI_API_KEY`
- Wan（阿里万象）: `DASHSCOPE_API_KEY`
- WaveSpeed: `WAVESPEED_API_KEY`
- LTX-2: `LTX_API_KEY`
- Gaga: `GAGA_API_KEY`

## 视频质量评估

基于 Gemini 2.5 Flash 的视频理解能力，对指定目录内所有视频进行 6 个维度评分（1~10分，支持小数）：
- 信息密度（Information Density）：剧情传递的信息含量
- 一致性（Consistency）：视频每一帧中的人物和场景是否都保持一致
- 流畅度（Fluency）：视频中人物动作和镜头切换等是否流畅
- 音画同步性（Audio-Visual Synchronization）：视频中的声音和图像是否一致
- 画面质量（Visual Quality）：是否存在丢帧、卡顿等画面质量问题
- 物理规律遵循（Physics Compliance）：画面是否遵循物理规律

模型生成每个视频的 JSON 结果（包含各维度分数、原因与总分），并计算总体平均分。总分范围为 6.0~60.0 分。

参考文档：`https://ai.google.dev/gemini-api/docs/video-understanding?hl=zh-cn`

### 使用方法

```bash
# 评估某目录下所有视频，并打印平均分
export GEMINI_API_KEY=your_key
python video_evaluator.py --dir ./sora

# 指定视频文件目录，并保存报告
python video_evaluator.py --dir ./sora --save-report
```

### 环境变量（评分）
- `GEMINI_API_KEY`

### 输出
- 终端打印每个视频的评分摘要与总体平均分
- 若加 `--save-report`，会在目标目录生成 `video_quality_eval_report__YYYYMMDD_HHMMSS.json`

## 执行流程（生成）

1. 从 `prompt.txt` 文件中读取角色名称和视频Prompt
2. 从 `pics` 目录下读取角色对应的参考图片
3. 调用不同的视频生成模型API，传入Prompt和参考图片，生成视频并轮询结果
4. 视频生成成功后，将视频下载下来，保存到模型对应的目录下
5. 生成测试报告，保存到模型对应的目录下

## 输出结果（生成）

### 视频文件
- `{model_name}_with_name/` - 保留角色名模式
- `{model_name}_hidden_name/` - 隐藏角色名模式

### 测试报告
- `{model_name}_*/report_YYYYMMDD_HHMMSS.txt`

## 设计说明

- 策略模式：统一接口 `VideoGenerationStrategy`（生成、轮询、下载）
- 核心执行器：`VideoTestExecutor` 统一实现测试流程

## 注意事项

1. 确保有足够的 API 配额
2. 生成任务间隔为 5 秒，避免限流
3. 确保参考图片存在于 `pics/` 目录
4. 输出目录自动创建

