import keyboard
import time

def on_key_event(event):
    """键盘事件回调函数"""
    # 获取组合键信息（如果有修饰键如Ctrl、Alt等）
    modifiers = []
    if event.modifiers:
        modifiers = list(event.modifiers)
    
    # 构建键名显示（修饰键+主键）
    keys_pressed = modifiers + [event.name]
    key_display = '+'.join(keys_pressed)
    
    print(f"你按下了: {key_display}")

def start_hotkey_listener():
    """开始监听键盘快捷键"""
    print("快捷键监听已启动，按下任意组合键查看结果...")
    print("按下ESC键退出程序")
    
    # 监听所有按键事件
    keyboard.hook(on_key_event)
    
    try:
        # 保持程序运行，直到按下ESC
        keyboard.wait('esc')
    finally:
        # 清理键盘监听
        keyboard.unhook_all()
        print("\n快捷键监听已关闭")

if __name__ == "__main__":
    start_hotkey_listener()