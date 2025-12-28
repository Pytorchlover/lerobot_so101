#!/usr/bin/env python3
"""
诊断键盘监听器问题的脚本
用于检查 pynput 在 Ubuntu 22.04 上的权限和配置问题
"""

import os
import sys
import subprocess
from pathlib import Path

def check_display():
    """检查 DISPLAY 环境变量"""
    display = os.environ.get("DISPLAY")
    if display:
        print(f"✓ DISPLAY 环境变量已设置: {display}")
        return True
    else:
        print("✗ DISPLAY 环境变量未设置")
        print("  解决方案: export DISPLAY=:0")
        return False

def check_pynput_import():
    """检查 pynput 是否可以导入"""
    try:
        import pynput
        print("✓ pynput 可以成功导入")
        return True
    except ImportError as e:
        print(f"✗ pynput 导入失败: {e}")
        print("  解决方案: pip install pynput")
        return False
    except Exception as e:
        print(f"✗ pynput 导入时出错: {e}")
        return False

def check_input_permissions():
    """检查输入设备权限"""
    input_devices = Path("/dev/input").glob("event*")
    devices = list(input_devices)
    
    if not devices:
        print("✗ 未找到输入设备 (/dev/input/event*)")
        return False
    
    print(f"✓ 找到 {len(devices)} 个输入设备")
    
    # 检查当前用户是否有权限
    user = os.environ.get("USER", "unknown")
    has_permission = False
    
    for device in devices[:3]:  # 只检查前3个
        try:
            # 尝试读取设备
            with open(device, 'rb'):
                has_permission = True
                print(f"✓ 可以访问 {device.name}")
        except PermissionError:
            print(f"✗ 无权限访问 {device.name}")
            print(f"  当前用户: {user}")
            stat = device.stat()
            print(f"  设备权限: {oct(stat.st_mode)[-3:]}")
    
    if not has_permission:
        print("\n权限问题解决方案:")
        print("1. 将用户添加到 input 组:")
        print(f"   sudo usermod -a -G input {user}")
        print("   然后重新登录或运行: newgrp input")
        print("\n2. 或者使用 udev 规则（推荐）:")
        print("   创建文件 /etc/udev/rules.d/99-input-permissions.rules:")
        print('   KERNEL=="event*", MODE="0664", GROUP="input"')
        print("   然后运行: sudo udevadm control --reload-rules")
        print("   并重新插拔键盘或重启")
        print("\n3. 临时解决方案（不推荐，每次需要）:")
        print("   sudo chmod 666 /dev/input/event*")
    
    return has_permission

def test_keyboard_listener():
    """测试键盘监听器是否工作"""
    try:
        from pynput import keyboard
        
        print("\n测试键盘监听器...")
        print("请按右箭头键 (->) 来测试...")
        print("如果5秒内没有反应，说明监听器不工作")
        
        key_pressed = False
        
        def on_press(key):
            nonlocal key_pressed
            if key == keyboard.Key.right:
                print("✓ 成功检测到右箭头键!")
                key_pressed = True
                return False  # 停止监听器
        
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        import time
        for i in range(5):
            time.sleep(1)
            if key_pressed:
                listener.stop()
                return True
            print(f"  等待中... ({5-i}秒)")
        
        listener.stop()
        print("✗ 5秒内未检测到按键")
        return False
        
    except Exception as e:
        print(f"✗ 测试键盘监听器时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_x11():
    """检查 X11 是否可用"""
    try:
        result = subprocess.run(
            ["xset", "q"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print("✓ X11 服务器可用")
            return True
        else:
            print("✗ X11 服务器不可用")
            return False
    except FileNotFoundError:
        print("✗ xset 命令未找到 (可能未安装 X11)")
        return False
    except Exception as e:
        print(f"✗ 检查 X11 时出错: {e}")
        return False

def main():
    print("=" * 60)
    print("键盘监听器诊断工具")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. 检查 DISPLAY 环境变量")
    results.append(("DISPLAY", check_display()))
    print()
    
    print("2. 检查 pynput 导入")
    results.append(("pynput", check_pynput_import()))
    print()
    
    print("3. 检查 X11 服务器")
    results.append(("X11", check_x11()))
    print()
    
    print("4. 检查输入设备权限")
    results.append(("权限", check_input_permissions()))
    print()
    
    # 只有在前面都通过的情况下才测试监听器
    if all(r[1] for r in results[:-1]):  # 排除权限检查
        print("5. 测试键盘监听器")
        results.append(("监听器", test_keyboard_listener()))
    else:
        print("5. 跳过监听器测试（前置条件未满足）")
        results.append(("监听器", False))
    
    print()
    print("=" * 60)
    print("诊断结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✓ 所有检查通过！键盘监听器应该可以正常工作。")
    else:
        print("\n✗ 发现问题，请根据上面的提示进行修复。")
        print("\n常见问题解决方案:")
        print("1. 如果 DISPLAY 未设置: export DISPLAY=:0")
        print("2. 如果权限不足: sudo usermod -a -G input $USER")
        print("3. 如果 pynput 未安装: pip install pynput")
        print("4. 确保在图形界面下运行，而不是 SSH 无显示连接")

if __name__ == "__main__":
    main()

