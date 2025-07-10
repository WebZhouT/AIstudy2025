import pyautogui
import os
import cv2
import numpy as np
from datetime import datetime
import time
import keyboard

def is_gray_or_blue(rgb):
    """判断颜色是否为灰色或蓝色"""
    r, g, b = rgb
    is_gray = abs(r - g) < 30 and abs(g - b) < 30
    is_blue = b > r + 50 and b > g + 50
    return is_gray or is_blue

def find_and_click_template(main_region, template_path, confidence=0.8):
    """
    在指定区域内查找模板图片并移动鼠标到匹配区域
    :param main_region: (x, y, width, height) 主搜索区域
    :param template_path: 模板图片路径
    :param confidence: 匹配置信度阈值(0-1)
    :return: 是否找到并移动鼠标到模板
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
        # 计算移动位置(相对主区域)
        w, h = template.shape[::-1]
        center_x = x + (max_loc[0] + w // 2)
        center_y = y + (max_loc[1] + h // 2)
        
        # 改为平滑移动鼠标
        pyautogui.moveTo(center_x, center_y, duration=0.5, tween=pyautogui.easeInOutQuad)
        print(f"找到模板并移动鼠标到 ({center_x}, {center_y})")
        
        # 在30像素半径范围内移动鼠标寻找第二个模板
        template_path2 = "F:\\AIstudy2025\\aitest\\test\\2.png"
        template2 = cv2.imread(template_path2, 0)
        if template2 is None:
            print(f"无法加载第二个模板图片: {template_path2}")
            return False
                
        w2, h2 = template2.shape[::-1]
        radius = 30
        steps = 12  # 搜索点数
        found = False
        
        print("\n开始12点搜索匹配:")
        # 初始化搜索坐标
        search_x, search_y = center_x, center_y
        # 坐标1610，246 直接点击
        if (1610, 246) == (search_x, search_y):
            # 鼠标移动到这个位置延迟1秒后点击
            pyautogui.moveTo(1610, 246, duration=0.5)
            time.sleep(1)
            pyautogui.click()
            print("点击(1610, 246)")
            return True
        # for angle in range(0, 360, 360//steps):
        #     rad = angle * np.pi / 180
        #     search_x = int(center_x + radius * np.cos(rad))
        #     search_y = int(center_y + radius * np.sin(rad))
        #     pyautogui.moveTo(search_x, search_y, duration=0.2)
            
        #     # 检查当前鼠标位置是否为白色
        #     try:
        #         pixel_color = pyautogui.pixel(search_x, search_y)
        #         if pixel_color == (255, 255, 255):  # 检测纯白色
        #             print(f"点{angle//30} ({search_x},{search_y}) 检测到白色像素，直接进行点击")
        #             pyautogui.click()
        #             found = True
        #             break
        #     except:
        #         print(f"点{angle//30} ({search_x},{search_y}) 颜色检测失败")
        #         pass
            
        #     # 截取当前鼠标位置附近的区域进行匹配
        #     template2 = cv2.imread(template_path2, 0)
        #     if template2 is None:
        #         print(f"无法加载第二个模板图片: {template_path2}")
        #         return False
                
        #     w2, h2 = template2.shape[::-1]
        #     small_region = (search_x-w2//2, search_y-h2//2, w2, h2)
        #     try:
        #         small_screenshot = pyautogui.screenshot(region=small_region)
        #         small_np = np.array(small_screenshot)
        #         small_gray = cv2.cvtColor(small_np, cv2.COLOR_BGR2GRAY)
                
        #         res2 = cv2.matchTemplate(small_gray, template2, cv2.TM_CCOEFF_NORMED)
        #         min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
                
        #         print(f"点{angle//30} ({search_x},{search_y}) 匹配度: {max_val2:.4f}")
                
        #         if max_val2 >= 0.25:
        #             print(f"找到第二个模板 (匹配度: {max_val2:.4f})，进行点击")
        #             pyautogui.click()
        #             found = True
        #             break
        #     except Exception as e:
        #         print(f"点{angle//30} ({search_x},{search_y}) 截图或匹配失败: {e}")
                
        if not found:
            print("\n12点搜索完成，未找到匹配的模板")
        return True
    else:
        print("未找到匹配的模板")
        return False

def check_top_color_and_operate(region):
    """检查顶部颜色并执行相应操作"""
    x, y, width, height = region
    try:
        top_color = pyautogui.pixel(x, y + 20)
        if is_gray_or_blue(top_color):
            print("检测到灰色/蓝色顶部区域")
            # 点击顶部和中间
            pyautogui.click(x + width//2, y + 20)
            time.sleep(0.5)
            pyautogui.click(x + width//2, y + height//2)
            time.sleep(0.5)
            # 按Tab键
            pyautogui.press('tab')
            time.sleep(0.5)
    except Exception as e:
        print(f"颜色检测/操作失败: {e}")

def save_screenshot(region, save_dir="screenshots"):
    """截图并保存到指定目录"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    screenshot = pyautogui.screenshot(region=region)
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    print(f"截图已保存: {filename}")
    return screenshot_gray

def monitor_region_changes(region, prev_img):
    """监控区域内容变化"""
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
                    # 再按下快捷键ALT+H
                    keyboard.press_and_release('alt+h')
                    time.sleep(1)
                    # 再按下快捷键alt
                    keyboard.press_and_release('alt')
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

def capture_region(region, save_dir="screenshots", template_path=None):
    """
    截图指定区域并执行操作
    新流程：
    1. 判断区域顶部颜色是否为灰色/蓝色
    2. 如果是，点击顶部和中间位置
    3. 按Tab键
    4. 截图
    5. 如果提供了模板图片，尝试匹配并移动鼠标
    """
    # 1-3. 检查顶部颜色并执行操作
    check_top_color_and_operate(region)
    
    # 4. 截图保存
    screenshot_gray = save_screenshot(region, save_dir)
    
    # 5. 模板匹配
    if template_path and os.path.exists(template_path):
        if find_and_click_template(region, template_path):
            # 6. 监听截图区域内容变化
            monitor_region_changes(region, screenshot_gray)

if __name__ == "__main__":
    # 使用示例：
    # 1. 先手动截图目标按钮/区域保存为template.png
    # 2. 设置监控区域和模板路径
    capture_region(
        region=(920, 0, 1800, 642),
        save_dir="screenshots",
        # 匹配的图片路径是/test/template.png
        template_path = "F:\\AIstudy2025\\aitest\\test\\1.png"  # 替换为你的模板图片路径
    )