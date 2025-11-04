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

# 模板缓存，避免重复读取和转换
template_cache = {}
color_templates = ["sj.png"]  # 需要彩色匹配的模板列表

def click_at_window_coord(hwnd, x, y):
    """在窗口坐标处点击，不移动鼠标"""
    # 检查窗口句柄是否有效
    if not hwnd or not win32gui.IsWindow(hwnd):
        print(f"[click_at_window_coord] 错误: 窗口句柄无效")
        return False
    
    # 检查窗口是否可见和启用
    if not win32gui.IsWindowVisible(hwnd):
        print(f"[click_at_window_coord] 警告: 窗口不可见")
        return False
    
    if not win32gui.IsWindowEnabled(hwnd):
        print(f"[click_at_window_coord] 警告: 窗口未启用")
        return False
    
    try:
        # 将屏幕坐标转换为窗口客户区坐标
        point = (x, y)
        client_point = win32gui.ScreenToClient(hwnd, point)
        
        # 发送点击消息到窗口
        lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.01)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        print(f"[click_at_window_coord] 模拟点击窗口坐标: ({x}, {y}) -> 客户区坐标: ({client_point[0]}, {client_point[1]})")
        return True
    
    except Exception as e:
        print(f"[click_at_window_coord] PostMessage点击失败: {str(e)}，尝试备用方案...")
        
        # 备用方案：使用pyautogui直接点击
        try:
            # 先激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            
            # 保存当前鼠标位置
            original_pos = pyautogui.position()
            
            # 移动并点击
            pyautogui.click(x, y)
            
            # 恢复鼠标位置
            pyautogui.moveTo(original_pos)
            
            print(f"[click_at_window_coord] 备用方案点击成功: ({x}, {y})")
            return True
        except Exception as e2:
            print(f"[click_at_window_coord] 备用方案也失败: {str(e2)}")
            return False
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

def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    click_at_window_coord(hwnd, click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.05)

def get_cached_template(template_path):
    """获取缓存的模板（根据模板类型决定使用灰度还是彩色）"""
    if template_path in template_cache:
        return template_cache[template_path]
    
    # 读取模板
    template = cv2.imread(template_path)
    if template is None:
        print(f"[get_cached_template] 警告: 无法读取模板图片 {template_path}")
        return None
    
    # 根据模板类型决定是否转换为灰度
    if template_path in color_templates:
        # 彩色模板，保持原样
        template_cache[template_path] = template
        print(f"[get_cached_template] 加载彩色模板: {template_path}")
    else:
        # 灰度模板，转换为灰度
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_cache[template_path] = template_gray
        print(f"[get_cached_template] 加载灰度模板: {template_path}")
        
    return template_cache[template_path]

def match_and_click_template(screenshot, template_path, threshold, region=None, hwnd=None):
    """
    匹配模板并执行点击操作
    """
    try:
        # 获取缓存的模板
        template = get_cached_template(template_path)
        if template is None:
            return False, None
        
        # 根据模板类型决定匹配方式
        if template_path in color_templates:
            # 彩色匹配
            if len(screenshot.shape) == 3:  # 截图已经是彩色
                screenshot_for_match = screenshot
            else:  # 截图是灰度，需要转换为彩色
                screenshot_for_match = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR)
            
            # 彩色匹配
            res = cv2.matchTemplate(screenshot_for_match, template, cv2.TM_CCOEFF_NORMED)
            match_type = "彩色"
        else:
            # 灰度匹配
            if len(screenshot.shape) == 3:  # 截图是彩色，转换为灰度
                screenshot_for_match = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:  # 截图已经是灰度
                screenshot_for_match = screenshot
            
            # 灰度匹配
            res = cv2.matchTemplate(screenshot_for_match, template, cv2.TM_CCOEFF_NORMED)
            match_type = "灰度"
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        # 打印匹配信息
        print(f"[match_and_click_template] {match_type}匹配度: {max_val:.2f} (阈值: {threshold})")
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            x, y = max_loc
            
            if region:
                region_x, region_y, region_w, region_h = region
                center_x = region_x + x + w // 2
                center_y = region_y + y + h // 2
                
                if not (region_x <= center_x <= region_x + region_w and 
                        region_y <= center_y <= region_y + region_h):
                    print(f"[match_and_click_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"[match_and_click_template] 匹配成功，点击坐标: ({center_x}, {center_y})")
            # 判断当前窗口是否是置顶窗口
            is_top_window = win32gui.GetForegroundWindow() == hwnd
            if not is_top_window:
                # 如果当前窗口不是置顶窗口，则将窗口置顶
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    print(f"[match_and_click_template] 已将窗口置顶")
                    time.sleep(0.2)
                except Exception as e:
                    print(f"[match_and_click_template] 置顶窗口失败: {str(e)}，但继续执行点击")
            # 使用模拟点击而不是真实鼠标点击
            if hwnd:
                click_at_window_coord(hwnd, center_x, center_y)
            else:
                print("[match_and_click_template] 警告: 没有窗口句柄，无法模拟点击")
            
            return True, (center_x, center_y)
        else:
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(region, template_path, threshold, hwnd):
    """在指定区域查找并点击模板"""
    try:
        # 获取当前屏幕截图
        screenshot = pyautogui.screenshot(region=region)
        
        # 根据模板类型决定截图处理方式
        if template_path in color_templates:
            # 彩色模板，截图转换为BGR格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            print(f"[find_and_click_template] 使用彩色匹配查找: {template_path}")
        else:
            # 灰度模板，截图转换为灰度
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            print(f"[find_and_click_template] 使用灰度匹配查找: {template_path}")
        
        # 进行模板匹配并点击
        matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region, hwnd)
        
        return matched
    except Exception as e:
        print(f"[find_and_click_template] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
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
    # 尹天奇 长寿村
    """主循环函数"""
    window_title = "Phone-S25QBDPT22ATF" 
    template_path = "444.png"
    template_path2 = "buy.png"
    goodsbj = "t4.png"
    template_path4 = "btn3.png"
    template_path5 = "close.png"
    sj = "sj.png"
    close2 = "close2.png"
    
    threshold = 0.2
    index = 0
    print(f"[主循环] 正在监听窗口: {window_title}")

    while not stop_event.is_set():
        if running:
            hwnd = find_window_by_title(window_title)
            if hwnd:
                print(f"[主循环] 找到窗口句柄: {hwnd}")
                
                # 获取窗口区域
                region = get_window_position(hwnd)
                print(f"[主循环] 窗口区域: {region}")
                
                # # 检查窗口是否最小化
                # if win32gui.IsIconic(hwnd):
                #     win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                #     time.sleep(0.02)
                
                # # 激活窗口
                # try:
                #     win32gui.SetForegroundWindow(hwnd)
                # except:
                #     pass
                
                if index == 0:
                    time.sleep(0.05)
                    click_top_center(hwnd)
                    index = 1
                
                # 查找道人
                if not stop_event.is_set() and running:
                    max_attempts = 999999
                    for attempt in range(max_attempts):
                        if stop_event.is_set() or not running:
                            break
                        success1 = find_and_click_template(region, template_path, 0.55, hwnd)
                        if success1:
                            print("[主循环] 点击道人")
                            time.sleep(0.05)
                            # 查找购买按钮 - 在找到道人后查找购买按钮
                            found_buy_button = False
                            max_buy_attempts = 12
                            for buy_attempt in range(max_buy_attempts):
                                if stop_event.is_set() or not running:
                                    break
                                success2 = find_and_click_template(region, template_path2, 0.5, hwnd)
                                if success2:
                                    print("[主循环] 点击购买按钮")
                                    found_buy_button = True
                                    time.sleep(0.05)
                                    break
                                else:
                                    if buy_attempt == max_buy_attempts - 1:
                                        print(f"[主循环] 未找到购买按钮，第{buy_attempt+1}次尝试，重新查找道人")
                                    time.sleep(0.05)
                                        # 如果找到了购买按钮，跳出道人查找循环，继续后续流程
                            if found_buy_button:
                                break
                            else:
                                # 如果没有找到购买按钮，继续下一次道人查找循环
                                print("[主循环] 未找到购买按钮，重新查找道人")
                                continue
                        else:
                            if attempt == max_attempts - 1:
                                print(f"[主循环] 未找到道人，第{attempt+1}次尝试")
                            time.sleep(0.05)
                
                # # 查找购买按钮
                # if not stop_event.is_set() and running:
                #     max_attempts = 12
                #     for attempt in range(max_attempts):
                #         if stop_event.is_set() or not running:
                #             break
                #         success2 = find_and_click_template(region, template_path2, 0.8, hwnd)
                #         if success2:
                #             print("[主循环] 点击购买按钮")
                #             time.sleep(0.15)
                #             break
                #         else:
                #             if attempt == max_attempts - 1:
                #                 print(f"[主循环] 未找到购买按钮，第{attempt+1}次尝试")
                #             time.sleep(0.05)
                
                # 查找商品背景
                if not stop_event.is_set() and running:
                    max_attempts = 12
                    for attempt in range(max_attempts):
                        if stop_event.is_set() or not running:
                            break
                        successbj = find_and_click_template(region, goodsbj, 0.6, hwnd)
                        if successbj:
                            print("[主循环] 找到商品背景")
                            time.sleep(0.15)
                            break
                        else:
                            if attempt == max_attempts - 1:
                                print(f"[主循环] 未找到商品背景，第{attempt+1}次尝试")
                            time.sleep(0.05)
                
                # 查找商品 - 使用彩色匹配和正确的阈值
                found_product = False
                if not stop_event.is_set() and running:
                    max_attempts = 12
                    for attempt in range(max_attempts):
                        if stop_event.is_set() or not running:
                            break
                        success3 = find_and_click_template(region, sj, 0.6, hwnd)  # 使用0.8阈值
                        if success3:
                            print("[主循环] 点击商品")
                            found_product = True
                            time.sleep(0.15)
                            break
                        else:
                            # 如果最终没有找到商品，点击关闭按钮并重新开始整个流程
                            find_and_click_template(region, template_path5, 0.6, hwnd)
                            time.sleep(0.5)
                            # 跳出当前循环，重新开始主循环（从查找道人开始）
                            print('跳出当前循环，重新开始主循环（从查找道人开始）')
                            break

                
                # 如果找到了商品，继续执行确认和重复购买流程
                if found_product and not stop_event.is_set() and running:
                    # 查找确认按钮
                    max_attempts = 12
                    for attempt in range(max_attempts):
                        if stop_event.is_set() or not running:
                            break
                        success4 = find_and_click_template(region, template_path4, 0.6, hwnd)
                        if success4:
                            print("[主循环] 完成第四个操作")
                            time.sleep(0.15)
                            break
                        else:
                            if attempt == max_attempts - 1:
                                print(f"[主循环] 未找到第四个按钮，第{attempt+1}次尝试")
                            time.sleep(0.05)
                    
                    # 重复执行点击商品和确认按钮
                    print("[主循环] 开始重复执行点击商品和点击确认按钮...")
                    
                    repeat_count = 0
                    max_repeats = 120
                    
                    while not stop_event.is_set() and running and repeat_count < max_repeats:
                        repeat_count += 1
                        
                        # 点击关闭按钮
                        find_and_click_template(region, close2, 0.8, hwnd)
                        
                        # 点击商品 - 使用彩色匹配和正确的阈值
                        if find_and_click_template(region, sj, 0.8, hwnd):
                            print(f"[主循环] 第{repeat_count}次重复点击商品成功")
                            time.sleep(0.05)
                            
                            # 点击确认按钮
                            if find_and_click_template(region, template_path4, 0.8, hwnd):
                                print(f"[主循环] 第{repeat_count}次重复点击确认按钮成功")
                                time.sleep(0.05)
                            else:
                                print(f"[主循环] 第{repeat_count}次重复点击确认按钮失败")
                                time.sleep(0.02)
                        else:
                            print(f"[主循环] 第{repeat_count}次重复点击商品失败")
                            time.sleep(0.02)
                
                print("[主循环] 等待下一次扫描...")
            else:
                print("[主循环] 未找到窗口")
            
            # 主循环间隔
            time.sleep(0.03)
        else:
            # 脚本停止状态
            time.sleep(0.03)

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