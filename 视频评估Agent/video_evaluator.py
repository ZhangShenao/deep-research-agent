# -*- coding: utf-8 -*-
"""
使用 Gemini 2.5 Flash 对视频进行多维度评分
- 评分维度（1~10分，支持小数）：
  1) 信息密度（Information Density）：剧情传递的信息含量
  2) 一致性（Consistency）：视频每一帧中的人物和场景是否都保持一致
  3) 流畅度（Fluency）：视频中人物动作和镜头切换等是否流畅
  4) 音画同步性（Audio-Visual Synchronization）：视频中的声音和图像是否一致
  5) 画面质量（Visual Quality）：是否存在丢帧、卡顿等画面质量问题
- 返回每个视频的 JSON 评分结果（包含各维度分数、打分原因、总分）
- 指定目录后，批量评估并输出所有视频的平均分

环境变量：
- GEMINI_API_KEY
"""
import os
import sys
import json
import argparse
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# 官方 SDK： https://ai.google.dev/gemini-api/docs/video-understanding?hl=zh-cn
from google import genai  # pip install google-genai


SUPPORTED_EXTS = {
    ".mp4",
    ".mpeg",
    ".mov",
    ".avi",
    ".x-flv",
    ".mpg",
    ".webm",
    ".wmv",
    ".3gpp",
}

EVAL_PROMPT = (
    "你是一个严格的视频评估专家。请基于视频内容，从以下5个维度给出1~10的分数（支持小数），并给出简要原因：\n\n"
    "1) 信息密度：剧情传递的信息含量\n"
    "2) 一致性：视频每一帧中的人物和场景是否都保持一致\n"
    "3) 流畅度：视频中人物动作和镜头切换等是否流畅\n"
    "4) 音画同步性：视频中的声音和图像是否一致\n"
    "5) 画面质量：是否存在丢帧、卡顿等画面质量问题\n\n"
    "请只输出 JSON，字段为：\n"
    "{\n"
    '  "information_density": float,\n'
    '  "consistency": float,\n'
    '  "fluency": float,\n'
    '  "audio_visual_synchronization": float,\n'
    '  "visual_quality": float,\n'
    '  "reasons": {\n'
    '    "information_density": string,\n'
    '    "consistency": string,\n'
    '    "fluency": string,\n'
    '    "audio_visual_synchronization": string,\n'
    '    "visual_quality": string\n'
    "  },\n"
    '  "total": float\n'
    "}\n\n"
    "注意：所有分数必须在1.0到10.0之间（支持小数）。总分为五项分数之和（范围5.0~50.0）。"
)


def is_video_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in SUPPORTED_EXTS


def wait_for_file_active(
    client: genai.Client, file_resource, max_wait_time: int = 300
) -> None:
    """
    等待文件处理完成，状态变为 ACTIVE。

    Args:
        client: Gemini 客户端
        file_resource: 文件资源对象
        max_wait_time: 最大等待时间（秒），默认5分钟
    """
    # 获取文件名称或ID
    file_name = None
    if hasattr(file_resource, "name"):
        file_name = file_resource.name
    elif hasattr(file_resource, "uri"):
        # 从URI中提取文件名（格式通常是 files/filename）
        uri = file_resource.uri
        if "/" in uri:
            file_name = uri.split("/")[-1]
        else:
            file_name = uri
    else:
        # 如果都没有，尝试直接使用
        file_name = str(file_resource)

    # 首先检查上传返回的文件对象是否有状态
    if hasattr(file_resource, "state") and file_resource.state == "ACTIVE":
        return

    # 轮询文件状态
    start_time = time.time()
    last_state = None

    while time.time() - start_time < max_wait_time:
        try:
            # 重新获取文件状态
            file_info = client.files.get(name=file_name)

            # 获取状态（可能是 state 或 status 属性）
            state = getattr(file_info, "state", None) or getattr(
                file_info, "status", None
            )

            if state != last_state:
                print(f"  文件状态: {state}")
                last_state = state

            if state == "ACTIVE":
                return
            elif state == "FAILED":
                raise RuntimeError(f"文件处理失败: {file_name}")

            # 等待一段时间再检查
            time.sleep(2)
        except AttributeError as e:
            # 如果获取状态失败，可能是文件对象结构不同，尝试直接使用
            print(f"  无法获取文件状态，尝试直接使用文件...")
            # 如果已经有URI，可能可以直接使用
            if hasattr(file_resource, "uri"):
                return
            time.sleep(2)
        except Exception as e:
            # 其他错误，继续等待
            print(f"  检查文件状态时出错: {e}，继续等待...")
            time.sleep(2)

    # 超时
    raise TimeoutError(f"文件处理超时（{max_wait_time}秒），文件: {file_name}")


def safe_parse_json(text: str) -> Dict[str, Any]:
    """尽量从模型输出中解析 JSON（清理代码块围栏等）。"""
    s = text.strip()
    if s.startswith("```"):
        # 去掉可能的代码围栏
        s = s.strip("`")
        # 再次尝试找到第一个 '{'
        idx = s.find("{")
        if idx != -1:
            s = s[idx:]
        # 去掉末尾多余字符
        last = s.rfind("}")
        if last != -1:
            s = s[: last + 1]
    return json.loads(s)


def evaluate_single_video(
    client: genai.Client, model: str, video_path: str
) -> Dict[str, Any]:
    """对单个视频进行评估，返回 JSON 结果。"""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频不存在: {video_path}")

    # 上传文件到 Files API（适用于 >20MB 或复用场景）
    uploaded = client.files.upload(file=video_path)

    # 等待文件处理完成（状态变为 ACTIVE）
    print(f"  上传完成，等待处理中...")
    wait_for_file_active(client, uploaded)
    print(f"  文件处理完成，开始评估...")

    # 调用模型进行视频理解
    resp = client.models.generate_content(
        model=model,
        contents=[uploaded, EVAL_PROMPT],
    )

    # 解析为 JSON
    result = safe_parse_json(resp.text)

    # 补充元信息
    result["video_path"] = video_path
    return result


def aggregate_scores(results: List[Dict[str, Any]]) -> Tuple[Dict[str, float], float]:
    """计算各维度与总分的平均值。"""
    if not results:
        return {}, 0.0

    dims = [
        "information_density",
        "consistency",
        "fluency",
        "audio_visual_synchronization",
        "visual_quality",
    ]

    sums = {k: 0.0 for k in dims}
    total_sum = 0.0

    for r in results:
        for k in dims:
            sums[k] += float(r.get(k, 0))
        total_sum += float(r.get("total", 0))

    n = float(len(results))
    avg_dims = {k: (sums[k] / n) for k in dims}
    avg_total = total_sum / n
    return avg_dims, avg_total


def main() -> None:
    parser = argparse.ArgumentParser(description="使用 Gemini 对目录内视频进行评分")
    parser.add_argument("--dir", required=True, help="待评估的视频目录")
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini 模型名（默认 gemini-2.5-flash）",
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="是否将评估结果保存为 JSON 报告到目录下",
    )

    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误：未找到 GEMINI_API_KEY 环境变量")
        sys.exit(1)

    target_dir = os.path.abspath(args.dir)
    if not os.path.isdir(target_dir):
        print(f"错误：目录不存在或不可读：{target_dir}")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # 收集目录下所有视频文件
    video_files: List[str] = []
    for name in sorted(os.listdir(target_dir)):
        path = os.path.join(target_dir, name)
        if os.path.isfile(path) and is_video_file(path):
            video_files.append(path)

    if not video_files:
        print("未在目录中发现可评估的视频文件。")
        sys.exit(0)

    print(f"发现 {len(video_files)} 个视频，开始评估……\n")

    all_results: List[Dict[str, Any]] = []
    for i, vp in enumerate(video_files, 1):
        print(f"[{i}/{len(video_files)}] 评估: {os.path.basename(vp)}")
        try:
            res = evaluate_single_video(client, args.model, vp)
            all_results.append(res)
            print(
                f"  -> total={res.get('total')} | information_density={res.get('information_density')} "
                f"| consistency={res.get('consistency')} | fluency={res.get('fluency')} "
                f"| audio_visual_synchronization={res.get('audio_visual_synchronization')} "
                f"| visual_quality={res.get('visual_quality')}"
            )
        except Exception as e:
            print(f"  评估失败: {e}")

    # 统计平均分
    avg_dims, avg_total = aggregate_scores(all_results)

    print("\n====== 评估完成（平均分） ======")
    if all_results:
        for k, v in avg_dims.items():
            print(f"{k}: {v:.2f}")
        print(f"total: {avg_total:.2f}")
    else:
        print("无可用结果")

    # 可选保存报告
    if args.save_report and all_results:
        report = {
            "evaluated_videos": len(all_results),
            "results": all_results,
            "average": {
                **avg_dims,
                "total": avg_total,
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": args.model,
        }
        report_path = os.path.join(
            target_dir,
            f"gemini_eval_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存: {report_path}")
        except Exception as e:
            print(f"保存报告失败: {e}")


if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    main()
