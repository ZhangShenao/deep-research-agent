# -*- coding: utf-8 -*-
"""
测试导入和基本功能
"""
import sys
from pathlib import Path

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        from state import GameState
        print("✅ state 模块导入成功")
    except Exception as e:
        print(f"❌ state 模块导入失败: {e}")
        return False
    
    try:
        from llm import DEEPSEEK
        print("✅ llm 模块导入成功")
    except Exception as e:
        print(f"❌ llm 模块导入失败: {e}")
        return False
    
    try:
        from sora2_client import Sora2Client
        print("✅ sora2_client 模块导入成功")
    except Exception as e:
        print(f"❌ sora2_client 模块导入失败: {e}")
        return False
    
    try:
        from worldview import get_default_worldview
        worldview = get_default_worldview()
        print(f"✅ worldview 模块导入成功 (长度: {len(worldview)} 字符)")
    except Exception as e:
        print(f"❌ worldview 模块导入失败: {e}")
        return False
    
    try:
        from prompts import STORY_CONTINUATION_PROMPT, STORYBOARD_PROMPT
        print("✅ prompts 模块导入成功")
    except Exception as e:
        print(f"❌ prompts 模块导入失败: {e}")
        return False
    
    try:
        from utils import ensure_data_dir, get_next_story_index, get_next_video_index
        ensure_data_dir()
        print("✅ utils 模块导入成功")
    except Exception as e:
        print(f"❌ utils 模块导入失败: {e}")
        return False
    
    try:
        from nodes import (
            story_continuation_node,
            storyboard_node,
            extract_frame_node,
            video_generation_node,
        )
        print("✅ nodes 模块导入成功")
    except Exception as e:
        print(f"❌ nodes 模块导入失败: {e}")
        return False
    
    try:
        from agent import build_agent
        print("✅ agent 模块导入成功")
    except Exception as e:
        print(f"❌ agent 模块导入失败: {e}")
        return False
    
    print("\n✅ 所有模块导入测试通过！")
    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

