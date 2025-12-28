# 键盘监听器问题排查指南 (Ubuntu 22.04)

## 问题描述
在数据采集时，键盘按钮（右箭头键、左箭头键、ESC键）没有反应，无法控制采集流程。

## 键盘快捷键说明
- **右箭头键 (→)**: 提前退出当前 episode，继续下一个
- **左箭头键 (←)**: 提前退出并重新录制当前 episode
- **ESC键**: 停止整个数据采集过程

## 可能原因分析

### 1. 权限问题（最常见）
在 Ubuntu 22.04 上，`pynput` 需要访问 `/dev/input/event*` 设备来监听键盘事件。默认情况下，普通用户可能没有权限访问这些设备。

**症状**:
- 程序运行正常，但按键无反应
- 没有任何错误信息
- 日志中可能显示 "pynput is available" 但监听器不工作

**解决方案**:

#### 方案 A: 将用户添加到 input 组（推荐）
```bash
# 将当前用户添加到 input 组
sudo usermod -a -G input $USER

# 重新登录或运行以下命令使组权限生效
newgrp input

# 验证是否已加入组
groups
```

#### 方案 B: 使用 udev 规则（永久解决方案）
```bash
# 创建 udev 规则文件
sudo nano /etc/udev/rules.d/99-input-permissions.rules
```

添加以下内容：
```
KERNEL=="event*", MODE="0664", GROUP="input"
```

然后重新加载规则：
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**注意**: 如果键盘是 USB 设备，可能需要重新插拔 USB 设备或重启系统。

#### 方案 C: 临时解决方案（每次需要）
```bash
# 临时给所有输入设备添加读写权限
sudo chmod 666 /dev/input/event*
```

### 2. DISPLAY 环境变量未设置
`pynput` 在 Linux 上需要图形界面环境。

**症状**:
- 日志显示 "No DISPLAY set. Skipping pynput import."
- 或者 "Headless environment detected"

**解决方案**:
```bash
# 检查 DISPLAY 是否设置
echo $DISPLAY

# 如果为空，设置 DISPLAY
export DISPLAY=:0

# 或者如果使用 X11 forwarding (SSH)
export DISPLAY=localhost:10.0
```

**注意**: 如果通过 SSH 连接，需要启用 X11 forwarding:
```bash
ssh -X username@hostname
# 或
ssh -Y username@hostname
```

### 3. pynput 未正确安装
**症状**:
- 导入错误
- "Error trying to import pynput"

**解决方案**:
```bash
# 安装 pynput
pip install pynput

# 或者如果使用 conda
conda install -c conda-forge pynput
```

### 4. 终端窗口没有焦点
键盘事件只能被有焦点的窗口捕获。

**解决方案**:
- 确保运行程序的终端窗口是活动窗口（点击终端窗口）
- 不要在后台运行，确保终端在前台
- 如果使用 SSH，确保 X11 forwarding 正常工作

### 5. 无独立显卡相关问题
虽然没有独立显卡通常不会直接影响键盘监听，但可能影响：
- Rerun 可视化界面（如果使用 `--display_data=true`）
- 图形界面相关的依赖

**解决方案**:
- 如果只是键盘问题，显卡不是主要原因
- 如果 Rerun 界面无法显示，可以设置 `--display_data=false` 来禁用可视化

## 诊断步骤

### 步骤 1: 运行诊断脚本
```bash
cd /home/jikangyi/lerobot
python diagnose_keyboard.py
```

这个脚本会检查：
- DISPLAY 环境变量
- pynput 是否可以导入
- X11 服务器是否可用
- 输入设备权限
- 键盘监听器是否工作

### 步骤 2: 手动检查
```bash
# 1. 检查 DISPLAY
echo $DISPLAY

# 2. 检查 pynput
python -c "import pynput; print('pynput OK')"

# 3. 检查输入设备权限
ls -l /dev/input/event*

# 4. 检查用户组
groups | grep input

# 5. 测试 X11
xset q
```

### 步骤 3: 检查程序日志
运行数据采集程序时，查看是否有以下日志：
- "pynput is available - enabling local keyboard listener."
- "Headless environment detected..."
- "No DISPLAY set. Skipping pynput import."
- "Error trying to import pynput..."

## 快速修复命令（按顺序尝试）

```bash
# 1. 设置 DISPLAY（如果未设置）
export DISPLAY=:0

# 2. 添加用户到 input 组
sudo usermod -a -G input $USER
newgrp input

# 3. 验证权限
groups | grep input

# 4. 如果还是不行，临时给权限
sudo chmod 666 /dev/input/event*

# 5. 重新运行程序
```

## 验证修复

修复后，运行数据采集程序，尝试按：
- **右箭头键**: 应该看到 "Right arrow key pressed. Exiting loop..."
- **左箭头键**: 应该看到 "Left arrow key pressed. Exiting loop and rerecord..."
- **ESC键**: 应该看到 "Escape key pressed. Stopping data recording..."

如果看到这些消息，说明键盘监听器工作正常。

## 常见错误信息

### "Permission denied" 或 "Operation not permitted"
→ 权限问题，使用方案 A 或 B

### "No module named 'pynput'"
→ 安装 pynput: `pip install pynput`

### "No DISPLAY set"
→ 设置 DISPLAY: `export DISPLAY=:0`

### "Headless environment detected"
→ 检查 DISPLAY 和 pynput 安装

## 如果所有方法都失败

如果以上方法都不行，可以考虑：
1. 使用 SSH 的 X11 forwarding（如果远程连接）
2. 使用 VNC 或远程桌面
3. 检查是否有其他程序占用了键盘输入
4. 尝试在不同的终端（gnome-terminal, xterm 等）中运行

## 联系支持

如果问题仍然存在，请提供：
1. `diagnose_keyboard.py` 的输出
2. 程序运行的完整日志
3. `groups` 命令的输出
4. `ls -l /dev/input/event*` 的输出
5. `echo $DISPLAY` 的输出

