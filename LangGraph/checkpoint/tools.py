# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : tools.py
@Desc    : 客服 Agent 工具定义
"""

from langchain_core.tools import tool
from langgraph.types import interrupt


# 模拟商品数据库
PRODUCTS_DB = {
    "iPhone 15": {
        "price": 6999,
        "stock": 100,
        "description": "Apple iPhone 15，A16芯片，6.1英寸超视网膜XDR显示屏"
    },
    "iPhone 15 Pro": {
        "price": 8999,
        "stock": 50,
        "description": "Apple iPhone 15 Pro，A17 Pro芯片，钛金属设计"
    },
    "MacBook Pro": {
        "price": 14999,
        "stock": 30,
        "description": "Apple MacBook Pro 14英寸，M3 Pro芯片"
    },
    "AirPods Pro": {
        "price": 1899,
        "stock": 200,
        "description": "Apple AirPods Pro 第二代，主动降噪"
    },
    "iPad Air": {
        "price": 4799,
        "stock": 80,
        "description": "Apple iPad Air，M1芯片，10.9英寸"
    }
}

# 模拟订单数据库
ORDERS_DB = {
    "ORD001": {
        "user_id": "user-001",
        "product": "iPhone 15",
        "status": "已发货",
        "tracking_number": "SF123456789",
        "estimated_delivery": "2025-12-08"
    },
    "ORD002": {
        "user_id": "user-001",
        "product": "AirPods Pro",
        "status": "待发货",
        "tracking_number": None,
        "estimated_delivery": "2025-12-10"
    },
    "ORD003": {
        "user_id": "user-002",
        "product": "MacBook Pro",
        "status": "已签收",
        "tracking_number": "YT987654321",
        "estimated_delivery": None
    }
}


@tool
def query_product_price(product_name: str) -> str:
    """
    查询商品价格
    
    Args:
        product_name: 商品名称，如 "iPhone 15", "MacBook Pro" 等
        
    Returns:
        商品价格信息
    """
    # 精确匹配
    if product_name in PRODUCTS_DB:
        product = PRODUCTS_DB[product_name]
        return f"{product_name} 的价格是 {product['price']} 元"
    
    # 模糊匹配
    for name, product in PRODUCTS_DB.items():
        if product_name.lower() in name.lower():
            return f"{name} 的价格是 {product['price']} 元"
    
    # 未找到
    available_products = ", ".join(PRODUCTS_DB.keys())
    return f"未找到商品「{product_name}」。目前可查询的商品有：{available_products}"


@tool
def query_product_stock(product_name: str) -> str:
    """
    查询商品库存
    
    Args:
        product_name: 商品名称
        
    Returns:
        商品库存信息
    """
    # 精确匹配
    if product_name in PRODUCTS_DB:
        product = PRODUCTS_DB[product_name]
        stock = product['stock']
        if stock > 50:
            status = "库存充足"
        elif stock > 10:
            status = "库存紧张"
        else:
            status = "即将售罄"
        return f"{product_name} 当前库存 {stock} 件，{status}"
    
    # 模糊匹配
    for name, product in PRODUCTS_DB.items():
        if product_name.lower() in name.lower():
            stock = product['stock']
            if stock > 50:
                status = "库存充足"
            elif stock > 10:
                status = "库存紧张"
            else:
                status = "即将售罄"
            return f"{name} 当前库存 {stock} 件，{status}"
    
    return f"未找到商品「{product_name}」的库存信息"


@tool
def query_product_info(product_name: str) -> str:
    """
    查询商品详细信息
    
    Args:
        product_name: 商品名称
        
    Returns:
        商品详细信息，包括价格、库存、描述
    """
    # 精确匹配
    if product_name in PRODUCTS_DB:
        product = PRODUCTS_DB[product_name]
        return f"""商品：{product_name}
价格：{product['price']} 元
库存：{product['stock']} 件
描述：{product['description']}"""
    
    # 模糊匹配
    for name, product in PRODUCTS_DB.items():
        if product_name.lower() in name.lower():
            return f"""商品：{name}
价格：{product['price']} 元
库存：{product['stock']} 件
描述：{product['description']}"""
    
    return f"未找到商品「{product_name}」的信息"


@tool
def query_order_status(order_id: str) -> str:
    """
    查询订单状态
    
    Args:
        order_id: 订单号，如 "ORD001"
        
    Returns:
        订单状态信息
    """
    order_id = order_id.upper()
    
    if order_id in ORDERS_DB:
        order = ORDERS_DB[order_id]
        result = f"""订单号：{order_id}
商品：{order['product']}
状态：{order['status']}"""
        
        if order['tracking_number']:
            result += f"\n快递单号：{order['tracking_number']}"
        
        if order['estimated_delivery']:
            result += f"\n预计送达：{order['estimated_delivery']}"
        
        return result
    
    return f"未找到订单号「{order_id}」，请检查订单号是否正确"


@tool
def list_available_products() -> str:
    """
    列出所有可购买的商品
    
    Returns:
        商品列表
    """
    result = "目前可购买的商品：\n"
    for name, product in PRODUCTS_DB.items():
        result += f"- {name}: {product['price']}元\n"
    return result.strip()


@tool
def ask_human(question: str) -> str:
    """
    向人类客服请求帮助
    
    当遇到无法处理的问题时，使用此工具向人类客服请求帮助。
    
    Args:
        question: 需要向人类客服询问的问题
        
    Returns:
        人类客服的回答
    """
    print(f"\n🙋 [需要人工介入] {question}")
    
    # 使用 interrupt 暂停执行，等待人类输入
    human_response = interrupt({"question": question})
    
    print(f"✅ [人工回复] {human_response}")
    
    return human_response


# 导出所有工具
ALL_TOOLS = [
    query_product_price,
    query_product_stock,
    query_product_info,
    query_order_status,
    list_available_products,
    ask_human,
]

