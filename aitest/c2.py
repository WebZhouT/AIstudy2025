import pyautogui
import os
import cv2
import numpy as np
from datetime import datetime
import time
import keyboard
from PIL import ImageGrab

class MouseOffsetCorrector:
    def __init__(self, region):
        # 剑柄特征点配置（根据实际游戏画面调整）
        self.sword_config = {
            'base_color': (136, 96, 32),     # 剑柄基础颜色 (BGR格式)
            'offset_points': [               # 特征点相对位置和颜色
                (5, 3, (224, 208, 120)),     # dx, dy, color
                (6, 5, (192, 156, 104)),
                (3, 4, (136, 112, 56)),
                (-1, 2, (88, 64, 40))
            ],
            'tip_offset': (22, 22)           # 剑尖相对于剑柄的偏移量
        }
        self.screen_region = region  # 屏幕检测区域
        self.last_correction = (0, 0)  # 记录最后一次校正量
    
    def find_sword_handle(self):
        """识别鼠标剑柄位置"""
        # 截取屏幕区域
        try:
            screen = np.array(ImageGrab.grab(bbox=self.screen_region))
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            
            # 基础颜色匹配
            base_color = np.array(self.sword_config['base_color'])
            color_mask = cv2.inRange(screen, base_color-20, base_color+20)
            
            # 多点特征匹配
            for dx, dy, color in self.sword_config['offset_points']:
                color_arr = np.array(color)
                offset_mask = cv2.inRange(screen, color_arr-10, color_arr+10)
                # 对特征点位置进行偏移计算
                if dx >= 0 and dy >= 0:
                    shifted_mask = np.roll(offset_mask, -dy, axis=0)
                    shifted_mask = np.roll(shifted_mask, -dx, axis=1)
                    color_mask = cv2.bitwise_and(color_mask, shifted_mask)
                else:
                    # 处理负偏移
                    shifted_mask = np.roll(offset_mask, abs(dy), axis=0)
                    shifted_mask = np.roll(shifted_mask, abs(dx), axis=1)
                    color_mask = cv2.bitwise_and(color_mask, shifted_mask)
            
            # 寻找匹配点
            contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                # 取最大轮廓的中心点
                max_contour = max(contours, key=cv2.contourArea)
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return cx, cy
        except Exception as e:
            print(f"鼠标偏移校正失败: {e}")
        
        return None

    def calculate_offset(self, target_x, target_y):
        """计算并返回偏移量"""
        handle_pos = self.find_sword_handle()
        if not handle_pos:
            print("未检测到鼠标指针，使用默认位置")
            return self.last_correction  # 返回上次校正值
        
        # 计算实际剑尖位置
        tip_x = handle_pos[0] + self.screen_region[0] - self.sword_config['tip_offset'][0]
        tip_y = handle_pos[1] + self.screen_region[1] - self.sword_config['tip_offset'][1]
        
        # 计算偏移量
        offset_x = target_x - tip_x
        offset_y = target_y - tip_y
        
        # 保存本次校正值
        self.last_correction = (offset_x, offset_y)
        print(f"检测到偏移: X:{offset_x} Y:{offset_y} | 剑柄:{handle_pos} 剑尖:({tip_x},{tip_y})")
        return offset_x, offset_y

    def accurate_click(self, target_x, target_y):
        """执行精确点击"""
        offset_x, offset_y = self.calculate_offset(target_x, target_y)
        
        # 应用偏移并点击
        final_x = target_x + offset_x
        final_y = target_y + offset_y
        
        pyautogui.moveTo(final_x, final_y, duration=0.2)
        pyautogui.click()
        print(f"已校正点击: 原始({target_x},{target_y}) -> 实际({final_x},{final_y})")
        return final_x, final_y

def is_gray_or_blue(rgb):
    """判断颜色是否为灰色或蓝色"""
    r, g, b = rgb
    is_gray = abs(r - g) < 30 and abs(g - b) < 30
    is_blue = b > r + 50 and b > g + 50
    return is_gray or is_blue

def find_and_click_template(main_region, template_path, confidence=0.8, offset_corrector=None):
    """
    在指定区域内查找模板图片并移动鼠标到匹配区域
    :param main_region: (x, y, width, height) 主搜索区域
    :param template_path: 模板图片路径
    :param confidence: 匹配置信度阈值(0-1)
    :param offset_corrector: 鼠标偏移校正器实例
    :return: 是否找到并移动鼠标到模板
    """
    # 1.截取主区域图像
    x, y, width, height = main_region
    screenshot = pyautogui.screenshot(region=main_region)
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # 2.读取模板图像
    template = cv2.imread(template_path)
    if template is None:
        print(f"无法加载模板图片: {template_path}")
        return False
    
    # 3.模板匹配
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 4.检查匹配结果
    if max_val < confidence:
        print(f"未找到匹配模板 (最大置信度: {max_val:.2f})")
        return False
    
    # 5.计算匹配位置中心点
    tw, th = template.shape[1], template.shape[0]
    match_x = x + max_loc[0] + tw // 2
    match_y = y + max_loc[1] + th // 2
    
    # 6.执行点击（使用偏移校正）
    if offset_corrector:
        offset_corrector.accurate_click(match_x, match_y)
    else:
        pyautogui.moveTo(match_x, match_y, duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        print(f"点击({match_x}, {match_y})")
    
    return True

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    print(f"截图已保存: {filename}")
    return np.array(screenshot.convert('L'))  # 返回灰度图像数组

def monitor_region_changes(region, prev_img):
    """监控区域内容变化"""
    no_change_count = 0
    max_no_change = 2  # 连续无变化次数阈值
    
    while True:
        try:
            # 获取当前区域截图
            current_screenshot = pyautogui.screenshot(region=region)
            current_np = np.array(current_screenshot.convert('L'))
            
            # 计算差异
            diff = cv2.absdiff(prev_img, current_np)
            changed_pixels = np.count_nonzero(diff > 25)  # 阈值25，忽略微小变化
            
            if changed_pixels < 1000:  # 降低变化像素数阈值
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
            
            prev_img = current_np
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
    # 初始化鼠标偏移校正器
    offset_corrector = MouseOffsetCorrector(region)
    
    # 1-3. 检查顶部颜色并执行操作
    check_top_color_and_operate(region)
    
    # 4. 截图保存
    screenshot_gray = save_screenshot(region, save_dir)
    
    # 5. 模板匹配
    if template_path and os.path.exists(template_path):
        if find_and_click_template(region, template_path, offset_corrector=offset_corrector):
            # 6. 监听截图区域内容变化
            monitor_region_changes(region, screenshot_gray)

if __name__ == "__main__":
    # 使用示例：
    # 1. 先手动截图目标按钮/区域保存为template.png
    # 2. 设置监控区域和模板路径
    
    # 测试前先调整剑柄颜色配置（根据实际游戏画面）
    capture_region(
        region=(920, 0, 1800, 642),
        save_dir="screenshots",
        template_path="F:\\AIstudy2025\\aitest\\test\\1.png"  # 替换为你的模板图片路径
    )