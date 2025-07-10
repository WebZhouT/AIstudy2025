import pyautogui
import os
import cv2
import numpy as np
from datetime import datetime
import time
import keyboard  # 新增键盘监听库
def is_gray_or_blue(rgb):
    """判断颜色是否为灰色或蓝色"""
    r, g, b = rgb
    is_gray = abs(r - g) < 30 and abs(g - b) < 30
    is_blue = b > r + 50 and b > g + 50
    return is_gray or is_blue

def find_and_click_template(main_region, template_path, confidence=0.8):
    """
    在指定区域内查找模板图片并点击匹配区域
    :param main_region: (x, y, width, height) 主搜索区域
    :param template_path: 模板图片路径
    :param confidence: 匹配置信度阈值(0-1)
    :return: 是否找到并点击了模板
    """
    # 1.截取主区域图像
    x, y, width, height = main_region
    screenshot = pyautogui.screenshot(region=main_region)
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    
    # 2.读取模板图像
    template = cv2.imread(template_path, 0)
    if template is None:
        print(f"无法加载模板图片: {template_path}")
        return False
    
    # 3.模板匹配
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= confidence:
        # 计算点击位置(相对主区域)
        w, h = template.shape[::-1]
        center_x = x + max_loc[0] + w // 2
        center_y = y + max_loc[1] + h // 2
        
        pyautogui.click(center_x, center_y)
        print(f"找到模板并点击 ({center_x}, {center_y})")
        return True
    else:
        print("未找到匹配的模板")
        return False
    # 4.监听前面的截图区域内的区域图像内容是否变化，如果没变化了输出没变化

def capture_region(region, save_dir="screenshots", template_path=None):
    """
    截图指定区域并执行操作
    新流程：
    1. 判断区域顶部颜色是否为灰色/蓝色
    2. 如果是，点击顶部和中间位置
    3. 按Tab键
    4. 截图
    5. 如果提供了模板图片，尝试匹配并点击
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    x, y, width, height = region
    
    # 1. 检查顶部40px区域颜色
    try:
        top_color = pyautogui.pixel(x, y + 20)
        if is_gray_or_blue(top_color):
            print("检测到灰色/蓝色顶部区域")
            # 2. 点击顶部和中间
            pyautogui.click(x + width//2, y + 20)
            time.sleep(0.5)
            pyautogui.click(x + width//2, y + height//2)
            time.sleep(0.5)
            # 3. 按Tab键
            pyautogui.press('tab')
            time.sleep(0.5)
    except Exception as e:
        print(f"颜色检测/操作失败: {e}")
    
    # 4. 截图保存
    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    print(f"截图已保存: {filename}")
    
    # 5. 模板匹配
    if template_path and os.path.exists(template_path):
        find_and_click_template(region, template_path)
    # 读取模板图像
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"无法加载模板图片: {template_path}")
        return False
    # 模板匹配
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= 0.8:
        # 计算点击位置(绝对坐标)
        w, h = template.shape[::-1]
        center_x = x + max_loc[0]
        center_y = y + max_loc[1]
        
        # pyautogui.click(center_x, center_y)
        # print(f"找到模板并点击 ({center_x}, {center_y})，匹配度: {max_val:.2f}")
        try:
            # 添加小范围随机偏移
            import random
            center_x += random.randint(-2, 2)
            center_y += random.randint(-2, 2)
            
            # 物理点击流程
            pyautogui.moveTo(center_x, center_y, duration=random.uniform(1, 5))
            time.sleep(random.uniform(1,3))
            pyautogui.mouseDown()
            time.sleep(random.uniform(0.1, 1))
            pyautogui.mouseUp()
            
            print(f"物理点击完成 ({center_x}, {center_y}) 匹配度: {max_val:.2f}")
            return True
        except Exception as e:
            print(f"点击操作失败: {e}")
            return False
        # return True
    else:
        print(f"未找到匹配的模板 (最高匹配度: {max_val:.2f})")
        return False
    
    # 4. 监听截图区域内容变化
    prev_img = screenshot_gray
    no_change_count = 0
    max_no_change = 2  # 连续无变化次数阈值
    
    while True:
        try:
            # 获取当前区域截图（不保存文件）
            current_screenshot = pyautogui.screenshot(region=region)
            current_np = np.array(current_screenshot)
            current_gray = cv2.cvtColor(current_np, cv2.COLOR_BGR2GRAY)
            
            # 计算差异
            diff = cv2.absdiff(prev_img, current_gray)
            changed_pixels = np.count_nonzero(diff)
            
            if changed_pixels < 100000:  # 变化像素数阈值
                no_change_count += 1
                print(f"区域内容无变化 ({no_change_count}/{max_no_change})")
                
                if no_change_count >= max_no_change:
                    print("连续无变化，按下F9键")
                    keyboard.press_and_release('f9')
                    no_change_count = 0
                    break
            else:
                no_change_count = 0
                print(f"区域内容有变化 (变化像素: {changed_pixels})")
            
            prev_img = current_gray
            time.sleep(1)
            
        except Exception as e:
            print(f"监控出错: {e}")
            time.sleep(2)
            continue
if __name__ == "__main__":
    # 使用示例：
    # 1. 先手动截图目标按钮/区域保存为template.png
    # 2. 设置监控区域和模板路径
    capture_region(
        region=(919, 0, 812, 663),
        save_dir="screenshots",
        # 匹配的图片路径是/test/template.png
        template_path = "F:\\AIstudy2025\\aitest\\test\\1.png"  # 替换为你的模板图片路径
    )