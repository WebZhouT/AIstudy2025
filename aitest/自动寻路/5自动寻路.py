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
    
    # # 1. 检查顶部40px区域颜色
    try:
        top_color = pyautogui.pixel(x, y + 40)
        time.sleep(3)
        # if is_gray_or_blue(top_color):
        print("检测到灰色/蓝色顶部区域")
        # 2. 点击顶部和中间
        pyautogui.click(x + width//2, y + 40)
        time.sleep(0.5)
        pyautogui.click(x + width//2, y + height//2)
        time.sleep(3)
        # 3. 按Tab键
        pyautogui.press('tab')
        time.sleep(0.5)
    except Exception as e:
        print(f"颜色检测/操作失败: {e}")
    # 2. 点击顶部和中间
    pyautogui.click(x + width//2, y + 40)
    time.sleep(0.5)
    pyautogui.click(x + width//2, y + height//2)
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
    
    if max_val >= 0.4:
        # 计算点击位置(绝对坐标)
        w, h = template.shape[::-1]
        center_x = x + (max_loc[0] + w // 2)
        center_y = y + (max_loc[1] + h // 2)
        # center_x = 1385
        # center_y = 396
        pyautogui.click(center_x, center_y)
        print(f"找到模板并点击 ({center_x}, {center_y})，匹配度: {max_val:.2f}")
        try:
            # 添加小范围随机偏移
            import random
            center_x += random.randint(-2, 2)
            center_y += random.randint(-2, 2)
            # 游戏图标模板路径
            ICON_TEMPLATE = "F:\\AIstudy2025\\aitest\\test\\mouse.png"  # 需要截取梦幻西游的鼠标图标
            # # 物理点击流程
            # pyautogui.moveTo(center_x, center_y, duration=random.uniform(1, 5))
            # time.sleep(random.uniform(1,3))
            # pyautogui.mouseDown()
            # time.sleep(random.uniform(0.1, 1))
            # pyautogui.mouseUp()
            """ =============== """
            # 添加移动轨迹可见
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(2)
            # pyautogui.click(center_x, center_y, duration=1)
            # 考虑偏移的点击
            move_icon_to_target(center_x, center_y, ICON_TEMPLATE)
            """ ============== """
            print(f"物理点击完成 ({center_x}, {center_y}) 匹配度: {max_val:.2f}")
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
                    
                    if changed_pixels < 140000:  # 变化像素数阈值
                        no_change_count += 1
                        print(f"区域内容无变化 ({no_change_count}/{max_no_change})")
                        
                        if no_change_count >= max_no_change:
                            print("连续无变化，按下F9键")
                            keyboard.press_and_release('f9')
                            keyboard.press_and_release('tab')
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


        except Exception as e:
            print(f"点击操作失败: {e}")
            return False
        return True
    else:
        print(f"未找到匹配的模板 (最高匹配度: {max_val:.2f})")

    
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
if __name__ == "__main__":
    # 使用示例：
    # 1. 先手动截图目标按钮/区域保存为template.png
    # 2. 设置监控区域和模板路径
    capture_region(
        region=(956, 13, 916, 827),
        save_dir="screenshots",
        # 匹配的图片路径是/test/template.png
        template_path = "F:\\AIstudy2025\\aitest\\test\\1.png"  # 替换为你的模板图片路径
    )