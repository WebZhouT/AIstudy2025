# index.py - 主程序入口
import keyboard
import threading
import pyautogui
import time
import win32gui
import win32con
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import json
import traceback

# 导入模块
from role_selector import cycle_select_roles, roleList
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
from image_utils import find_and_click_template

# 初始化 OCR 引擎
ocr = RapidOCR()

# 全局变量控制运行状态
running = False
stop_event = threading.Event()

# 当前匹配的角色索引
current_character_index = 0

def click_at_window_coord(hwnd, x, y):
    """在窗口坐标处点击，不移动鼠标"""
    try:
        # 将屏幕坐标转换为窗口客户区坐标
        point = (x, y)
        client_point = win32gui.ScreenToClient(hwnd, point)
        
        # 发送点击消息到窗口
        lParam = (client_point[1] << 16) | (client_point[0] & 0xFFFF)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        print(f"[click_at_window_coord] 点击坐标: ({x}, {y})")
        return True
    except Exception as e:
        print(f"[click_at_window_coord] 点击失败: {str(e)}")
        return False

def run(region):
    """主运行函数"""
    print("[run] 开始执行任务流程")
    
    try:
        # 点击确认按钮
        find_and_click_template(region, "sure.png", 0.7)             
        time.sleep(2)
        
        # 点击公告的关闭按钮
        find_and_click_template(region, "close.png", 0.7)   
        time.sleep(2)
        
        # 点击礼物左侧的公告里面可能有20的精力领取
        find_and_click_template(region, "gonggao.png", 0.7)
        time.sleep(1)
        
        # 如果存在对应的礼物并且成功点击
        gift_found = find_and_click_template(region, "gift.png", 0.7)
        if gift_found:
            time.sleep(1)
            # 点击领取礼物
            find_and_click_template(region, "save.png", 0.7)
            time.sleep(2)
            # 点击关闭按钮
            find_and_click_template(region, "close.png", 0.7)
            
        time.sleep(2)
        
        # 点击礼物按钮出现签到日历
        goods_found = find_and_click_template(region, ["goods.png","goods2.png","goods3.png"], 0.8)
        if goods_found:
            time.sleep(2)
            # 点击关闭提示文案
            find_and_click_template(region, "tip.png", 0.7)
            # 点击签到的图标按钮
            qiandao = find_and_click_template(region, ["aim.png","aim2.png","aim3.png"], 0.7)
            time.sleep(0.5)
            qiandao = find_and_click_template(region, ["aim.png","aim2.png","aim3.png"], 0.7)
            time.sleep(2)
            find_and_click_template(region, "null.png", 0.7)
            time.sleep(1)
            
            if qiandao:
                # 如果签到成功点击关闭按钮
                find_and_click_template(region, "close.png", 0.7)
                time.sleep(2)
                # 如果出现葫芦达到上限
                exitTop = find_and_click_template(region, "discard.png", 0.6)
                time.sleep(2)
                if exitTop:
                    # 点击确认丢弃
                    find_and_click_template(region, "discardsure.png", 0.6)
                    time.sleep(2)
                    # 再次点击关闭按钮
                    find_and_click_template(region, "close.png", 0.7)
                    time.sleep(2)
            else:
                # 点击签到图标
                find_and_click_template(region, "aim.png", 0.7)
                # 如果签到失败，点击关闭按钮
                find_and_click_template(region, "close.png", 0.7)
            time.sleep(2)
            find_and_click_template(region, "close.png", 0.7)
            time.sleep(2)
        else:
            print("[run] 未找到礼物按钮")
            show_alert("未找到礼物按钮，请检查游戏是否正常启动")
            return False
            
        print("[run] 任务流程执行完成")
        return True
        
    except Exception as e:
        print(f"[run] 执行任务时发生错误: {str(e)}")
        traceback.print_exc()
        return False

def main_loop():
    """主循环"""
    global running, current_character_index, window_title
    
    error_count = 0
    max_errors = 5
    
    while not stop_event.is_set():
        if running:
            print(f"[主循环] 正在监听窗口: {window_title}")
            
            # 查找游戏窗口
            hwnd = find_window_by_title(window_title)
            if not hwnd:
                print("[主循环] 未找到游戏窗口")
                error_count += 1
                if error_count >= max_errors:
                    print("[主循环] 连续未找到游戏窗口次数过多，脚本将停止")
                    show_alert("未找到游戏窗口，脚本已停止")
                    stop_script()
                time.sleep(1)
                continue
            else:
                error_count = 0  # 重置错误计数
                
                # 获取窗口区域
                region = get_window_position(hwnd)
                print(f"[主循环] 窗口区域: {region}")
                
                time.sleep(1)
                
                # 选择角色
                result = cycle_select_roles(current_character_index)
                
                # 如果成功找到并点击了角色，则执行任务并更新索引
                if result:
                    print(f"[主循环] 角色选择成功，开始执行任务")
                    time.sleep(2)
                    find_and_click_template(region, "close.png", 0.7)
                    time.sleep(2)
                    # 执行主要任务
                    task_success = run(region)
                    
                    if task_success:
                        current_character_index += 1
                        # 如果已遍历完所有角色，则重置索引为0
                        if current_character_index >= len(roleList):
                            current_character_index = 0
                            print("[主循环] 所有角色已处理完毕，重新开始")
                            show_alert("所有角色任务已完成", use_toast=True)
                            break
                    else:
                        print("[主循环] 任务执行失败，停止脚本")
                        stop_script()
                        break
                else:
                    print("[主循环] 角色选择失败")
                    error_count += 1
                    if error_count >= max_errors:
                        print("[主循环] 连续角色选择失败次数过多，脚本将停止")
                        show_alert("角色选择失败，脚本已停止")
                        stop_script()
                        break
            
            time.sleep(2)  # 主循环间隔

def start_script():
    """启动脚本"""
    global running
    running = True
    stop_event.clear()
    print("\n===== 脚本已启动 =====")

def stop_script():
    """停止脚本"""
    global running
    running = False
    stop_event.set()
    print("\n===== 脚本已停止 =====")

def main():
    """主函数"""
    # 注册热键
    keyboard.add_hotkey('f1', start_script)
    keyboard.add_hotkey('f2', stop_script)
    
    print("提示: 按 F1 启动脚本，按 F2 停止脚本")
    
    try:
        # 启动主循环线程
        main_thread = threading.Thread(target=main_loop)
        main_thread.daemon = True
        main_thread.start()
        
        # 等待主线程结束
        while main_thread.is_alive():
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        stop_script()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()