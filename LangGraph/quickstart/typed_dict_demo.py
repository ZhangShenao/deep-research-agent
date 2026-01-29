# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/28
@Author  : ZhangShenao
@File    : typed_dict_demo.py
@Desc    : TypedDict 示例

TypedDict 原理详解：

1. 什么是 TypedDict？
   TypedDict 是 Python 3.8+ 引入的一个类型工具，用于为字典提供结构化的类型注解。
   它允许你定义一个字典应该包含哪些键，以及每个键对应的值类型。

2. 核心特性：
   - 运行时行为：TypedDict 在运行时本质上是普通 dict，不会进行类型检查
   - 静态类型检查：主要用于 mypy、pyright 等静态类型检查器，提供类型推断
   - 键约束：定义了字典应该包含的键集合（可选或必需）
   - 值类型标注：为每个键指定预期的值类型

3. 类型注解 vs 运行时验证：
   - 类型注解：只用于静态分析（IDE 提示、类型检查器）
   - 运行时验证：默认不执行，需要手动实现或使用 pydantic 等库
   - Python 的类型系统是可选的，解释器不会强制执行

4. 常见使用场景：
   - API 请求/响应的参数结构定义
   - 配置文件的数据结构
   - 函数返回值的多键字典结构
   - LangGraph 中的状态定义（State 定义）

5. TypedDict 的工作机制：
   - 继承自 dict，运行时就是普通字典
   - 使用类语法定义结构，更清晰易读
   - 类型检查器会根据定义进行静态检查
   - 支持 total=False 标记可选键

6. 示例对比：
   运行时错误：
   - 访问不存在的键：user["phone"] → KeyError（这是 dict 的标准行为）
   - 类型不匹配的赋值：user["age"] = "34" → 不报错（运行时不检查）

   静态类型检查错误：
   - 缺少必需键：User = {"name": "zsa"} → 类型检查器报错
   - 类型不匹配：user["age"] = "34" → mypy/pyright 报错
"""

from typing import TypedDict


# 定义一个 TypedDict 类，用于定义用户信息
# TypedDict 是一个泛型类，用于定义一个字典，字典的键和值都是类型化的
# 它可以限定一个dict中包含哪些键，以及这些键的值的类型
class User(TypedDict):
    name: str
    age: int
    email: str


user: User = {"name": "zsa", "age": 34, "email": "zsa@example.com"}
print(user)

# 当尝试访问一个不存在的键时，会抛出 KeyError 异常
# print(user["phone"])

# 注意：TypedDict 不会在运行时检查类型，这里虽然类型不匹配但不会报错
# 类型不匹配的错误只会在使用 mypy、pyright 等静态类型检查器时才会提示
user["age"] = "34"
print(user)
