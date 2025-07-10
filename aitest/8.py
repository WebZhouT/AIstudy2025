import pyautogui
import time

def get_mouse_click_position():
    print("请在5秒内点击鼠标...")
    time.sleep(5)  # 给用户5秒时间准备点击
    x, y = pyautogui.position()  # 获取鼠标当前位置
    print(f"鼠标点击位置: X={x}, Y={y}")
    return (x, y)

if __name__ == "__main__":
    get_mouse_click_position()