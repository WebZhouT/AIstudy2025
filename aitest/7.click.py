import json
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import threading
import time
import random

class MouseRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.actions = []
        self.repeat_count = 999  # 默认重复次数
        self.current_repeat = 0
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        self.mouse_listener.start()

    def on_move(self, x, y):
        if self.recording:
            self.actions.append(('move', (x, y), time.time()))

    def on_click(self, x, y, button, pressed):
        if self.recording:
            action = 'press' if pressed else 'release'
            # 修改：保存按钮名称而非字符串表示
            self.actions.append((action, (x, y, button.name), time.time()))

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            self.actions.append(('scroll', (x, y, dx, dy), time.time()))

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.f1:
                if not self.recording and not self.playing:
                    print("开始录制...")
                    self.actions = []
                    self.recording = True
                    
            elif key == keyboard.Key.f2:
                if self.recording:
                    print("结束录制")
                    self.recording = False
                    self.save_script()
                    
            elif key == keyboard.Key.f10:
                if not self.recording and not self.playing:
                    self.repeat_count = 99999999  # 直接设置为默认1次
                    print("开始播放")
                    self.play_actions()
                    
            elif key == keyboard.Key.f12:  # 添加F12作为停止快捷键
                if self.playing:
                    print("停止播放")
                    self.playing = False
                    self.current_repeat = self.repeat_count  # 设置为最大值以结束循环
                    
        except AttributeError:
            pass

    def save_script(self):
        with open('mouse_script.json', 'w') as f:
            # 保存时减去第一个动作的时间，使时间变为相对值
            if self.actions:
                first_time = self.actions[0][2]
                adjusted_actions = [(action, pos, t - first_time) 
                                  for action, pos, t in self.actions]
                json.dump(adjusted_actions, f)
        print(f"已保存 {len(self.actions)} 个动作到 mouse_script.json")

    def load_script(self):
        try:
            with open('mouse_script.json', 'r') as f:
                self.actions = json.load(f)   
            print(f"已加载 {len(self.actions)} 个动作")
            return True
        except:
            print("无法加载脚本文件")
            return False

    def play_actions(self):
        # 确保总是重新加载脚本
        if not self.load_script():
            print("无法加载脚本，无法播放")
            return
            
        self.playing = True
        self.current_repeat = 0
        
        def play_thread():
            while self.current_repeat < self.repeat_count and self.playing:
                self.current_repeat += 1
                print(f"第 {self.current_repeat} 次播放...")
                
                # 执行每个动作
                start_time = time.time()
                for action, pos, delay in self.actions:
                    if not self.playing:
                        break
                    while time.time() - start_time < delay and self.playing:
                        # 随机间隔1-3秒
                        # time.sleep(1 + (2 - 1) * random.random())
                        time.sleep(0.001)
                    
                    if not self.playing:
                        break
                        
                    if action == 'move':
                        self.mouse.position = pos
                    elif action == 'press':
                        x, y, button_name = pos
                        self.mouse.position = (x, y)
                        # 修改：兼容新旧格式按钮名称
                        button = Button[button_name.split('.')[-1]]
                        self.mouse.press(button)
                    elif action == 'release':
                        x, y, button_name = pos
                        self.mouse.position = (x, y)
                        # 修改：兼容新旧格式按钮名称
                        button = Button[button_name.split('.')[-1]]
                        self.mouse.release(button)
                    elif action == 'scroll':
                        x, y, dx, dy = pos
                        self.mouse.position = (x, y)
                        self.mouse.scroll(dx, dy)
                
            self.playing = False
            print("播放完成" if self.current_repeat >= self.repeat_count else "播放已停止")
        
        threading.Thread(target=play_thread).start()

if __name__ == "__main__":
    recorder = MouseRecorder()
    print("快捷键说明:")
    print("F1 - 开始录制")
    print("F2 - 结束录制并保存")
    print("F10 - 播放录制的动作")
    print("F12 - 停止播放")  # 添加停止快捷键说明
    print("程序运行中...")
    while True:
        time.sleep(1)