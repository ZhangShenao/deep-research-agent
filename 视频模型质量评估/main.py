# -*- coding: utf-8 -*-
"""
视频生成测试主入口
"""
import sys
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core_executor import VideoTestExecutor

# 导入各个策略
from fal.strategy import FalStrategy
from sora2.strategy import Sora2Strategy
from wan.strategy import WanStrategy
from wavespeed.strategy import WaveSpeedStrategy
from ltx2.strategy import LTX2Strategy
from gaga.strategy import GagaStrategy


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="视频生成测试工具")
    parser.add_argument(
        "--model",
        type=str,
        choices=["fal", "sora2", "wan", "wavespeed", "ltx2", "gaga"],
        required=True,
        help="选择视频生成模型",
    )
    parser.add_argument(
        "--hide-name", action="store_true", help="隐藏角色名（替换为'this character'）"
    )

    args = parser.parse_args()

    # 根据模型选择策略
    model_name = args.model
    hide_name = args.hide_name

    try:
        if model_name == "fal":
            strategy = FalStrategy()
        elif model_name == "sora2":
            strategy = Sora2Strategy()
        elif model_name == "wan":
            strategy = WanStrategy()
        elif model_name == "wavespeed":
            strategy = WaveSpeedStrategy()
        elif model_name == "ltx2":
            strategy = LTX2Strategy()
        elif model_name == "gaga":
            strategy = GagaStrategy()
        else:
            print(f"未知的模型: {model_name}")
            return

        # 创建执行器并运行测试
        executor = VideoTestExecutor(
            strategy=strategy, model_name=model_name, hide_name=hide_name
        )

        executor.run_batch_test()

    except Exception as e:
        print(f"运行测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
