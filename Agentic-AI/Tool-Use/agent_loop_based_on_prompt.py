# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/26
@Author  : ZhangShenao
@File    : agent_loop_based_on_prompt.py
@Desc    : 基于Prompt Engineering驱动的Agent Loop
"""

from llm.llm import generate_response
from parser.parser import parse_action
from tool.tools import list_files, read_file
import json

# 定义System Prompt
# 在System Prompt中，定义了Agent可以调用的工具列表和工具的参数说明
# 通过Prompt Engineering的方式，来驱动Agent调用工具，完成任务
SYSTEM_PROMPT = """
你是一个强大的AI智能体，可以通过使用可用工具来执行任务。

以下是你可以调用的工具列表：

```json
{
    "list_files": {
        "description": "列出当前目录中的所有文件。",
        "parameters": {}
    },
    "read_file": {
        "description": "读取文件的内容。",
        "parameters": {
            "file_name": {
                "type": "string",
                "description": "要读取的文件名。"
            }
        }
    },
    "terminate": {
        "description": "结束智能体循环并提供任务摘要。",
        "parameters": {
            "message": {
                "type": "string",
                "description": "返回给用户的摘要消息。"
            }
        }
    }
}
```

如果用户询问文件、文档或内容，请先列出文件，然后再读取它们。

当你完成任务后，请使用 `terminate` 来工具结束对话，我将向用户提供结果。

重要：每个响应都必须包含一个动作！！！

你必须始终严格按照以下格式响应：

<停下来逐步思考。参数映射到args。在这里插入你逐步思考的丰富描述。>

```action
{
    "tool_name": "插入工具名称",
    "args": {...在这里填入任何必需的参数...}
}```
"""

# 定义Agent的最大迭代次数，避免出现无限循环
MAX_ITERATIONS = 10

if __name__ == "__main__":
    # 记录迭代次数
    iteration = 0

    # 获取用户任务
    user_task = input("请输入您想让我执行的任务：")

    # 保存Memory记忆
    memory = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_task,
        },
    ]

    # 执行Agent Loop
    while iteration < MAX_ITERATIONS:
        print(f"【Round {iteration + 1}】Agent 正在思考")

        # 调用LLM,生成响应
        response = generate_response(messages=memory)
        print(f"【Round {iteration + 1}】Agent 执行结果: {response}")

        # 解析响应以确定要执行的动作
        action = parse_action(response)
        result = "Action executed"  # 默认结果

        # 根据解析出的动作执行相应的工具函数
        if action["tool_name"] == "list_files":
            result = {"result": list_files()}
        elif action["tool_name"] == "read_file":
            result = {"result": read_file(action["args"]["file_name"])}
        elif action["tool_name"] == "error":
            result = {"error": action["args"]["message"]}
        elif action["tool_name"] == "terminate":
            print(action["args"]["message"])
            break  # 终止循环
        else:
            result = {"error": "Unknown action: " + action["tool_name"]}

        print(f"Action result: {result}")

        # 更新对话记忆，添加智能体响应和执行结果
        memory.extend(
            [
                {"role": "assistant", "content": response},
                {"role": "tool", "content": json.dumps(result)},
            ]
        )

        # 检查终止条件
        if action["tool_name"] == "terminate":
            break

        iteration += 1  # 增加迭代计数
