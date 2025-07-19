import win32gui
import win32ui
import win32con
from PIL import Image
import time
import pyautogui
import cv2
import os
import numpy as np
from rapidocr_onnxruntime import RapidOCR



# 初始化 OCR 引擎
ocr = RapidOCR()

def click_and_screenshot(left, top, right, bottom):
    # 点击窗口顶部位置
    click_x = left + 5  # 顶部10px区域内点击
    click_y = top + 5
    pyautogui.click(click_x, click_y, _pause=False)
    time.sleep(0.2)  # 等待点击完成
    # 延迟5秒执行
    time.sleep(2)
    # 获取窗口截图
    width = right - left
    height = bottom - top
    
    # 创建设备上下文
    hwnd = win32gui.GetDesktopWindow()
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    
    # 截图
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (left, top), win32con.SRCCOPY)
    
    # 转换为PIL图像
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    
    # 保存截图
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"./screenshots/window_{timestamp}.png"
    im.save(filename)
    print(f"截图已保存为: {filename}")
    
    # 释放资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return filename  # 返回生成的截图文件名

def find_template_in_screenshot(screenshot_path, template_path):
    """
    在截图中查找模板图片的位置
    :param screenshot_path: 截图文件路径
    :param template_path: 模板图片路径
    :return: 匹配区域的坐标(x, y, width, height)或None
    """
    # 读取图片
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    
    if screenshot is None or template is None:
        print("无法读取图片文件")
        return None
    
    # 模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 设置相似度阈值
    threshold = 0.4
    if max_val < threshold:
        print(f"未找到匹配区域 (最高相似度: {max_val:.2f})")
        return None
    
    # 获取匹配区域坐标
    h, w = template.shape[:2]
    x, y = max_loc
    return (x, y, w, h)

def crop_matched_region(screenshot_path, template_path, output_path):
    """
    截取匹配的区域并保存
    :param screenshot_path: 截图文件路径
    :param template_path: 模板图片路径
    :param output_path: 输出文件路径
    :return: 成功返回True，失败返回False
    """
    match = find_template_in_screenshot(screenshot_path, template_path)
    if not match:
        return False
    
    x, y, w, h = match
    screenshot = cv2.imread(screenshot_path)
    cropped = screenshot[y:y+h, x:x+w]
    cv2.imwrite(output_path, cropped)
    
    # 计算匹配区域在屏幕中的绝对坐标
    # 截图文件名包含窗口坐标信息，格式为"window_YYYYMMDD_HHMMSS.png"
    # window_coords = screenshot_path.split('_')[-1].replace('.png', '').split('_')
    # window_left = int(window_coords[0])
    # window_top = int(window_coords[1])
    
    # # 绝对坐标 = 窗口坐标 + 匹配区域相对坐标
    # abs_x1 = window_left + x
    # abs_y1 = window_top + y
    # abs_x2 = abs_x1 + w
    # abs_y2 = abs_y1 + h
    
    print(f"匹配区域已保存为: {output_path}")
    # print(f"匹配区域绝对坐标: ({abs_x1}, {abs_y1}, {abs_x2}, {abs_y2})")
    return True

def recognize_text(image_path):
    """
    识别图片中的文本（保留中文、英文、数字和常见标点符号）
    :param image_path: 图片路径
    :return: 识别到的文本
    """
    try:
        # 读取图片
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # 执行 OCR 识别
        result, _ = ocr(img_array)
        
        # 检查是否有识别结果
        if not result:
            return "未识别到有效文字"
        
        # 提取所有文本
        recognized_texts = []
        for text_info in result:
            if text_info and len(text_info) > 1:
                text = text_info[1]
                recognized_texts.append(text)
        print("识别结果：")
        print("\n".join(recognized_texts))
        # 返回合并后的文本
        # return "\n".join(recognized_texts)
    
    except Exception as e:
        return f"识别过程中发生错误: {str(e)}"
if __name__ == "__main__":
    # 调用函数执行操作并获取截图路径
    screenshot_path = click_and_screenshot(888, 0, 1924, 831)
    
    # 示例：查找模板并截取匹配区域
    template_path = "./templates/2.png"
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # 获取当前时间戳
    output_path = f"./screenshots/matched_region_{timestamp}.png"  # 修改为带时间戳的文件名
    crop_matched_region(screenshot_path, template_path, output_path)
    # 识别文本并获取可视化结果
    recognize_text(output_path)
