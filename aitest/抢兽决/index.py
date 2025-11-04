import os
import pyautogui
import time
import win32gui
import win32con
import cv2
import numpy as np
import keyboard
import threading
import ctypes
from ctypes import wintypes
import win32api

# 全局变量控制运行状态
running = False
stop_event = threading.Event()
window_title = "Phone-721QADRSEEMJX" 
# Windows API常量
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_MOUSEMOVE = 0x0200

# Windows API函数声明
user32 = ctypes.windll.user32
SendMessage = user32.SendMessageW
SendMessage.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
SendMessage.restype = ctypes.c_long

def find_window_by_title(title):
    """根据窗口标题查找窗口句柄"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None
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
def get_window_position(hwnd):
    """获取窗口位置和大小"""
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return x, y, width, height

def send_input_click(x, y):
    """使用SendInput API模拟鼠标点击，更接近真实输入"""
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
    
    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("mi", MOUSEINPUT)]
    
    INPUT_MOUSE = 0
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_MOVE = 0x0001
    
    # 转换坐标到绝对坐标系统(0-65535)
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    absolute_x = x * 65535 // screen_width
    absolute_y = y * 65535 // screen_height
    
    # 先移动鼠标到目标位置
    mi_move = MOUSEINPUT(absolute_x, absolute_y, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, 0, None)
    input_move = INPUT(INPUT_MOUSE, mi_move)
    
    # 创建点击输入结构
    mi_down = MOUSEINPUT(absolute_x, absolute_y, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTDOWN, 0, None)
    mi_up = MOUSEINPUT(absolute_x, absolute_y, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTUP, 0, None)
    
    input_down = INPUT(INPUT_MOUSE, mi_down)
    input_up = INPUT(INPUT_MOUSE, mi_up)
    
    # 发送输入
    result1 = ctypes.windll.user32.SendInput(1, ctypes.byref(input_move), ctypes.sizeof(input_move))
    time.sleep(0.05)  # 增加延迟确保移动完成
    result2 = ctypes.windll.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(input_down))
    time.sleep(0.05)
    result3 = ctypes.windll.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(input_up))
    
    print(f"[send_input_click] 鼠标移动结果: {result1}, 按下结果: {result2}, 释放结果: {result3}")
    
    # 如果SendInput失败，尝试使用pyautogui作为备选方案
    if result2 == 0 or result3 == 0:
        print("[send_input_click] SendInput执行失败，尝试使用pyautogui作为备选方案")
        try:
            original_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.1
            hwnd = find_window_by_title(window_title)
            pyautogui.click(x, y)
            click_at_window_coord(hwnd, x, y)
            # 改成模拟点击
            pyautogui.PAUSE = original_pause
            print("[send_input_click] 已使用pyautogui点击")
        except Exception as e:
            print(f"[send_input_click] pyautogui点击也失败: {e}")

def click_top_center(hwnd):
    """点击窗口上方中间位置"""
    # 确保窗口不在最小化状态
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.1)
    
    # 尝试多种方式激活窗口
    activated = False
    
    # 方式1: 直接激活窗口
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        activated = True
        print(f"[click_top_center] 成功通过SetForegroundWindow激活窗口")
    except Exception as e:
        print(f"[click_top_center] SetForegroundWindow激活失败: {e}")
    
    # 方式2: 如果方式1失败，尝试ShowWindow + SetForegroundWindow
    if not activated:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            activated = True
            print(f"[click_top_center] 成功通过ShowWindow+SetForegroundWindow激活窗口")
        except Exception as e:
            print(f"[click_top_center] ShowWindow+SetForegroundWindow激活失败: {e}")
    
    # 方式3: 如果前两种都失败，尝试FlashWindow
    if not activated:
        try:
            win32gui.FlashWindow(hwnd, True)
            time.sleep(0.1)
            print(f"[click_top_center] 已尝试通过FlashWindow提醒用户")
        except Exception as e:
            print(f"[click_top_center] FlashWindow提醒失败: {e}")
    
    x, y, width, height = get_window_position(hwnd)
    click_x = x + width // 2
    click_y = y + 20
    
    print(f"[click_top_center] 窗口位置: ({x}, {y}, {width}, {height})")
    print(f"[click_top_center] 屏幕点击坐标: ({click_x}, {click_y})")
    
    # 转换屏幕坐标为窗口坐标
    try:
        point = win32gui.ScreenToClient(hwnd, (click_x, click_y))
        client_x, client_y = point
        print(f"[click_top_center] 窗口相对坐标: ({client_x}, {client_y})")
    except Exception as e:
        print(f"[click_top_center] 坐标转换失败: {e}")
        # 如果坐标转换失败，使用屏幕坐标直接点击
        client_x, client_y = click_x, click_y
    
    # 发送鼠标移动和点击消息
    try:
        lparam = (client_y << 16) | client_x
        SendMessage(hwnd, WM_MOUSEMOVE, 0, lparam)
        time.sleep(0.05)
        result1 = SendMessage(hwnd, WM_LBUTTONDOWN, 0, lparam)
        time.sleep(0.05)
        result2 = SendMessage(hwnd, WM_LBUTTONUP, 0, lparam)
        
        print(f"[click_top_center] 已发送鼠标点击消息: ({click_x}, {click_y}) 窗口坐标: ({client_x}, {client_y})")
        print(f"[click_top_center] 按下消息返回: {result1}, 弹起消息返回: {result2}")
        
        # 检查SendMessage返回值
        if result1 == 0 and result2 == 0:
            print("[click_top_center] SendMessage可能执行失败，尝试备选方案")
            raise Exception("SendMessage返回值为0")
    except Exception as e:
        print(f"[click_top_center] 发送鼠标消息失败: {e}")
        # 备选方案：使用SendInput
        try:
            send_input_click(click_x, click_y)
            print(f"[click_top_center] 已使用SendInput作为备选方案点击: ({click_x}, {click_y})")
        except Exception as e2:
            print(f"[click_top_center] SendInput备选方案也失败: {e2}")
            # 最后的备选方案：使用pyautogui
            try:
                pyautogui.click(click_x, click_y)
                print(f"[click_top_center] 已使用pyautogui作为最后备选方案点击: ({click_x}, {click_y})")
            except Exception as e3:
                print(f"[click_top_center] 所有点击方案都失败: {e3}")
    
    print(f"[click_top_center] 点击窗口顶部中心: ({click_x}, {click_y}) 窗口坐标: ({client_x}, {client_y})")
    time.sleep(0.1)

def match_and_click_template(screenshot, template_path, threshold, region=None, use_real_mouse=False, use_sendinput=False):
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
            
            if use_real_mouse:
                # 使用真实鼠标点击
                try:
                    original_pause = pyautogui.PAUSE
                    pyautogui.PAUSE = 0.1
                    pyautogui.click(center_x, center_y)
                    pyautogui.PAUSE = original_pause
                    print(f"[match_and_click_template] 已通过真实鼠标点击坐标: ({center_x}, {center_y})")
                except Exception as e:
                    print(f"[match_and_click_template] 真实鼠标点击失败: {e}")
            elif use_sendinput:
                # 使用SendInput模拟鼠标点击
                send_input_click(center_x, center_y)
                print(f"[match_and_click_template] 已通过SendInput点击坐标: ({center_x}, {center_y})")
            else:
                # 使用Windows API发送点击消息
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    # 确保窗口激活
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    
                    try:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"[match_and_click_template] 激活窗口失败: {e}")
                    
                    # 转换屏幕坐标为窗口坐标
                    try:
                        point = win32gui.ScreenToClient(hwnd, (center_x, center_y))
                        client_x, client_y = point
                        
                        # 发送鼠标移动和点击消息
                        lparam = (client_y << 16) | client_x
                        SendMessage(hwnd, WM_MOUSEMOVE, 0, lparam)
                        time.sleep(0.05)
                        result1 = SendMessage(hwnd, WM_LBUTTONDOWN, 0, lparam)
                        time.sleep(0.05)
                        result2 = SendMessage(hwnd, WM_LBUTTONUP, 0, lparam)
                        
                        print(f"[match_and_click_template] 已通过Windows API点击坐标: ({center_x}, {center_y}) 窗口坐标: ({client_x}, {client_y})")
                        print(f"[match_and_click_template] 按下消息返回: {result1}, 弹起消息返回: {result2}")
                        
                        # 检查SendMessage返回值
                        if result1 == 0 and result2 == 0:
                            print("[match_and_click_template] SendMessage可能执行失败，尝试备选方案")
                            raise Exception("SendMessage返回值为0")
                    except Exception as e:
                        print(f"[match_and_click_template] Windows API点击失败: {e}")
                        # 备选方案：使用SendInput
                        try:
                            send_input_click(center_x, center_y)
                            print(f"[match_and_click_template] 已使用SendInput作为备选方案点击: ({center_x}, {center_y})")
                        except Exception as e2:
                            print(f"[match_and_click_template] SendInput备选方案也失败: {e2}")
                            # 最后的备选方案：使用pyautogui
                            try:
                                pyautogui.click(center_x, center_y)
                                print(f"[match_and_click_template] 已使用pyautogui作为最后备选方案点击: ({center_x}, {center_y})")
                            except Exception as e3:
                                print(f"[match_and_click_template] 所有点击方案都失败: {e3}")
                else:
                    print("[match_and_click_template] 错误: 无法找到窗口句柄")
            
            time.sleep(0.1)  # 增加点击后的延迟
            
            return True, (center_x, center_y)
        else:
            print(f"[match_and_click_template] 匹配度不足阈值({threshold:.2f})")
            return False, None
            
    except Exception as e:
        print(f"[match_and_click_template] 匹配过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def find_and_click_template(region, template_path, threshold, use_real_mouse=False, use_sendinput=False):
    """在指定区域查找并点击模板"""
    try:
        # 获取当前屏幕彩色截图
        print(f"[find_and_click_template] 截图区域: {region}")
        screenshot = pyautogui.screenshot(region=region)
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 进行模板匹配并点击
        matched, pos = match_and_click_template(screenshot_cv, template_path, threshold, region, use_real_mouse, use_sendinput)
        
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
                
                # 在窗口区域内查找并点击模板 - 改为流式写法并循环匹配直到找到
                print("[主循环] 开始查找模板...")
                
                # 循环查找第一个模板直到找到为止
                while not stop_event.is_set() and running:
                    success = find_and_click_template(region, template_path, threshold, use_sendinput=True)
                    if success:
                        print("[主循环] 成功找到目标NPC并点击了模板")
                        time.sleep(0.5)  # 增加等待时间确保界面稳定
                        break
                    else:
                        print("[主循环] 未找到模板，1秒后继续查找...")
                        time.sleep(1)  # 增加等待时间
                
                # 如果脚本仍在运行，继续查找第二个对话模板
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success2 = find_and_click_template(region, template_path2, 0.8, use_sendinput=True)
                        if success2:
                            print("[主循环] 点击购买按钮")
                            time.sleep(0.5)  # 增加等待时间确保界面稳定
                            break
                        else:
                            print("[主循环] 未找到丹青之道按钮，1秒后继续查找...")
                            time.sleep(1)  # 增加等待时间
                            break
                
                # 如果脚本仍在运行，继续查找第三个对话模板
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success3 = find_and_click_template(region, template_path3, 0.8, use_sendinput=True)
                        if success3:
                            print("[主循环] 点击购买按钮")
                            time.sleep(0.5)  # 增加等待时间确保界面稳定
                            break
                        else:
                            print("[主循环] 点击购买后继续购买，1秒后继续查找...")
                            # 未找到购买按钮点击关闭按钮重新找购买按钮
                            find_and_click_template(region, close2, 0.8, use_sendinput=True)
                            time.sleep(1)  # 增加等待时间
                            break
                
                # 如果脚本仍在运行，继续查找第四个商品背景图片是否存在
                if not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        successbj = find_and_click_template(region, goodsbj, 0.8, use_sendinput=True)
                        if successbj:
                            print("[主循环] 找到商品背景")
                            time.sleep(0.5)  # 增加等待时间确保界面稳定
                            break
                        else:
                            print("[主循环] 未找到商品背景，1秒后继续查找...从头开始")
                            time.sleep(1)  # 增加等待时间
                            break
                
                # 如果脚本仍在运行，继续查找商品
                if not stop_event.is_set() and running:
                    found_product = False
                    while not stop_event.is_set() and running:
                        success3 = find_and_click_template(region, sj, 0.8, use_sendinput=True)
                        if success3:
                            print("[主循环] 点击商品")
                            found_product = True
                            time.sleep(0.5)  # 增加等待时间确保界面稳定
                            break
                        else:
                            print("[主循环] 未找到商品目标，点击关闭按钮后重新开始...")
                            # 未找到商品，点击关闭按钮后重新开始
                            find_and_click_template(region, template_path5, 0.4, use_sendinput=True)
                            time.sleep(0.2)  # 增加等待时间
                            # 重置循环，重新开始
                            break
                
                # 如果找到了商品，则继续查找确认按钮
                if found_product and not stop_event.is_set() and running:
                    while not stop_event.is_set() and running:
                        success4 = find_and_click_template(region, template_path4, 0.8, use_sendinput=True)
                        if success4:
                            print("[主循环] 完成第四个操作")
                            time.sleep(0.5)  # 增加等待时间确保界面稳定
                            break
                        else:
                            print("[主循环] 未找到第四个按钮，1秒后继续查找...")
                            time.sleep(1)  # 增加等待时间
                
                # 新增：如果已完成前面所有步骤，则重复执行点击商品和点击确认按钮
                if found_product and not stop_event.is_set() and running:
                    print("[主循环] 开始重复执行点击商品和点击确认按钮...")
                    
                    while not stop_event.is_set() and running:
                        find_and_click_template(region, close2, 0.8, use_sendinput=True)
                        # 点击商品
                        if find_and_click_template(region, sj, 0.8, use_sendinput=True):
                            print("[主循环] 重复点击商品成功")
                            time.sleep(0.5)
                            
                            # 点击确认按钮
                            if find_and_click_template(region, template_path4, 0.8, use_sendinput=True):
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
            
            time.sleep(0.1)  # 增加每次等待时间
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