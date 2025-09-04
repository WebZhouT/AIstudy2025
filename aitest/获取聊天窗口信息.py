from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import pyautogui
import logging
from datetime import datetime
import ctypes  # 用于系统弹窗
import time  # 新增用于定时
import win32gui  # 添加这一行
from win10toast import ToastNotifier
# 初始化 OCR 引擎
ocr = RapidOCR()
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
# 配置日志
logging.basicConfig(
    filename='screen_text.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def show_alert(message, use_toast=True):
    """显示提醒（可选择Toast或传统弹窗）"""
    if use_toast:
        toaster.show_toast(
            "文本检测提醒",
            message,
            duration=5,
            threaded=True
        )
    else:
        ctypes.windll.user32.MessageBoxW(0, message, "文本检测提醒", 1)

def capture_region(x1, y1, x2, y2):
    """截取屏幕指定区域并返回图像对象"""
    screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
    return np.array(screenshot)

def recognize_text(img_array):
    """
    识别图片中的文本（保留中文、英文、数字和常见标点符号）
    :param img_array: 图像数组
    :return: 识别到的文本
    """
    try:
        # 执行 OCR 识别
        result, _ = ocr(img_array)
        
        # 检查是否有识别结果
        if not result:
            return "未识别到有效文字"
        
        # 提取所有文本
        recognized_texts = []
        for text_info in result:
            if text_info and len(text_info) > 1:
                recognized_texts.append(text_info[1])
        
        # 将OCR结果合并为字符串
        full_text = "\n".join(recognized_texts)
        
        # 查找包含关键词的完整段落
        key_paragraphs = []
        paragraphs = full_text.split("\n\n")  # 假设段落之间用空行分隔
        KEYWORDS = ["五星二十八","江行初雪","赋图", "树色平远", "千里江山", "山水", "赤壁", "女孝", "女史", "史箴图", "洛神", "洛神赋图"]
        # 添加排除关键词数组
        EXCLUDE_KEYWORDS = ["后赤壁赋"]
        for para in paragraphs:
            # 使用any()检查是否包含任意关键词
            if any(keyword in para for keyword in KEYWORDS):
                # 检查是否包含排除关键词，如果包含则跳过
                if not any(exclude_keyword in para for exclude_keyword in EXCLUDE_KEYWORDS):
                    key_paragraphs.append(para)
        
        # 如果有找到关键词段落，截图保存到本地
        if key_paragraphs:
            show_alert("检测到关键内容")
            # 保存截图到本地文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/screenshot_{timestamp}.png"
            # 需要重新截取完整的PIL图像用于保存
            screenshot = pyautogui.screenshot(region=region_coords)
            screenshot.save(screenshot_path)
            
        return full_text
        
    except Exception as e:
        return f"识别过程中发生错误: {str(e)}"
def get_window_region(window_title):
    """根据窗口标题获取窗口区域坐标"""
    try:
        # 查找窗口句柄
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            show_alert(f"未找到窗口: {window_title}")
            return None
            
        # 获取窗口位置和大小
        rect = win32gui.GetWindowRect(hwnd)
        x1, y1, x2, y2 = rect[0], rect[1], rect[2], rect[3]
        
        # 可选：获取客户端区域（去除边框）
        # client_rect = win32gui.GetClientRect(hwnd)
        # client_x, client_y, client_width, client_height = client_rect
        
        return (x1, y1, x2, y2)
    except Exception as e:
        show_alert(f"获取窗口区域失败: {str(e)}")
        return None
if __name__ == "__main__":
    window_title = "Phone-E6EDU20429087631"  # 请替换为实际的窗口标题
    region_coords = get_window_region(window_title)
    
    while True:
        try:
            print("正在截取屏幕区域...")
            img_array = capture_region(*region_coords)
            
            print("正在进行OCR识别...")
            result = recognize_text(img_array)
            print("\n识别结果:", result)
            
            time.sleep(6)  # 等待10秒
            
        except KeyboardInterrupt:
            print("程序终止")
            break