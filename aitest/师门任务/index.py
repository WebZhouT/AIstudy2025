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
import win32con
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
def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    pyautogui.moveTo(click_x, click_y, duration=0.1)  # 减少移动时间
    pyautogui.click(click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.1)  # 减少等待时间
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
    global running, current_character_index  # 声明所有需要的全局变量
    window_title = "Phone-OBN7WS7D99EYFI49" 
    while not stop_event.is_set():
        if running:
            # 获取窗口区域
            region = get_window_position(window_title)  # 返回 (x, y, width, height)
            print(f"[主循环] 窗口区域: {region}")
            
            # 检查窗口是否最小化
            if win32gui.IsIconic(window_title):
                win32gui.ShowWindow(window_title, win32con.SW_RESTORE)
                time.sleep(0.05)  # 减少等待时间
            
            # 激活窗口
            try:
                win32gui.SetForegroundWindow(window_title)
            except:
                pass
            if index == 0:
                time.sleep(0.1)  # 减少等待时间
                # 点击窗口顶部激活窗口
                click_top_center(window_title)
                index = 1
            else:
                pass
            print("[主循环] 开始查找模板...")
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