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

def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    pyautogui.moveTo(click_x, click_y, duration=0.3)
    pyautogui.click(click_x, click_y)
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y})")
    time.sleep(0.5)

def match_and_click_template(screenshot, template_path, threshold, region=None):
    """
    匹配模板并执行点击操作
    """
    try:
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_and_click_template] 警告: 无法读取模板图片 {template_path}")
            return False, None
            
        # 彩色匹配
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        print(f"[match_and_click_template] 当前匹配度: {max_val:.2f} (阈值: {threshold})")
        
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
                    print(f"[match_and_click_template] 警告: 计算坐标({center_x},{center_y})超出区域{region}")
            else:
                # 如果没有提供区域，则直接使用匹配位置
                center_x = x + w // 2
                center_y = y + h // 2
            
            print(f"[match_and_click_template] 匹配成功，点击坐标: ({center_x}, {center_y})")
            
            # 保存匹配结果的调试图像
            # debug_img = screenshot.copy()
            # cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # timestamp = time.strftime("%Y%m%d_%H%M%S")
            # cv2.imwrite(f"debug_match_{timestamp}.png", debug_img)
            
            # 实际执行鼠标移动和点击操作 - 物理移动方式
            current_x, current_y = pyautogui.position()
            distance = ((center_x - current_x)**2 + (center_y - current_y)**2)**0.5
            
            # 根据距离动态调整移动时间
            move_duration = min(0.5, max(0.1, distance / 1000))  # 移动时间在0.1-0.5秒之间
            
            # 物理移动鼠标
            pyautogui.moveTo(center_x, center_y, duration=move_duration, tween=pyautogui.easeInOutQuad)
            time.sleep(2)
            
            # 物理点击
            pyautogui.click()
            time.sleep(0.05)
            
            print(f"[match_and_click_template] 已物理点击坐标: ({center_x}, {center_y})")
            time.sleep(0.5)
            
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(region, template_path, threshold):
    """在指定区域查找并点击模板"""
    try:
        # 获取当前屏幕彩色截图
        print(f"[find_and_click_template] 截图区域: {region}")
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配并点击
        matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region)
        
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
    """主循环函数"""
    # window_title = "ZT 周挺的Redmi Note 11 5G"
    window_title = "Phone-E6EDU20429087631" 
    # window_title = "内测版-Redmi(游戏模式)"
    # template_path = "people.png"  # 替换为你的模板图片路径
    # template_path2 = "btn1.png"  # 替换为你的模板图片路径
    # template_path3 = "btn2.png"  # 替换为你的模板图片路径
    # template_path4 = "btn3.png"  # 替换为你的模板图片路径
    # template_path5 = "close.png"  # 新增关闭按钮模板路径
    template_path = "t1.png"  # 替换为你的模板图片路径
    template_path2 = "t2.png"  # 替换为你的模板图片路径
    template_path3 = "t3.png"  # 替换为你的模板图片路径
    goodsbj = "t4.png"  # 替换为你的模板图片路径
    template_path4 = "btn3.png"  # 替换为你的模板图片路径
    template_path5 = "close.png"  # 新增关闭按钮模板路径
    sj = "sj.png"  # 新增关闭按钮模板路径
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
                    time.sleep(0.1)
                
                # 激活窗口
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass
                if index == 0:
                    time.sleep(0.2)
                    # 点击窗口顶部激活窗口
                    click_top_center(hwnd)
                    index = 1
                else:
                    pass

                
                # 在窗口区域内查找并点击模板 - 改为流式写法并循环匹配直到找到
                print("[主循环] 开始查找模板...")
                
                # 循环查找第一个模板直到找到为止
                while not stop_event.is_set() and running:
                    success = find_and_click_template(region, template_path, threshold)
                    if success:
                        print("[主循环] 成功找到目标NPC并点击了模板")
                        break
                    else:
                        print("[主循环] 未找到模板，1秒后继续查找...")
                        time.sleep(0.2)
                
                # 如果脚本仍在运行，继续查找第二个对话模板
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success2 = find_and_click_template(region, template_path2, 0.8)
                        if success2:
                            print("[主循环] 点击购买按钮")
                            break
                        else:
                            print("[主循环] 未找到购买按钮，1秒后继续查找...")
                            time.sleep(0.2)
                            break
                # 如果脚本仍在运行，继续查找第三个对话模板
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success3 = find_and_click_template(region, template_path3, 0.8)
                        if success3:
                            print("[主循环] 点击购买按钮")
                            break
                        else:
                            print("[主循环] 未找到购买按钮，1秒后继续查找...")
                            # 未找到购买按钮点击关闭按钮重新找购买按钮
                            find_and_click_template(region, close2, 0.8)
                            time.sleep(1)
                            break
                # 如果脚本仍在运行，继续查找第四个商品背景图片是否存在
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        successbj = find_and_click_template(region, goodsbj, 0.8)
                        if successbj:
                            print("[主循环] ")
                            break
                        else:
                            print("[主循环] 未找到购买按钮，1秒后继续查找...")
                            # 这里是未找到就一直等待直到出现为止
                            # 未找到购买按钮点击关闭按钮重新找购买按钮
                            # find_and_click_template(region, close2, 0.8)
                            time.sleep(1)
                            break
                # 如果脚本仍在运行，继续查找第三个模板
                if not stop_event.is_set() and running:
                    found_product = False
                    while not stop_event.is_set() and running:
                        success3 = find_and_click_template(region, sj, 0.8)
                        # success3 = find_and_click_template(region, template_path3, 0.8)
                        if success3:
                            print("[主循环] 点击商品")
                            found_product = True
                            break
                        else:
                            print("[主循环] 未找到商品按钮，点击关闭按钮后重新开始...")
                            # 未找到商品，点击template_path5 的关闭按钮后，从点击目标NPC重新开始执行循环
                            find_and_click_template(region, template_path5, 0.8)
                            time.sleep(0.2)
                            # 重置循环，重新开始
                            break
                
                # 如果找到了商品，则继续查找第四个模板
                if found_product and not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success4 = find_and_click_template(region, template_path4, 0.8)
                        if success4:
                            print("[主循环] 完成第四个操作")
                            break
                        else:
                            print("[主循环] 未找到第四个按钮，1秒后继续查找...")
                            time.sleep(0.2)
                
                print("[主循环] 等待下一次扫描...")
            else:
                print("[主循环] 未找到窗口")
            
            # 等待1秒再进行下一次扫描
            for i in range(3, 0, -1):
                if not running or stop_event.is_set():
                    break
                print(f"\r[主循环] 下次扫描倒计时: {i}秒", end="", flush=True)
                time.sleep(0.1)
            print("\r" + " " * 30, end="\r")  # 清除倒计时行
        else:
            # 脚本停止状态，每秒检查一次
            time.sleep(0.1)

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