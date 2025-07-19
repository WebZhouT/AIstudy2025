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
# 游戏图标模板路径
ICON_TEMPLATE = "F:\\AIstudy2025\\aitest\\test\\mouse.png"  # 需要截取梦幻西游的鼠标图标
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
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
            
            print(f"匹配成功，点击坐标: ({center_x}, {center_y})")
            # 游戏图标模板路径
            ICON_TEMPLATE = "F:\\dream_icon.png"  # 需要截取梦幻西游的鼠标图标
            # 添加移动轨迹可见
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(2)
            # pyautogui.click(center_x, center_y, duration=1)
            # 考虑偏移的点击
            move_icon_to_target(center_x, center_y, ICON_TEMPLATE)
            time.sleep(2)
            return True, (center_x, center_y)
            
    except Exception as e:
        print(f"匹配过程中出错: {e}")
    return False, None
def get_dynamic_offset(icon_template_path):
    """动态获取游戏图标与鼠标的实际偏移"""
    try:
        # 获取鼠标当前位置
        mouse_x, mouse_y = pyautogui.position()
        
        # 截取鼠标周围区域（假设图标在鼠标附近100x100像素范围内）
        region = (mouse_x-50, mouse_y-50, 100, 100)
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 匹配图标
        template = cv2.imread(icon_template_path)
        res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val > 0.8:
            # 计算图标中心相对于鼠标的位置
            h, w = template.shape[:2]
            icon_x = max_loc[0] + w//2
            icon_y = max_loc[1] + h//2
            
            # 计算偏移量（图标中心 - 鼠标位置 + 区域偏移）
            offset_x = icon_x - 50  # 因为区域是鼠标-50开始的
            offset_y = icon_y - 50
            return (offset_x, offset_y)
            
    except Exception as e:
        print(f"动态获取偏移量失败: {e}")
    return (0, 0)  # 默认无偏移

def move_icon_to_target(target_x, target_y, icon_template_path):
    """将游戏图标动态移动到目标位置"""
    try:
        # 首先获取当前偏移量
        offset_x, offset_y = get_dynamic_offset(icon_template_path)
        print(f"检测到动态偏移量: X:{offset_x}, Y:{offset_y}")
        
        # 计算鼠标需要移动的位置
        mouse_x = target_x - offset_x
        mouse_y = target_y - offset_y
        
        # 移动鼠标（使图标到达目标位置）
        pyautogui.moveTo(mouse_x, mouse_y, duration=0.5)
        time.sleep(0.3)
        
        # 验证图标位置
        new_offset_x, new_offset_y = get_dynamic_offset(icon_template_path)
        icon_x = mouse_x + new_offset_x
        icon_y = mouse_y + new_offset_y
        
        distance = ((icon_x - target_x)**2 + (icon_y - target_y)**2)**0.5
        if distance < 15:  # 允许15像素误差
            print(f"图标已到达目标位置({target_x}, {target_y})")
            pyautogui.click(target_x, target_y)  # 直接点击目标坐标
            return True
        else:
            print(f"图标未准确到位，当前在({icon_x}, {icon_y})")
            return False
            
    except Exception as e:
        print(f"图标移动失败: {e}")
        return False
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
    region = (956, 13, 916, 827)  # 1800-920=880
    
    # 检查顶部颜色
    check_top_color_and_operate(region)
    time.sleep(3)
    # 执行模板匹配（提高阈值到0.7）
    find_and_click_template(region, template_path3, 0.2)
    # time.sleep(1)
    # find_and_click_template(region, template_path4, 0.3)

if __name__ == "__main__":
    # 安全设置
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = True
    
    try:
        # while not keyboard.is_pressed('q'):
        main_loop()
        time.sleep(3)
    except KeyboardInterrupt:
        print("程序已停止")
