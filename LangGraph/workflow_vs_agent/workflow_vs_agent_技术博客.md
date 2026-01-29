# Workflow vs Agent？本质上是个光谱

> 本文基于 LangGraph 官方博客 [How to think about agent frameworks](https://blog.langchain.com/how-to-think-about-agent-frameworks/) 的核心观点，结合个人理解撰写。

## 引言

2024-2025 年，Agent（智能体）无疑是 AI 领域最火热的话题之一。各种 Agent 框架层出不穷：LangGraph、OpenAI Agents SDK、Google ADK、CrewAI、AutoGen……开发者们在选择时常常陷入困惑：

- 我的应用到底需要 Agent 还是 Workflow？
- 什么时候该用 Agent，什么时候用 Workflow 就够了？
- Agent 框架这么多，该怎么选？

这些问题的答案，往往被过度简化成了一个二元选择。但实际上，**Workflow 和 Agent 之间并不是非此即彼的关系，而是一个连续的光谱**。

## 什么是 Agent？什么是 Workflow？

在深入讨论之前，我们需要先澄清这两个概念的定义。

### OpenAI 的定义（抽象版）

> Agents are systems that independently accomplish tasks on your behalf.
> 
> Agent 是能够代表你独立完成任务的系统。

这个定义过于抽象，几乎没有给出任何技术上的指导意义。

### Anthropic 的定义（务实版）

Anthropic 在其 [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) 博客中给出了更精确的技术定义：

> **Workflows** are systems where LLMs and tools are orchestrated through predefined code paths.
> 
> **Workflow（工作流）** 是 LLM 和工具通过**预定义的代码路径**进行编排的系统。

> **Agents** are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.
> 
> **Agent（智能体）** 是 LLM **动态地**指导自身流程和工具使用的系统，LLM 对任务的完成方式保持控制权。

简单来说：

| | Workflow | Agent |
|---|----------|-------|
| **控制权** | 代码控制流程 | LLM 控制流程 |
| **执行路径** | 预定义、确定性 | 动态、非确定性 |
| **LLM 角色** | 执行特定步骤 | 决策 + 执行 |

## 核心观点：光谱而非二元对立

### Andrew Ng 的 "Agentic" 观点

吴恩达（Andrew Ng）提出了一个非常有洞察力的观点：

> Rather than having to choose whether or not something is an agent in a binary way, it would be more useful to think of systems as being **agent-like to different degrees**. Unlike the noun "agent," the adjective **"agentic"** allows us to contemplate such systems and include all of them in this growing movement.
> 
> 与其用二元方式选择某个系统是否是 Agent，不如思考系统的 **"agentic 程度"（agent-like to different degrees）**。不同于名词 "agent"，形容词 **"agentic"** 让我们能够思考并涵盖所有这类系统。

这个观点非常关键：**不要问"这是不是 Agent"，而要问"这个系统有多 agentic"**。

### 光谱模型

让我们用一个光谱来理解这个概念：

```
低 agentic 程度                                        高 agentic 程度
     │                                                      │
     ▼                                                      ▼
┌─────────┐   ┌─────────────┐   ┌─────────────┐   ┌────────┐   ┌──────────────┐
│   纯    │   │  带条件分支  │   │  带 LLM    │   │  受限  │   │    完全     │
│Workflow │ → │  的Workflow │ → │  路由的    │ → │ Agent  │ → │  自主Agent  │
│         │   │             │   │  Workflow  │   │        │   │             │
└─────────┘   └─────────────┘   └─────────────┘   └────────┘   └──────────────┘
     │              │                 │               │              │
  顺序执行       if/else           LLM决定         工具调用       完全由LLM
  固定步骤       条件判断          下一步          循环          驱动决策
```

让我们看几个具体的例子：

#### 1. 纯 Workflow（最左端）

```python
def process_document(doc):
    # 步骤完全固定，无任何动态决策
    text = extract_text(doc)
    summary = llm.summarize(text)
    translation = llm.translate(summary, target="en")
    return translation
```

这是一个典型的 Workflow：步骤固定、顺序执行、LLM 只是被调用来完成特定任务。

#### 2. 带条件分支的 Workflow

```python
def process_document(doc):
    text = extract_text(doc)
    
    # 有条件分支，但条件判断是确定性的
    if len(text) > 1000:
        summary = llm.summarize(text)
    else:
        summary = text
    
    if detect_language(text) != "en":
        return llm.translate(summary, target="en")
    return summary
```

#### 3. 带 LLM 路由的 Workflow

```python
def process_query(query):
    # LLM 参与路由决策
    intent = llm.classify_intent(query)  # ["search", "calculate", "chat"]
    
    if intent == "search":
        return search_pipeline(query)
    elif intent == "calculate":
        return calculation_pipeline(query)
    else:
        return chat_pipeline(query)
```

LLM 开始参与流程控制，但每个分支的执行路径仍然是预定义的。

#### 4. 受限 Agent

```python
def restricted_agent(query):
    tools = [search_tool, calculator_tool]
    max_iterations = 5
    
    for i in range(max_iterations):
        response = llm.decide_action(query, tools, history)
        if response.is_final:
            return response.answer
        
        # Agent 可以选择工具，但有迭代限制
        result = execute_tool(response.tool, response.args)
        history.append(result)
    
    return "达到最大迭代次数"
```

LLM 控制工具选择和执行流程，但有明确的约束（最大迭代次数、可用工具范围）。

#### 5. 完全自主 Agent（最右端）

```python
def autonomous_agent(goal):
    while not goal_achieved:
        # LLM 完全控制：分析、规划、执行、反思
        analysis = llm.analyze_current_state()
        plan = llm.create_plan(analysis)
        
        for step in plan:
            tool = llm.select_tool(step)
            result = execute_tool(tool)
            reflection = llm.reflect(result)
            
            if reflection.needs_replan:
                break
        
        goal_achieved = llm.evaluate_goal(goal)
```

LLM 完全控制整个流程，包括规划、执行、反思和重新规划。

### 生产环境中的现实

LangGraph 官方博客中有一个非常重要的观察：

> Nearly all of the "agentic systems" we see in production are a **combination** of "workflows" and "agents".
> 
> 我们在生产环境中看到的几乎所有"智能体系统"，都是 workflow 和 agent 的**混合体**。

这意味着：
- 不存在纯粹的 Agent 或纯粹的 Workflow
- 实际系统往往在光谱的不同位置组合多种模式
- 好的系统设计是找到**合适的 agentic 程度**

## 构建可靠 Agent 系统的核心挑战

在讨论如何选择之前，我们需要理解构建可靠 Agent 系统的核心挑战是什么。

### 核心难点：上下文工程（Context Engineering）

LangGraph 官方博客一针见血地指出：

> **The hard part of building reliable agentic systems is making sure the LLM has the appropriate context at each step.**
> 
> 构建可靠智能体系统的难点在于：**确保 LLM 在每一步都拥有适当的上下文**。

这包括两个方面：
1. **控制传入 LLM 的具体内容**
2. **运行适当的步骤来生成相关内容**

### LLM 为什么会出错？

LLM 在 Agent 系统中出错通常有两个原因：

1. **模型能力不足** —— 这需要等待模型进步
2. **上下文不当或不完整** —— 这是我们可以优化的

第二个原因在实际应用中更为常见，常见的问题包括：

| 问题类型 | 具体表现 |
|---------|---------|
| 系统提示不完整 | 缺少关键指令、约束或背景信息 |
| 用户输入模糊 | 用户意图不明确，缺少必要信息 |
| 工具访问问题 | 没有提供正确的工具，或工具描述不清 |
| 工具描述不佳 | 工具的功能、参数、返回值描述不准确 |
| 上下文传递不当 | 关键信息在步骤间丢失或被错误处理 |
| 工具响应格式差 | 工具返回的信息难以被 LLM 理解 |

### 框架的价值

理解了核心挑战后，我们就能明白 Agent 框架的真正价值：

> Any framework that makes it harder to control **exactly** what is being passed to the LLM is just getting in your way.
> 
> 任何让你更难控制**精确传递给 LLM 的内容**的框架，都是在妨碍你。

好的框架应该：
- ✅ 让你完全控制传入 LLM 的上下文
- ✅ 提供便利功能（持久化、流式处理、人机协作）
- ❌ 不应该过度抽象导致失去控制

## 如何选择：Workflow 还是 Agent？

### 决策矩阵

| 维度 | Workflow | Agent |
|------|----------|-------|
| **可预测性** | 高 ✅ | 低 ❌ |
| **灵活性** | 低 ❌ | 高 ✅ |
| **调试难度** | 低 ✅ | 高 ❌ |
| **成本** | 低 ✅ | 高 ❌ |
| **延迟** | 低 ✅ | 高 ❌ |
| **适用场景** | 明确定义的任务 | 需要灵活决策的任务 |

### Anthropic 的建议

Anthropic 在其博客中给出了非常务实的建议：

> When building applications with LLMs, we recommend finding the **simplest solution possible**, and only increasing complexity when needed. This might mean **not building agentic systems at all**.
> 
> 在构建 LLM 应用时，我们建议找到**最简单的可行方案**，只在需要时才增加复杂度。这可能意味着**根本不需要构建智能体系统**。

> When more complexity is warranted, **workflows** offer predictability and consistency for well-defined tasks, whereas **agents** are the better option when flexibility and model-driven decision-making are needed at scale.
> 
> 当需要更高复杂度时，**Workflow** 为定义明确的任务提供可预测性和一致性，而当需要大规模的灵活性和模型驱动决策时，**Agent** 是更好的选择。

### 实际决策流程

```
你的任务是否有明确、固定的步骤？
         │
         ├── 是 → 使用 Workflow
         │
         └── 否 → 任务是否需要动态决策？
                        │
                        ├── 否 → 使用带条件分支的 Workflow
                        │
                        └── 是 → 决策点是否可以枚举？
                                       │
                                       ├── 是 → 使用 LLM 路由 + 子 Workflow
                                       │
                                       └── 否 → 使用 Agent（带适当约束）
```

### 什么时候需要 Agent？

根据 OpenAI 和 Anthropic 的指南，以下情况更适合使用 Agent：

1. **任务复杂度高**：需要多步推理、工具组合使用
2. **执行路径不确定**：无法预先定义所有可能的分支
3. **需要适应性**：任务可能需要根据中间结果调整策略
4. **人工处理成本高**：任务足够复杂，值得承受 Agent 的额外成本和延迟

### 什么时候 Workflow 就够了？

1. **步骤明确**：任务可以分解为固定的步骤序列
2. **分支可枚举**：所有可能的执行路径都可以预先定义
3. **对延迟敏感**：需要快速响应
4. **成本敏感**：需要控制 API 调用次数
5. **需要高可靠性**：不能容忍不确定的行为

## LangGraph 的设计哲学

LangGraph 的定位非常清晰：

> LangGraph is best thought of as an **orchestration framework** (with both declarative and imperative APIs), with a series of agent abstractions built on top.
> 
> LangGraph 最好被理解为一个**编排框架**（同时支持声明式和命令式 API），在此基础上构建了一系列 Agent 抽象。

### 不只是 Agent 抽象

很多 Agent 框架只提供了高级抽象（比如 OpenAI Agents SDK），这让入门变得简单，但也带来了问题：

- 难以控制传入 LLM 的精确内容
- 难以实现自定义的流程逻辑
- 难以调试和优化

LangGraph 的不同之处在于：
- 提供底层的编排能力（图、节点、边）
- 在此基础上提供高级 Agent 抽象
- 开发者可以在任意抽象层次工作

### 关键特性

无论你构建的是 Workflow 还是 Agent，都能从以下特性中受益：

| 特性 | 说明 |
|-----|------|
| **持久化（Persistence）** | 保存和恢复执行状态 |
| **流式处理（Streaming）** | 实时返回中间结果 |
| **人机协作（Human-in-the-loop）** | 在关键节点引入人工审核 |
| **容错（Fault Tolerance）** | 处理失败和重试 |
| **调试/可观测性** | 追踪和分析执行过程 |

## 实践建议

### 1. 从简单开始

```
原则：Start simple, add complexity only when needed.
从简单开始，只在需要时增加复杂度。
```

不要一上来就构建复杂的 Agent 系统。从 Workflow 开始，验证核心逻辑，然后逐步增加 agentic 特性。

### 2. 专注于上下文工程

无论使用什么框架，都要确保：
- 系统提示清晰、完整、具体
- 工具描述准确、详细
- 关键上下文在步骤间正确传递
- 工具响应格式化为 LLM 友好的形式

### 3. 设置适当的约束

即使需要 Agent 的灵活性，也要设置合理的约束：
- 最大迭代次数
- 超时限制
- 可用工具范围
- 关键操作的人工审核

### 4. 建立可观测性

Agent 系统的调试比 Workflow 困难得多，需要：
- 完整的执行日志
- LLM 输入/输出记录
- 工具调用追踪
- 决策路径可视化

### 5. 混合使用

实际项目中，最佳实践往往是：
- 用 Workflow 处理确定性的部分
- 用 Agent 处理需要灵活决策的部分
- 通过清晰的接口组合两者

```python
def hybrid_system(query):
    # Workflow 部分：固定的预处理
    processed = preprocess_workflow(query)
    
    # Agent 部分：灵活的信息收集
    info = research_agent(processed)
    
    # Workflow 部分：固定的后处理
    result = postprocess_workflow(info)
    
    return result
```

## 总结

回到我们的核心观点：**Workflow 和 Agent 本质上是一个光谱**。

关键 takeaways：

1. **不要陷入二元思维**：不是"要不要用 Agent"的问题，而是"需要多少 agentic 程度"的问题。

2. **从简单开始**：Workflow 在很多场景下就是最佳选择，不要被 Agent 的热度迷惑。

3. **理解核心挑战**：可靠 Agent 系统的难点是上下文工程，选择能让你控制上下文的框架和方法。

4. **混合是常态**：生产环境的系统几乎都是 Workflow 和 Agent 的混合体。

5. **框架是工具**：好的框架应该提供灵活性和控制力，而不是限制你的选择。

最后，用 Andrew Ng 的话作为结尾：

> Think in terms of **"agentic"** rather than **"agent"**.
> 
> 用 **"agentic"** 而非 **"agent"** 来思考。

选择合适的 agentic 程度，而不是纠结于是否构建了一个"真正的 Agent"。

---

## 参考资料

- [How to think about agent frameworks - LangChain Blog](https://blog.langchain.com/how-to-think-about-agent-frameworks/)
- [Building Effective Agents - Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI Guide on Building Agents](https://platform.openai.com/docs/guides/agents)

