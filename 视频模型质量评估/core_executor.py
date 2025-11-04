# -*- coding: utf-8 -*-
"""
核心执行流程，包含通用的测试流程逻辑
"""
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_strategy import VideoGenerationStrategy


class VideoTestExecutor:
    """视频测试执行器，负责执行通用的测试流程"""
    
    def __init__(
        self, 
        strategy: VideoGenerationStrategy,
        model_name: str,
        hide_name: bool = False,
        base_dir: Optional[str] = None
    ):
        """
        初始化执行器
        
        Args:
            strategy: 视频生成策略
            model_name: 模型名称（用于目录命名）
            hide_name: 是否隐藏角色名（替换为"this character"）
            base_dir: 基础目录路径（默认为当前脚本目录）
        """
        self.strategy = strategy
        self.model_name = model_name
        self.hide_name = hide_name
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        
        # 确定输出目录名称
        output_suffix = "hidden_name" if hide_name else "with_name"
        self.output_dir = os.path.join(self.base_dir, f"{model_name}_{output_suffix}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 统计信息
        self.results: List[Dict[str, Any]] = []
        self.total_tests = 0
        self.successful_tests = 0
        self.failed_tests = 0
        
        # 路径配置
        self.prompt_file = os.path.join(self.base_dir, "prompt.txt")
        self.pics_dir = os.path.join(self.base_dir, "pics")
    
    def read_prompts(self) -> List[Dict[str, str]]:
        """读取prompt文件并解析"""
        prompts = []
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and " - " in line:
                        parts = line.split(" - ", 1)
                        if len(parts) == 2:
                            char_name = parts[0].strip()
                            action = parts[1].strip()
                            prompts.append({
                                "line_num": line_num,
                                "char_name": char_name,
                                "action": action,
                                "full_prompt": f"{char_name} {action}",
                            })
                        else:
                            print(f"警告: 第{line_num}行格式不正确: {line}")
                    elif line:
                        print(f"警告: 第{line_num}行格式不正确: {line}")
        except FileNotFoundError:
            print(f"错误: 找不到文件 {self.prompt_file}")
            return []
        except Exception as e:
            print(f"错误: 读取文件时发生异常: {e}")
            return []
        
        return prompts
    
    def get_reference_image_path(self, char_name: str) -> Optional[str]:
        """获取参考图片路径"""
        image_path = os.path.join(self.pics_dir, f"{char_name}.png")
        if os.path.exists(image_path):
            return image_path
        return None
    
    def process_prompt(self, prompt: str, char_name: str) -> str:
        """处理prompt，根据hide_name参数决定是否替换角色名"""
        if self.hide_name:
            return prompt.replace(char_name, "this character")
        return prompt
    
    def generate_single_video(self, prompt_data: Dict[str, str]) -> Dict[str, Any]:
        """生成单个视频"""
        char_name = prompt_data["char_name"]
        full_prompt = prompt_data["full_prompt"]
        
        # 处理prompt（是否隐藏角色名）
        processed_prompt = self.process_prompt(full_prompt, char_name)
        
        print(f"\n开始生成视频: {char_name}")
        print(f"Prompt: {processed_prompt}")
        
        result: Dict[str, Any] = {
            "char_name": char_name,
            "prompt": processed_prompt,
            "video_id": None,
            "status": "pending",
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "success": False,
            "error": None,
            "file_path": None,
            "reference_image": None,
        }
        
        try:
            # 查找参考图片
            reference_image_path = self.get_reference_image_path(char_name)
            if reference_image_path:
                result["reference_image"] = reference_image_path
                print(f"找到参考图片: {reference_image_path}")
            else:
                print(f"警告: 未找到参考图片 {char_name}.png，将不使用参考图片")
            
            start_time = time.time()
            
            # 调用策略生成视频
            generation_result = self.strategy.generate_video(
                prompt=processed_prompt,
                reference_image_path=reference_image_path
            )
            
            if generation_result.get("error"):
                result["error"] = generation_result["error"]
                result["status"] = "failed"
                result["end_time"] = time.time()
                result["duration"] = result["end_time"] - result["start_time"]
                return result
            
            video_id = generation_result.get("video_id")
            if not video_id:
                result["error"] = "未返回视频ID"
                result["status"] = "failed"
                result["end_time"] = time.time()
                result["duration"] = result["end_time"] - result["start_time"]
                return result
            
            result["video_id"] = video_id
            print(f"视频任务创建成功，ID: {video_id}")
            
            # 轮询生成状态
            while True:
                poll_result = self.strategy.poll_status(video_id)
                status = poll_result.get("status")
                
                if status == "completed":
                    # 下载视频
                    video_url = poll_result.get("video_url")
                    if not video_url:
                        result["error"] = "未返回视频URL"
                        result["status"] = "download_failed"
                        break
                    
                    file_path = os.path.join(self.output_dir, f"{char_name}.mp4")
                    
                    if self.strategy.download_video(video_url, file_path):
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        result["end_time"] = end_time
                        result["duration"] = duration
                        result["status"] = "completed"
                        result["success"] = True
                        result["file_path"] = file_path
                        
                        print(f"视频生成完成: {char_name}, 耗时: {duration:.2f}秒")
                        break
                    else:
                        result["error"] = "下载视频失败"
                        result["status"] = "download_failed"
                        result["end_time"] = time.time()
                        result["duration"] = result["end_time"] - result["start_time"]
                        break
                        
                elif status == "failed":
                    result["error"] = poll_result.get("error", "视频生成失败")
                    result["status"] = "failed"
                    result["end_time"] = time.time()
                    result["duration"] = result["end_time"] - result["start_time"]
                    print(f"视频生成失败: {char_name}, 错误: {result['error']}")
                    break
                else:
                    # 处理中，继续轮询
                    print(f"视频生成中... 状态: {status}")
                    time.sleep(1)
            
        except Exception as e:
            result["error"] = f"生成视频失败: {str(e)}"
            result["status"] = "failed"
            result["end_time"] = time.time()
            if result["start_time"]:
                result["duration"] = result["end_time"] - result["start_time"]
            print(f"生成视频失败: {char_name}, 错误: {e}")
        
        return result
    
    def run_batch_test(self):
        """运行批量测试"""
        model_type = "隐藏角色名" if self.hide_name else "保留角色名"
        print("=" * 60)
        print(f"{self.model_name} {model_type} 生成测试")
        print("=" * 60)
        
        # 读取测试数据
        prompts = self.read_prompts()
        if not prompts:
            print("没有找到有效的测试数据")
            return
        
        self.total_tests = len(prompts)
        print(f"共找到 {self.total_tests} 个测试样本")
        
        # 开始批量测试
        start_time = time.time()
        
        for i, prompt_data in enumerate(prompts, 1):
            print(f"\n进度: {i}/{self.total_tests}")
            result = self.generate_single_video(prompt_data)
            self.results.append(result)
            
            if result["success"]:
                self.successful_tests += 1
            else:
                self.failed_tests += 1
            
            # 添加延迟避免API限制
            if i < self.total_tests:
                print("等待5秒后继续下一个测试...")
                time.sleep(5)
        
        total_time = time.time() - start_time
        print(f"\n批量测试完成，总耗时: {total_time:.2f}秒")
        
        # 生成统计报告
        self.generate_report()
    
    def generate_report(self):
        """生成统计报告"""
        print("\n" + "=" * 60)
        print("测试统计报告")
        print("=" * 60)
        
        # 基本统计
        success_rate = (
            (self.successful_tests / self.total_tests) * 100
            if self.total_tests > 0
            else 0
        )
        failure_rate = (
            (self.failed_tests / self.total_tests) * 100
            if self.total_tests > 0
            else 0
        )
        
        print(f"总测试数: {self.total_tests}")
        print(f"成功数: {self.successful_tests}")
        print(f"失败数: {self.failed_tests}")
        print(f"成功率: {success_rate:.2f}%")
        print(f"失败率: {failure_rate:.2f}%")
        
        # 耗时统计（仅统计成功的）
        successful_results = [
            r for r in self.results 
            if r["success"] and r["duration"] is not None
        ]
        if successful_results:
            durations = [r["duration"] for r in successful_results]
            avg_duration = sum(durations) / len(durations)
            print(f"\n平均耗时（成功）: {avg_duration:.2f}秒")
        else:
            print(f"\n平均耗时（成功）: N/A（无成功案例）")
        
        # 失败原因统计
        failed_results = [r for r in self.results if not r["success"]]
        if failed_results:
            print(f"\n失败原因统计:")
            error_counts = {}
            for result in failed_results:
                error = result.get("error") or "未知错误"
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"  {error}: {count}次")
        else:
            print(f"\n失败原因统计: 无失败案例")
        
        # 保存报告到文件
        self.save_report()
    
    def save_report(self):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            self.output_dir, 
            f"report_{timestamp}.txt"
        )
        
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                model_type = "隐藏角色名" if self.hide_name else "保留角色名"
                f.write("=" * 80 + "\n")
                f.write(f"{self.model_name} {model_type} 测试报告\n")
                f.write("=" * 80 + "\n")
                f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 基本统计
                success_rate = (
                    (self.successful_tests / self.total_tests) * 100
                    if self.total_tests > 0
                    else 0
                )
                failure_rate = (
                    (self.failed_tests / self.total_tests) * 100
                    if self.total_tests > 0
                    else 0
                )
                
                f.write("基本统计:\n")
                f.write("-" * 40 + "\n")
                f.write(f"总测试数: {self.total_tests}\n")
                f.write(f"成功数: {self.successful_tests}\n")
                f.write(f"失败数: {self.failed_tests}\n")
                f.write(f"成功率: {success_rate:.2f}%\n")
                f.write(f"失败率: {failure_rate:.2f}%\n\n")
                
                # 耗时统计
                successful_results = [
                    r for r in self.results 
                    if r["success"] and r["duration"] is not None
                ]
                if successful_results:
                    durations = [r["duration"] for r in successful_results]
                    avg_duration = sum(durations) / len(durations)
                    f.write("耗时统计:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"平均耗时（成功）: {avg_duration:.2f}秒\n\n")
                else:
                    f.write("耗时统计:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"平均耗时（成功）: N/A（无成功案例）\n\n")
                
                # 失败原因统计
                failed_results = [r for r in self.results if not r["success"]]
                if failed_results:
                    f.write("失败原因统计:\n")
                    f.write("-" * 40 + "\n")
                    error_counts = {}
                    for result in failed_results:
                        error = result.get("error") or "未知错误"
                        error_counts[error] = error_counts.get(error, 0) + 1
                    
                    for error, count in error_counts.items():
                        f.write(f"{error}: {count}次\n")
                    f.write("\n")
                else:
                    f.write("失败原因统计:\n")
                    f.write("-" * 40 + "\n")
                    f.write("无失败案例\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("报告结束\n")
                f.write("=" * 80 + "\n")
            
            print(f"\n报告已保存到: {report_file}")
        except Exception as e:
            print(f"保存报告失败: {e}")

