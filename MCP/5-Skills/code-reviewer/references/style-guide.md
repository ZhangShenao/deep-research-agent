# 代码风格指南

本文档定义代码审查时参考的编码规范和最佳实践。

---

## 1. 通用原则

### 1.1 清晰优于简洁

```python
# ❌ 过于简洁，难以理解
x = [i for i in range(10) if i % 2 == 0 and i > 4]

# ✅ 清晰易懂
even_numbers = []
for number in range(10):
    if number % 2 == 0 and number > 4:
        even_numbers.append(number)
```

### 1.2 显式优于隐式

```python
# ❌ 隐式依赖
from utils import *

# ✅ 显式导入
from utils import format_date, validate_email
```

### 1.3 简单优于复杂

```python
# ❌ 过度设计
class UserFactory:
    def create_user(self, **kwargs):
        return UserBuilder().set_name(kwargs['name']).set_email(kwargs['email']).build()

# ✅ 简单直接
def create_user(name: str, email: str) -> User:
    return User(name=name, email=email)
```

---

## 2. 命名规范

### 2.1 命名风格

| 类型 | 风格 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_name`, `total_count` |
| 常量 | UPPER_SNAKE_CASE | `MAX_CONNECTIONS`, `API_KEY` |
| 函数 | snake_case | `get_user()`, `calculate_total()` |
| 类名 | PascalCase | `UserService`, `HttpClient` |
| 私有成员 | _prefix | `_internal_state`, `_helper()` |
| 保护成员 | __prefix | `__private_method()` |

### 2.2 命名原则

#### 变量命名

```python
# ❌ 模糊的命名
d = get_data()
temp = process(d)
x = temp[0]

# ✅ 清晰的命名
user_data = get_user_data()
processed_users = process_users(user_data)
first_user = processed_users[0]
```

#### 布尔变量

```python
# ❌ 不清晰
flag = True
status = False

# ✅ 清晰表达含义
is_active = True
has_permission = False
can_edit = True
```

#### 函数命名

```python
# ❌ 模糊的函数名
def do_stuff(data):
    pass

def handle(item):
    pass

# ✅ 动词开头，清晰表达功能
def validate_user_input(data: dict) -> bool:
    pass

def process_payment(order: Order) -> PaymentResult:
    pass

def send_notification(user: User, message: str) -> None:
    pass
```

---

## 3. 函数设计

### 3.1 单一职责

```python
# ❌ 职责过多
def process_order(order):
    validate_order(order)
    calculate_total(order)
    apply_discount(order)
    charge_payment(order)
    send_confirmation_email(order)
    update_inventory(order)

# ✅ 单一职责，组合使用
def process_order(order: Order) -> ProcessResult:
    validated_order = validate_order(order)
    priced_order = calculate_pricing(validated_order)
    payment_result = process_payment(priced_order)
    notify_customer(order, payment_result)
    return ProcessResult(order, payment_result)
```

### 3.2 参数数量

```python
# ❌ 参数过多
def create_user(name, email, age, address, phone, role, department, manager, start_date):
    pass

# ✅ 使用数据类
@dataclass
class UserCreateRequest:
    name: str
    email: str
    age: int
    address: str
    phone: str
    role: str
    department: str
    manager: str
    start_date: date

def create_user(request: UserCreateRequest) -> User:
    pass
```

### 3.3 返回值

```python
# ❌ 混合返回类型
def get_user(user_id):
    user = db.find(user_id)
    if user:
        return user
    return None  # 有时返回 User，有时返回 None

# ✅ 使用 Optional 或 Result 类型
from typing import Optional

def get_user(user_id: int) -> Optional[User]:
    """获取用户，如果不存在返回 None"""
    return db.find(user_id)

# 或者抛出异常
def get_user(user_id: int) -> User:
    """获取用户，如果不存在抛出异常"""
    user = db.find(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

---

## 4. 错误处理

### 4.1 异常捕获

```python
# ❌ 裸 except
try:
    process_data(data)
except:
    pass

# ❌ 捕获 Exception 但不处理
try:
    process_data(data)
except Exception:
    pass

# ✅ 捕获特定异常
try:
    process_data(data)
except ValueError as e:
    logger.warning(f"Invalid data format: {e}")
    raise InvalidDataError(str(e)) from e
except IOError as e:
    logger.error(f"IO error: {e}")
    raise DataAccessError(str(e)) from e
```

### 4.2 错误信息

```python
# ❌ 模糊的错误信息
raise ValueError("Invalid input")

# ✅ 具体的错误信息
raise ValueError(
    f"User age must be between 0 and 150, got {age}"
)
```

### 4.3 资源清理

```python
# ❌ 可能的资源泄漏
file = open('data.txt')
data = file.read()
process(data)
file.close()  # 如果 process() 抛出异常，文件不会关闭

# ✅ 使用上下文管理器
with open('data.txt') as file:
    data = file.read()
    process(data)
```

---

## 5. 代码组织

### 5.1 导入顺序

```python
# 标准库
import os
import sys
from datetime import datetime

# 第三方库
import requests
from sqlalchemy import Column, String

# 本地模块
from myapp.models import User
from myapp.utils import format_date
```

### 5.2 类结构

```python
class UserService:
    """用户服务类
    
    负责用户相关的业务逻辑处理。
    """
    
    # 类常量
    MAX_LOGIN_ATTEMPTS = 5
    
    def __init__(self, db: Database, cache: Cache):
        """初始化服务
        
        Args:
            db: 数据库连接
            cache: 缓存服务
        """
        self._db = db
        self._cache = cache
    
    # 公共方法
    def get_user(self, user_id: int) -> User:
        """获取用户"""
        pass
    
    def create_user(self, data: UserCreateRequest) -> User:
        """创建用户"""
        pass
    
    # 私有方法
    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pass
```

---

## 6. 文档和注释

### 6.1 Docstring 格式

```python
def calculate_discount(
    price: float,
    discount_rate: float,
    max_discount: float = 100.0
) -> float:
    """计算折扣后的价格
    
    根据折扣率计算最终价格，确保折扣不超过最大限制。
    
    Args:
        price: 原始价格，必须为正数
        discount_rate: 折扣率，范围 0-1
        max_discount: 最大折扣金额，默认 100.0
    
    Returns:
        折扣后的价格
    
    Raises:
        ValueError: 如果 price 为负数或 discount_rate 不在 0-1 范围内
    
    Examples:
        >>> calculate_discount(100, 0.2)
        80.0
        >>> calculate_discount(100, 0.5, max_discount=30)
        70.0
    """
    if price < 0:
        raise ValueError(f"Price must be positive, got {price}")
    if not 0 <= discount_rate <= 1:
        raise ValueError(f"Discount rate must be between 0 and 1, got {discount_rate}")
    
    discount = min(price * discount_rate, max_discount)
    return price - discount
```

### 6.2 注释原则

```python
# ❌ 描述"做什么"的注释（代码已经说明）
# 遍历用户列表
for user in users:
    # 检查用户是否活跃
    if user.is_active:
        # 发送邮件
        send_email(user)

# ✅ 解释"为什么"的注释
# 只处理活跃用户，因为非活跃用户的邮箱可能已失效
for user in users:
    if user.is_active:
        send_email(user)

# ✅ 解释复杂逻辑
# 使用位运算优化：x & (x-1) 会清除最低位的 1
# 如果结果为 0，说明 x 只有一个 1 位，即 x 是 2 的幂
def is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0
```

---

## 7. 安全规范

### 7.1 SQL 查询

```python
# ❌ SQL 注入风险
query = f"SELECT * FROM users WHERE name = '{name}'"
cursor.execute(query)

# ✅ 参数化查询
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (name,))

# ✅ 使用 ORM
User.objects.filter(name=name)
```

### 7.2 敏感信息

```python
# ❌ 硬编码敏感信息
API_KEY = "sk-12345abcdef"
DATABASE_PASSWORD = "super_secret_password"

# ✅ 使用环境变量
import os

API_KEY = os.environ.get("API_KEY")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

# ✅ 使用配置文件（不要提交到版本控制）
from config import settings

API_KEY = settings.api_key
```

### 7.3 输入验证

```python
# ❌ 信任用户输入
def process_file(filename):
    with open(filename) as f:
        return f.read()

# ✅ 验证和清理用户输入
import os
from pathlib import Path

ALLOWED_DIR = Path("/app/uploads")

def process_file(filename: str) -> str:
    # 规范化路径，防止目录遍历攻击
    safe_path = ALLOWED_DIR / Path(filename).name
    
    if not safe_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    if not safe_path.is_relative_to(ALLOWED_DIR):
        raise SecurityError("Access denied: path traversal detected")
    
    with open(safe_path) as f:
        return f.read()
```

---

## 8. 性能建议

### 8.1 避免 N+1 查询

```python
# ❌ N+1 查询
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # 每次循环都查询 profile

# ✅ 预加载关联数据
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.bio)
```

### 8.2 使用生成器

```python
# ❌ 一次性加载所有数据到内存
def get_all_lines(filename):
    with open(filename) as f:
        return f.readlines()  # 大文件会消耗大量内存

# ✅ 使用生成器逐行处理
def get_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()
```

### 8.3 合理使用缓存

```python
from functools import lru_cache

# ✅ 缓存计算密集型函数的结果
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

---

## 参考资源

- [PEP 8 -- Python 代码风格指南](https://pep8.org/)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)
- [Real Python 代码质量指南](https://realpython.com/python-code-quality/)

