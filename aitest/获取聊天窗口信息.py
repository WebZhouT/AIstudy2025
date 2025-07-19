from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import pyautogui
import logging
from datetime import datetime
import ctypes  # 用于系统弹窗
import time  # 新增用于定时

# 初始化 OCR 引擎
ocr = RapidOCR()

# 配置日志
logging.basicConfig(
    filename='screen_text.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def show_alert(message):
    """显示系统弹窗"""
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
        for para in paragraphs:
            if "奇货可居" in para or "奇货可居" in para:
                key_paragraphs.append(para)
        
        # 如果有找到关键词段落，保存完整段落
        if key_paragraphs:
            show_alert("检测到关键内容")
            logging.info("检测到关键内容:\n" + "\n\n".join(key_paragraphs))
            
        return full_text
        
    except Exception as e:
        return f"识别过程中发生错误: {str(e)}"

if __name__ == "__main__":
    # 定义监测区域坐标
    region_coords = (1570, 13, 1932, 652)
    
    while True:
        try:
            print("正在截取屏幕区域...")
            img_array = capture_region(*region_coords)
            
            print("正在进行OCR识别...")
            result = recognize_text(img_array)
            print("\n识别结果:", result)
            
            time.sleep(3)  # 等待10秒
            
        except KeyboardInterrupt:
            print("程序终止")
            break