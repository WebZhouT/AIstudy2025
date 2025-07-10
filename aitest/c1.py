import pyautogui
import time
import random

def click_npc():
    # 方法1：图像识别（首选）
    if click_by_image():
        return True
        
    # 方法2：固定坐标+容差（备选）
    return click_by_coordinate_with_retry()

def click_by_image():
    """使用图像识别点击NPC"""
    try:
        # 在屏幕上查找NPC图像
        location = pyautogui.locateCenterOnScreen("F:\\AIstudy2025\\aitest\\test\\1.png", confidence=0.8)
        if location:
            pyautogui.moveTo(location.x, location.y, duration=0.3)
            time.sleep(0.3)
            pyautogui.click()
            print(f"图像识别点击 ({location.x}, {location.y})")
            return True
    except Exception as e:
        print(f"图像识别错误: {e}")
    return False

def click_by_coordinate_with_retry():
    """使用固定坐标+随机容差点击"""
    base_x, base_y = 1610, 246  # 你的基础坐标
    tolerance = 20  # 允许的偏移范围
    
    for attempt in range(3):  # 尝试3次
        # 在基础坐标附近随机生成一个点
        target_x = base_x + random.randint(-tolerance, tolerance)
        target_y = base_y + random.randint(-tolerance, tolerance)
        
        pyautogui.moveTo(target_x, target_y, duration=0.3)
        time.sleep(0.3)
        pyautogui.click()
        print(f"坐标点击尝试 #{attempt+1} ({target_x}, {target_y})")
        
        # 添加点击后的验证逻辑（可选）
        time.sleep(1)  # 等待响应
        if verify_click_success():
            return True
            
    return False

def verify_click_success():
    """验证点击是否成功（根据你的游戏实际情况实现）"""
    # 示例：检查NPC对话框是否出现
    try:
        if pyautogui.locateOnScreen("dialog_template.png", confidence=0.7):
            print("点击成功验证通过")
            return True
    except:
        pass
    
    print("点击成功验证失败")
    return False

# 使用示例
if click_npc():
    print("NPC点击成功！")
else:
    print("NPC点击失败，请检查")