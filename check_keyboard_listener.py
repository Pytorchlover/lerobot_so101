#!/usr/bin/env python3
"""
快速检查键盘监听器是否工作的脚本
"""

import os
import sys

print("=" * 60)
print("检查键盘监听器状态")
print("=" * 60)
print()

# 1. 检查 DISPLAY
display = os.environ.get("DISPLAY")
if display:
    print(f"✓ DISPLAY: {display}")
else:
    print("✗ DISPLAY 未设置")
    print("  运行: export DISPLAY=:0")
    sys.exit(1)

# 2. 检查 pynput
try:
    from pynput import keyboard
    print("✓ pynput 可以导入")
except Exception as e:
    print(f"✗ pynput 导入失败: {e}")
    sys.exit(1)

# 3. 检查 is_headless
try:
    sys.path.insert(0, 'src')
    from lerobot.utils.control_utils import is_headless
    
    if is_headless():
        print("✗ 检测到 headless 模式")
        print("  键盘监听器将不会工作")
        sys.exit(1)
    else:
        print("✓ 非 headless 模式")
except Exception as e:
    print(f"⚠ 无法检查 headless 状态: {e}")

# 4. 测试键盘监听器
print("\n测试键盘监听器...")
print("请按右箭头键 (→) 测试...")
print("如果看到 'Right arrow key pressed' 说明工作正常")
print("如果看到转义序列 (^[[C) 说明监听器未工作")
print()

events = {"exit_early": False}

def on_press(key):
    try:
        if key == keyboard.Key.right:
            print("\n✓ Right arrow key pressed. Exiting loop...")
            events["exit_early"] = True
            return False  # 停止监听器
        elif key == keyboard.Key.left:
            print("\n✓ Left arrow key pressed. Exiting loop and rerecord...")
            events["exit_early"] = True
            return False
        elif key == keyboard.Key.esc:
            print("\n✓ Escape key pressed. Stopping...")
            events["exit_early"] = True
            return False
    except Exception as e:
        print(f"\n✗ 处理按键时出错: {e}")

try:
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("键盘监听器已启动，等待按键...")
    
    import time
    for i in range(10):
        time.sleep(1)
        if events["exit_early"]:
            listener.stop()
            print("\n✓ 键盘监听器工作正常！")
            sys.exit(0)
        print(f"  等待中... ({10-i}秒)")
    
    listener.stop()
    print("\n✗ 10秒内未检测到按键")
    print("可能的原因:")
    print("1. 权限不足 - 运行: sudo usermod -a -G input $USER && newgrp input")
    print("2. 终端窗口没有焦点 - 点击终端窗口")
    print("3. 键盘监听器没有正确启动")
    
except PermissionError as e:
    print(f"\n✗ 权限错误: {e}")
    print("\n解决方案:")
    print("1. 将用户添加到 input 组:")
    print("   sudo usermod -a -G input $USER")
    print("   newgrp input")
    print("\n2. 或临时给权限:")
    print("   sudo chmod 666 /dev/input/event*")
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()

