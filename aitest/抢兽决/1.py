import os
import pyautogui
import time
import win32gui
import win32con
import cv2
import numpy as np
import keyboard
import threading

# 全局变量控制运行状态
running = False
stop_event = threading.Event()

def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

def click_at_window_coord(hwnd, x, y):
    """在窗口坐标处点击，不移动鼠标"""
    # 将屏幕坐标转换为窗口客户区坐标
    point = (x, y)
    client_point = win32gui.ScreenToClient(hwnd, point)
    
    # 发送点击消息到窗口
    lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
    print(f"[click_at_window_coord] 模拟点击窗口坐标: ({x}, {y}) -> 客户区坐标: ({client_point[0]}, {client_point[1]})")

def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    click_at_window_coord(hwnd, click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.1)  # 减少等待时间

def match_template(screenshot, template_path, threshold, region=None):
    """
    匹配模板但不执行点击操作
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2]  # 彩色图片shape是(h,w,3)
            x, y = max_loc
            
            if region:
                # 区域参数为(x,y,width,height)
                region_x, region_y, region_w, region_h = region
                
                # 计算模板中心点相对于全屏的坐标
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
                
                # 验证坐标是否在区域内
                if not (region_x <= center_x <= region_x + region_w and 
                        region_y <= center_y <= region_y + region_h):
                    print(f"[match_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                # 如果没有提供区域，则直接使用匹配位置
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"[match_template] 匹配成功，坐标: ({center_x}, {center_y})")
            return True, (center_x, center_y)
        else:
            print(f"[match_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def match_and_click_template(hwnd, screenshot, template_path, threshold, region=None):
    """
    匹配模板并执行虚拟点击操作
    """
    matched, pos = match_template(screenshot, template_path, threshold, region)
    
    if matched:
        center_x, center_y = pos
        # 使用虚拟点击而不是物理移动鼠标
        click_at_window_coord(hwnd, center_x, center_y)
        print(f"[match_and_click_template] 已虚拟点击坐标: ({center_x}, {center_y})")
        time.sleep(0.05)
        
    return matched, pos

def find_template(region, template_path, threshold):
    """在指定区域查找模板"""
    try:
        # 获取当前屏幕彩色截图
        print(f"[find_template] 截图区域: {region}")
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配
        matched, pos = match_template(screenshot_cv, template_path, threshold, region)
        
        return matched, pos
    except Exception as e:
        print(f"[find_template] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(hwnd, region, template_path, threshold):
    """在指定区域查找并虚拟点击模板"""
    try:
        # 获取当前屏幕彩色截图
        print(f"[find_and_click_template] 截图区域: {region}")
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配并虚拟点击
        matched, pos = match_and_click_template(hwnd, screenshot_cv, template_path, threshold, region)
        
        return matched
    except Exception as e:
        print(f"[find_and_click_template] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def wait_for_template(region, template_path, threshold, timeout=10):
    """等待模板出现，超时返回False"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if stop_event.is_set() or not running:
            return False
            
        matched, pos = find_template(region, template_path, threshold)
        if matched:
            return True
            
        time.sleep(0.5)
    
    print(f"[wait_for_template] 等待模板 {template_path} 超时")
    return False

def start_script():
    """启动脚本"""
    global running
    running = True
    print("\n===== 脚本已启动 =====")

def stop_script():
    """停止脚本"""
    global running
    running = False
    print("\n===== 脚本已停止 =====")

def main_loop():
    """主循环函数"""
    window_title = "Phone-OBN7WS7D99EYFI49" 
    template_path = "t1.png"  # 替换为你的模板图片路径
    template_path2 = "t2.png"  # 替换为你的模板图片路径
    template_path3 = "t3.png"  # 替换为你的模板图片路径
    goodsbj = "t4.png"  # 替换为你的模板图片路径
    template_path4 = "btn3.png"  # 替换为你的模板图片路径
    template_path5 = "close.png"  # 新增关闭按钮模板路径
    sj = "sj.png"  # 商品模板路径
    close2 = "close2.png"  # 新增关闭按钮模板路径
    threshold = 0.2  # 匹配阈值
    index = 0
    print(f"[主循环] 正在监听窗口: {window_title}")

    while not stop_event.is_set():
        if running:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                print(f"[主循环] 找到窗口句柄: {hwnd}")
                
                # 获取窗口区域
                region = get_window_position(hwnd)  # 返回 (x, y, width, height)
                print(f"[主循环] 窗口区域: {region}")
                
                # 检查窗口是否最小化
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.05)  # 减少等待时间
                
                # 激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
                if index == 0:
                    time.sleep(0.1)  # 减少等待时间
                    # 点击窗口顶部激活窗口
                    click_top_center(hwnd)
                    index = 1
                else:
                    pass

                
                # 在窗口区域内查找并虚拟点击模板 - 改为流式写法并循环匹配直到找到
                print("[主循环] 开始查找模板...")
                
                # 步骤1: 等待并点击第一个模板
                if not wait_for_template(region, template_path, threshold, timeout=10):
                    print("[主循环] 未找到第一个模板，重新开始")
                    continue
                
                # 点击第一个模板
                find_and_click_template(hwnd, region, template_path, threshold)
                print("[主循环] 成功找到目标NPC并点击了模板")
                time.sleep(0.5)  # 增加等待时间确保界面稳定
                
                # 步骤2: 等待并点击第二个模板
                if not wait_for_template(region, template_path2, 0.8, timeout=10):
                    print("[主循环] 未找到第二个模板，重新开始")
                    continue
                
                # 点击第二个模板
                find_and_click_template(hwnd, region, template_path2, 0.7)
                print("[主循环] 点击购买按钮")
                time.sleep(0.5)  # 增加等待时间确保界面稳定
                
                # 步骤3: 等待并点击第三个模板
                if not wait_for_template(region, template_path3, 0.7, timeout=10):
                    print("[主循环] 未找到第三个模板，重新开始")
                    continue
                
                # 点击第三个模板
                find_and_click_template(hwnd, region, template_path3, 0.7)
                print("[主循环] 点击购买按钮")
                time.sleep(0.5)  # 增加等待时间确保界面稳定
                
                # 步骤4: 等待商品背景出现
                if not wait_for_template(region, goodsbj, 0.6, timeout=10):
                    print("[主循环] 未找到商品背景，重新开始")
                    continue
                
                print("[主循环] 找到商品背景")
                time.sleep(0.5)  # 增加等待时间确保界面稳定
                
                # 步骤5: 查找商品模板 - 特殊处理，如果找不到则点击关闭并重新开始
                found_product = False
                # 直接尝试查找商品，不等待
                matched, pos = find_template(region, sj, 0.7)
                if matched:
                    # 找到商品，点击它
                    find_and_click_template(hwnd, region, sj, 0.7)
                    print("[主循环] 点击商品")
                    found_product = True
                    time.sleep(0.5)  # 增加等待时间确保界面稳定
                else:
                    # 未找到商品，点击关闭按钮后重新开始
                    print("[主循环] 未找到商品目标，点击关闭按钮后重新开始...")
                    find_and_click_template(hwnd, region, template_path5, 0.4)
                    time.sleep(0.2)  # 增加等待时间
                    continue
                
                # 步骤6: 等待并点击确认按钮
                if found_product:
                    if not wait_for_template(region, template_path4, 0.8, timeout=10):
                        print("[主循环] 未找到确认按钮，重新开始")
                        continue
                    
                    # 点击确认按钮
                    find_and_click_template(hwnd, region, template_path4, 0.8)
                    print("[主循环] 完成第四个操作")
                    time.sleep(0.5)  # 增加等待时间确保界面稳定
                
                # 新增：如果已完成前面所有步骤，则重复执行点击商品和点击template_path4
                if found_product and not stop_event.is_set() and running:
                    print("[主循环] 开始重复执行点击商品和点击确认按钮...")
                    
                    while not stop_event.is_set() and running:
                        # 先点击关闭按钮
                        find_and_click_template(hwnd, region, close2, 0.8)
                        
                        # 直接尝试查找商品，不等待
                        if find_and_click_template(hwnd, region, sj, 0.8):
                            print("[主循环] 重复点击商品成功")
                            time.sleep(0.5)
                            
                            # 等待并点击确认按钮
                            if wait_for_template(region, template_path4, 0.8, timeout=5):
                                find_and_click_template(hwnd, region, template_path4, 0.8)
                                print("[主循环] 重复点击确认按钮成功")
                                time.sleep(0.5)
                            else:
                                print("[主循环] 重复点击确认按钮失败，继续下一轮")
                                time.sleep(1)
                        else:
                            print("[主循环] 重复点击商品失败，继续下一轮")
                            time.sleep(1)
                
                print("[主循环] 等待下一次扫描...")
            else:
                print("[主循环] 未找到窗口")
            
            # 等待1秒再进行下一次扫描
            time.sleep(0.1)  # 增加每次等待时间
            print("\r" + " " * 30, end="\r")  # 清除倒计时行
        else:
            # 脚本停止状态，每秒检查一次
            time.sleep(0.1)  # 增加检查间隔

def main():
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("提示: 按 F1 启动脚本，按 F2 停止脚本")
    
    try:
        # 启动主循环
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()