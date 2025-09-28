import keyboard
from pynput import mouse
from datetime import datetime
import sys
import time

class ClickListenerApp:
    def __init__(self):
        self.is_listening = False
        self.running = True
        
        # 绑定键盘事件
        keyboard.add_hotkey('f1', self.start_listening)
        keyboard.add_hotkey('f2', self.stop_listening)
        keyboard.add_hotkey('esc', self.exit_program)
        
        # 绑定鼠标点击事件
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()
        
        print('程序已启动，按F1开始监听点击位置，按F2停止监听，按ESC退出程序')
        self.show_status()

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.show_status()

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.show_status()

    def show_status(self):
        status = "正在监听点击位置" if self.is_listening else "未监听"
        print(f"当前状态: {status}")

    def on_click(self, x, y, button, pressed):
        if self.is_listening and pressed:  # 只在按下时触发
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # 控制台输出点击位置
            print(f"[{timestamp}] 点击位置: X={x}, Y={y}")

    def exit_program(self):
        print("程序退出")
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        sys.exit(0)

if __name__ == "__main__":
    app = ClickListenerApp()
    try:
        # 保持程序运行
        while app.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序被中断")