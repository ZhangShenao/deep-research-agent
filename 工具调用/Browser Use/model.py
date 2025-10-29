# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/29 20:11
@Author  : ZhangShenao
@File    : model.py
@Desc    : 数据模型定义
"""

from pydantic import BaseModel
from pydantic import Field


class WeatherInfo(BaseModel):
    """
    天气信息
    """

    city: str = Field(description="城市名称")
    high_temperature: float = Field(description="最高温度")
    low_temperature: float = Field(description="最低温度")
    wind_power: float = Field(description="风力")
