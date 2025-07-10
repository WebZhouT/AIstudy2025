import pyautogui
import os
import cv2
import numpy as np
import time
import keyboard

def is_gray_or_blue(rgb):
    """判断颜色是否为灰色或蓝色"""
    r, g, b = rgb
    is_gray = abs(r - g) < 30 and abs(g - b) < 30
    is_blue = b > r + 50 and b > g + 50
    return is_gray or is_blue

def check_top_color_and_operate(region):
    """检查顶部颜色并执行相应操作"""
    x, y, width, height = region
    try:
        top_color = pyautogui.pixel(x, y + 20)
        if is_gray_or_blue(top_color):
            print("检测到灰色/蓝色顶部区域")
            pyautogui.click(x + width//2, y + 20)
            time.sleep(0.5)
            keyboard.press_and_release('alt+h')
            time.sleep(1)
            keyboard.press_and_release('f9')
    except Exception as e:
        print(f"颜色检测/操作失败: {e}")

# 模板路径
template_path3 = "F:\\AIstudy2025\\aitest\\test\\3.png"
template_path4 = "F:\\AIstudy2025\\aitest\\test\\4.png"
template_path5 = "F:\\AIstudy2025\\aitest\\test\\5.png"

def match_and_click_template(screenshot, template_path, threshold, region=None):
    """
    修正版：匹配模板并执行点击操作
    主要修改点：坐标计算逻辑和彩色匹配
    """
    try:
        # 读取模板图片（保持彩色）
        template = cv2.imread(template_path)
        if template is None:
            print(f"警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"当前匹配度: {max_val:.2f}")
        
        if max_val >= threshold:
            h, w = template.shape[:2]  # 彩色图片shape是(h,w,3)
            x, y = max_loc
            
            # 修正坐标计算逻辑
            if region:
                # 区域参数应为(x,y,width,height)
                region_x, region_y, region_w, region_h = region
                
                # 计算模板中心点相对于全屏的坐标
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
                
                # 验证坐标是否在区域内
                if not (region_x <= center_x <= region_x + region_w and 
                        region_y <= center_y <= region_y + region_h):
                    print(f"警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")
            
            # 添加移动轨迹可见
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(0.1)
            pyautogui.click(center_x, center_y, duration=0.3)
            time.sleep(0.3)
            return True, (center_x, center_y)
            
    except Exception as e:
        print(f"匹配过程中出错: {e}")
    return False, None

def find_and_click_template(region, template_path, threshold):
    """在指定区域查找并点击模板"""
    # 获取当前屏幕彩色截图
    screenshot = pyautogui.screenshot(region=region)
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 进行模板匹配
    matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region)
    
    # 二次匹配逻辑
    if matched and os.path.exists(template_path4):
        time.sleep(0.5)
        new_screenshot = pyautogui.screenshot(region=region)
        new_screenshot_cv = cv2.cvtColor(np.array(new_screenshot), cv2.COLOR_RGB2BGR)
        match_and_click_template(new_screenshot_cv, template_path4, threshold, region)
    
    return matched

def main_loop():
    """主循环函数"""
    print("开始循环匹配(按q键退出)...")
    
    # 修正区域定义：(x,y,width,height)
    region = (920, 0, 880, 642)  # 1800-920=880
    
    # 检查顶部颜色
    check_top_color_and_operate(region)
    
    # 执行模板匹配（提高阈值到0.7）
    find_and_click_template(region, template_path3, 0.7)
    time.sleep(1)
    find_and_click_template(region, template_path4, 0.7)

if __name__ == "__main__":
    # 安全设置
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = True
    
    try:
        while not keyboard.is_pressed('q'):
            main_loop()
            time.sleep(3)
    except KeyboardInterrupt:
        print("程序已停止")
