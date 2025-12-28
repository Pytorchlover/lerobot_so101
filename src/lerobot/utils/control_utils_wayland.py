"""
Wayland 兼容的键盘监听器实现
使用终端输入读取作为 pynput 的替代方案
"""

import logging
import os
import sys
import threading
import time
from queue import Queue

def init_keyboard_listener_terminal():
    """
    使用终端输入读取的键盘监听器（Wayland 兼容）
    
    用户需要在终端中输入：
    - 'n' + Enter: 下一个 episode (相当于右箭头键)
    - 'r' + Enter: 重新录制 (相当于左箭头键)  
    - 'q' + Enter: 退出 (相当于 ESC 键)
    """
    events = {}
    events["exit_early"] = False
    events["rerecord_episode"] = False
    events["stop_recording"] = False
    
    input_queue = Queue()
    running = threading.Event()
    running.set()
    
    def input_thread():
        """在后台线程中读取终端输入"""
        print("\n" + "="*60)
        print("键盘控制（Wayland 兼容模式）")
        print("="*60)
        print("在终端中输入以下命令：")
        print("  n + Enter: 下一个 episode（提前退出当前 episode）")
        print("  r + Enter: 重新录制当前 episode")
        print("  q + Enter: 退出数据采集")
        print("="*60 + "\n")
        
        while running.is_set():
            try:
                # 非阻塞读取（使用 select 或直接读取）
                if sys.stdin.isatty():
                    # 在交互式终端中
                    user_input = input().strip().lower()
                    input_queue.put(user_input)
                else:
                    # 非交互式，等待一下
                    time.sleep(0.1)
            except (EOFError, KeyboardInterrupt):
                running.clear()
                break
            except Exception as e:
                logging.error(f"读取输入时出错: {e}")
                time.sleep(0.1)
    
    def check_input():
        """检查输入队列并更新事件"""
        while not input_queue.empty():
            try:
                cmd = input_queue.get_nowait()
                if cmd == 'n':
                    print("\n✓ 下一个 episode (提前退出当前 episode)...")
                    events["exit_early"] = True
                elif cmd == 'r':
                    print("\n✓ 重新录制当前 episode...")
                    events["rerecord_episode"] = True
                    events["exit_early"] = True
                elif cmd == 'q':
                    print("\n✓ 退出数据采集...")
                    events["stop_recording"] = True
                    events["exit_early"] = True
                    running.clear()
            except Exception as e:
                logging.error(f"处理输入时出错: {e}")
    
    # 启动输入线程
    thread = threading.Thread(target=input_thread, daemon=True)
    thread.start()
    
    # 返回一个模拟的 listener 对象和事件字典
    class TerminalListener:
        def __init__(self):
            self._running = running
            self._check_input = check_input
        
        def is_alive(self):
            return self._running.is_set()
        
        def stop(self):
            self._running.clear()
        
        def check(self):
            """需要在主循环中定期调用此方法来检查输入"""
            check_input()
    
    listener = TerminalListener()
    
    return listener, events


def init_keyboard_listener_wayland_aware():
    """
    Wayland 感知的键盘监听器初始化
    如果检测到 Wayland，使用终端输入；否则使用 pynput
    """
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    
    if session_type == "wayland":
        logging.warning(
            "检测到 Wayland 显示服务器。pynput 在 Wayland 下无法工作。"
            "使用终端输入模式。"
            "在终端中输入: n (下一个), r (重新录制), q (退出)"
        )
        return init_keyboard_listener_terminal()
    
    # 非 Wayland，尝试使用 pynput
    try:
        from lerobot.utils.control_utils import init_keyboard_listener
        return init_keyboard_listener()
    except Exception as e:
        logging.warning(f"无法使用 pynput，回退到终端输入模式: {e}")
        return init_keyboard_listener_terminal()

