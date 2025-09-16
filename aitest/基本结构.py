# 图像识别
from rapidocr_onnxruntime import RapidOCR
import ctypes  # 用于系统弹窗
from win10toast import ToastNotifier
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
import keyboard
import threading
import pyautogui
import time
import win32gui
# 全部操作完毕后出现提示信息
def show_alert(message, use_toast=True):
    """显示提醒（可选择Toast或传统弹窗）"""
    if use_toast:
        toaster.show_toast(
            "提醒",
            message,
            duration=5,
            threaded=True
        )
    else:
        ctypes.windll.user32.MessageBoxW(0, message, "提醒", 1)

def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height
# 全局变量控制运行状态
running = False
stop_event = threading.Event()


def main_loop():
    """主循环函数"""
    while not stop_event.is_set():
        if running:
            # 在这里添加你的主要逻辑
            pass
        time.sleep(0.1)  # 短暂休眠避免CPU占用过高


def start_script():
    """启动脚本"""
    global running
    running = True
    print("\n===== 脚本已启动 =====")

def stop_script():
    """停止脚本"""
    global running
    running = False
    print("\n===== 脚本已停止 =====")
def main():
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("提示: 按 F1 启动脚本，按 F2 停止脚本")
    
    try:
        # 启动主循环
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:  # 添加: 捕获主循环外的异常
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()