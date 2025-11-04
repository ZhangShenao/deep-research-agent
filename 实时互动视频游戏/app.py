# -*- coding: utf-8 -*-
"""
Streamlit前端应用
"""
import streamlit as st
import time
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from worldview import get_default_worldview  # , generate_cover_image
from state import GameState
from agent import run_agent_step
from utils import ensure_data_dir, concatenate_videos
from nodes import story_continuation_node_stream, storyboard_node_stream
from nodes.extract_frame_node import extract_frame_node
from nodes.video_node import video_generation_node


# 页面配置
st.set_page_config(
    page_title="实时互动视频游戏",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化会话状态
if "game_state" not in st.session_state:
    worldview = get_default_worldview()
    st.session_state.game_state = {
        "messages": [],
        "story_context": worldview,
        "latest_story": None,
        "storyboard": None,
        "storyboard_shots": None,
        "reference_image_path": None,
        "video_path": None,
        "current_step": "idle",
        "error": None,
    }
    st.session_state.show_worldview = True
    st.session_state.video_index = 0
    st.session_state.video_list = []  # 保存所有生成的视频路径
    # st.session_state.cover_image_path = None  # 封面图路径（已注释）

if "show_worldview" not in st.session_state:
    st.session_state.show_worldview = True

if "video_list" not in st.session_state:
    st.session_state.video_list = []

# if "cover_image_path" not in st.session_state:
#     st.session_state.cover_image_path = None

if "full_video_path" not in st.session_state:
    st.session_state.full_video_path = None  # 完整拼接视频路径


def display_worldview():
    """显示世界观"""
    if st.session_state.show_worldview:
        # # 如果还没有生成封面图，生成一个（已注释）
        # if st.session_state.cover_image_path is None:
        #     with st.spinner("🎨 正在生成游戏封面图..."):
        #         # 使用世界观文本生成匹配的封面图
        #         worldview_text = st.session_state.game_state.get("story_context", "")
        #         cover_path = generate_cover_image(worldview_text=worldview_text)
        #         if cover_path:
        #             st.session_state.cover_image_path = cover_path

        # # 显示封面图（已注释）
        # if (
        #     st.session_state.cover_image_path
        #     and Path(st.session_state.cover_image_path).exists()
        # ):
        #     st.image(st.session_state.cover_image_path, caption="游戏封面")
        #     st.markdown("---")

        with st.expander("📖 游戏世界观和故事背景", expanded=True):
            st.markdown(st.session_state.game_state["story_context"])

        # 按钮布局
        # col1, col2 = st.columns(2)
        # with col1:
        #     if st.button("🔄 重新生成封面图", use_container_width=True):
        #         with st.spinner("🎨 正在重新生成游戏封面图..."):
        #             # 删除旧封面图
        #             old_cover = st.session_state.cover_image_path
        #             if old_cover and Path(old_cover).exists():
        #                 try:
        #                     Path(old_cover).unlink()
        #                 except:
        #                     pass

        #             # 清空封面图路径，强制重新生成
        #             st.session_state.cover_image_path = None

        #             # 生成新封面图
        #             worldview_text = st.session_state.game_state.get(
        #                 "story_context", ""
        #             )
        #             cover_path = generate_cover_image(worldview_text=worldview_text)
        #             if cover_path:
        #                 st.session_state.cover_image_path = cover_path
        #                 st.success("✅ 封面图已重新生成！")
        #                 st.rerun()
        #             else:
        #                 st.error("❌ 封面图生成失败")

        # with col2:
        if st.button("开始游戏", type="primary", use_container_width=True):
            st.session_state.show_worldview = False
            st.rerun()


def display_chat():
    """显示聊天界面"""
    st.title("🎮 实时互动视频游戏")

    # 在游戏界面中显示世界观（可折叠）
    with st.expander("📖 游戏世界观和故事背景", expanded=False):
        st.markdown(st.session_state.game_state["story_context"])

    st.markdown("---")

    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.game_state["messages"]:
            if isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.write(msg.content)
            elif isinstance(msg, AIMessage):
                with st.chat_message("assistant"):
                    st.write(msg.content)

    # 显示当前状态
    if st.session_state.game_state.get("current_step") != "idle":
        current_step = st.session_state.game_state["current_step"]
        step_names = {
            "story_continuation": "📝 正在续写剧情...",
            "storyboard": "🎬 正在生成分镜脚本...",
            "extract_frame": "🖼️ 正在抽取参考图片...",
            "video_generation": "🎥 正在生成视频...",
            "completed": "✅ 完成",
            "error": "❌ 错误",
        }
        st.info(step_names.get(current_step, "处理中..."))

    # 显示错误
    if st.session_state.game_state.get("error"):
        st.error(f"错误: {st.session_state.game_state['error']}")


def display_story():
    """显示最新剧情"""
    if st.session_state.game_state.get("latest_story"):
        with st.expander("📖 最新剧情", expanded=True):
            st.markdown(st.session_state.game_state["latest_story"])


def display_storyboard():
    """显示分镜脚本"""
    if st.session_state.game_state.get("storyboard_shots"):
        with st.expander("🎬 分镜脚本", expanded=False):
            shots = st.session_state.game_state["storyboard_shots"]
            for i, shot in enumerate(shots, 1):
                st.markdown(f"**分镜 {i}** (时长: {shot.get('duration', 0)}秒)")
                st.write(f"描述: {shot.get('description', '')}")
                st.write(f"镜头运动: {shot.get('camera_movement', '')}")
                st.write(f"风格: {shot.get('style', '')}")
                st.markdown("---")


def display_video():
    """显示所有生成的视频（持续保留在侧边栏）"""
    if st.session_state.video_list:
        st.markdown("### 🎥 生成的视频")

        # 生成完整视频按钮
        if len(st.session_state.video_list) > 1:
            if st.button("🎬 生成完整视频", type="primary", use_container_width=True):
                with st.spinner("正在拼接所有视频..."):
                    # 按顺序拼接视频（video_list已经按顺序保存）
                    output_path = str(
                        Path(__file__).parent / "data" / "videos" / "full_video.mp4"
                    )
                    success = concatenate_videos(
                        st.session_state.video_list, output_path
                    )
                    if success:
                        # 确保路径是绝对路径
                        full_path = Path(output_path).resolve()
                        st.session_state.full_video_path = str(full_path)
                        st.success("✅ 完整视频生成成功！")
                        st.rerun()
                    else:
                        st.error("❌ 视频拼接失败")

        # 显示完整视频
        full_video_path = st.session_state.get("full_video_path")
        if full_video_path and Path(full_video_path).exists():
            st.markdown("#### 🎞️ 完整视频")
            try:
                st.video(full_video_path)
            except Exception as e:
                st.error(f"无法播放视频: {e}")
                st.write(f"视频路径: {full_video_path}")
            st.markdown("---")
        else:
            # 检查是否有完整视频文件但未加载到状态中
            default_full_video = (
                Path(__file__).parent / "data" / "videos" / "full_video.mp4"
            )
            if default_full_video.exists():
                st.session_state.full_video_path = str(default_full_video)
                st.markdown("#### 🎞️ 完整视频")
                st.video(str(default_full_video))
                st.markdown("---")

        # 显示所有历史视频，最新的在最上面
        st.markdown("#### 📹 分段视频")
        for idx, video_path in enumerate(reversed(st.session_state.video_list), 1):
            if video_path and Path(video_path).exists():
                st.markdown(f"**视频 {len(st.session_state.video_list) - idx + 1}**")
                st.video(video_path)
                if idx < len(st.session_state.video_list):
                    st.markdown("---")


def process_user_input(user_input: str):
    """处理用户输入并执行工作流（支持流式输出）"""
    # 添加用户消息
    st.session_state.game_state["messages"].append(HumanMessage(content=user_input))

    # 步骤1: 续写剧情（流式输出）
    st.session_state.game_state["current_step"] = "story_continuation"
    with st.chat_message("assistant"):
        story_placeholder = st.empty()
        story_placeholder.markdown("📝 正在续写剧情...")

        st.session_state.game_state = story_continuation_node_stream(
            st.session_state.game_state, stream_placeholder=story_placeholder
        )

        if st.session_state.game_state.get("error"):
            st.error(f"错误: {st.session_state.game_state['error']}")
            return

    # 步骤2: 生成分镜脚本（流式输出）
    st.session_state.game_state["current_step"] = "storyboard"
    with st.chat_message("assistant"):
        storyboard_placeholder = st.empty()
        storyboard_placeholder.markdown("🎬 正在生成分镜脚本...")

        st.session_state.game_state = storyboard_node_stream(
            st.session_state.game_state, stream_placeholder=storyboard_placeholder
        )

        if st.session_state.game_state.get("error"):
            st.error(f"错误: {st.session_state.game_state['error']}")
            return

        # 显示最终的分镜脚本摘要
        shots_count = len(st.session_state.game_state.get("storyboard_shots", []))
        storyboard_placeholder.markdown(f"✅ 分镜脚本已生成，共{shots_count}个分镜")

    # 步骤3: 抽取参考图片
    st.session_state.game_state["current_step"] = "extract_frame"
    st.info("🖼️ 正在抽取参考图片...")
    st.session_state.game_state = extract_frame_node(st.session_state.game_state)

    if st.session_state.game_state.get("error"):
        st.error(f"错误: {st.session_state.game_state['error']}")
        return

    # 步骤4: 生成视频
    st.session_state.game_state["current_step"] = "video_generation"
    with st.spinner("🎥 正在生成视频，这可能需要几分钟..."):
        st.session_state.game_state = video_generation_node(st.session_state.game_state)

    if st.session_state.game_state.get("error"):
        st.error(f"错误: {st.session_state.game_state['error']}")
        return

    # 重置步骤状态
    if st.session_state.game_state.get("current_step") == "completed":
        st.session_state.game_state["current_step"] = "idle"
        # 将新生成的视频添加到视频列表
        video_path = st.session_state.game_state.get("video_path")
        if video_path and Path(video_path).exists():
            # 避免重复添加
            if video_path not in st.session_state.video_list:
                st.session_state.video_list.append(video_path)
        st.success("✅ 视频生成完成！")


def main():
    """主函数"""
    # 确保数据目录存在
    ensure_data_dir()

    # 显示世界观（首次）
    display_worldview()

    if not st.session_state.show_worldview:
        # 显示聊天界面
        display_chat()

        # 侧边栏
        with st.sidebar:
            st.header("📊 游戏状态")

            # 显示世界观（侧边栏版本，方便查看）
            with st.expander("📖 世界观", expanded=False):
                st.markdown(st.session_state.game_state["story_context"])

            st.markdown("---")

            # 显示最新剧情
            display_story()

            # 显示分镜脚本
            display_storyboard()

            # 显示参考图片
            ref_image = st.session_state.game_state.get("reference_image_path")
            if ref_image and Path(ref_image).exists():
                st.image(ref_image, caption="参考图片（上一段视频的最后一帧）")

            # 显示视频
            display_video()

        # 用户输入
        user_input = st.chat_input("输入你的行动或对话...")
        if user_input:
            # 处理用户输入（流式输出）
            process_user_input(user_input)
            st.rerun()


if __name__ == "__main__":
    main()
