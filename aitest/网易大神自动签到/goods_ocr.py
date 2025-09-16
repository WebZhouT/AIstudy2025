import pyautogui
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import json
import time
import win32gui
import win32con
import os
import keyboard
import threading

# 初始化 OCR 引擎
ocr = RapidOCR()

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
aimData = ''  # 当前操作的目标角色名字

def match_and_click_template(screenshot, template_path, threshold, region=None):
    """
    匹配模板并返回匹配结果
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_and_click_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            x, y = max_loc
            
            # 返回相对于传入截图的坐标（不是绝对坐标）
            center_x = x + w // 2
            center_y = y + h // 2
            
            print(f"[match_and_click_template] 匹配成功，相对位置: ({center_x}, {center_y})")
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

# 添加查找窗口的函数
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

def recognize_goods_text():
    """
    识别屏幕中goods.png区域的文字并保存到日志文件
    """
    print("[识别奖励] 开始识别奖励内容...")
    
    # 获取指定窗口区域
    window_title = "Phone-OBN7WS7D99EYFI49" 
    hwnd = find_window_by_title(window_title)
    
    if not hwnd:
        print(f"[识别奖励] 未找到窗口: {window_title}")
        return
    
    # 获取窗口区域
    window_region = get_window_position(hwnd)
    print(f"[识别奖励] 窗口区域: {window_region}")
    
    # 先截取整个窗口用于调试
    window_screenshot = pyautogui.screenshot(region=window_region)
    window_screenshot.save("debug_window_screenshot.png")
    print("[识别奖励] 已保存窗口截图用于调试")
    
    # 查找goods.png模板在窗口中的位置
    template_path = "goods.png"
    template = cv2.imread(template_path)
    if template is None:
        print(f"[识别奖励] 无法读取模板图片 {template_path}")
        return
    
    # 将PIL图像转换为OpenCV格式
    open_cv_image = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
    
    # 在窗口截图中匹配goods.png模板
    res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    threshold = 0.8
    if max_val >= threshold:
        # 计算匹配区域的坐标（相对于整个屏幕）
        h, w = template.shape[:2]
        top_left = (window_region[0] + max_loc[0], window_region[1] + max_loc[1])
        bottom_right = (top_left[0] + w, top_left[1] + h)
        
        # 截取匹配区域（基于屏幕绝对坐标）
        goods_region = (top_left[0], top_left[1], w, h)
        goods_screenshot = pyautogui.screenshot(region=goods_region)
        goods_screenshot.save("goods_region.png")
        print("[识别奖励] 已保存匹配区域截图")
        
        # 对截取的区域进行OCR识别
        img = cv2.cvtColor(np.array(goods_screenshot), cv2.COLOR_RGB2BGR)
        result, elapse = ocr(img)
        
        print("[识别奖励] 识别结果:")
        if result:
            for line in result:
                print(line[1])  # 输出识别的文字
        else:
            print("[识别奖励] 未识别到文字")
    else:
        print(f"[识别奖励] 未能在窗口中找到goods.png模板，最高匹配度: {max_val:.2f}")

def start_script():
    """启动脚本"""
    global running
    running = True
    print("\n===== 奖励识别已启动，按F1识别奖励内容 =====")

def stop_script():
    """停止脚本"""
    global running
    running = False
    print("\n===== 脚本已停止 =====")

def main_loop():
    """主循环函数"""
    print("[主循环] 正在监听按键...")
    
    while not stop_event.is_set():
        if running:
            # 检查是否按下F1键
            if keyboard.is_pressed('f1'):
                recognize_goods_text()
                # 等待一段时间避免重复触发
                time.sleep(1)
        
        # 等待一段时间再检查
        time.sleep(0.1)

def main():
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("提示: 按 F1 启动奖励识别，按 F2 停止脚本")
    print("启动后，按 F1 识别屏幕中 goods.png 区域的文字内容")
    
    try:
        # 启动主循环
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()