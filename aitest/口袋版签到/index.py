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
from role_selector import cycle_select_roles
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title, roleList
from image_utils import find_and_click_template

# 初始化 OCR 引擎
ocr = RapidOCR()

# 全局变量控制运行状态
running = False
stop_event = threading.Event()

# 当前匹配的角色索引
current_character_index = 0

# 配置参数 - 可调整以优化性能
CONFIG = {
    "short_delay": 0.3,      # 短延迟
    "medium_delay": 0.5,     # 中等延迟
    "long_delay": 1.0,       # 长延迟
    "max_attempts": 2,       # 最大尝试次数（整数）
    "max_errors": 3,         # 最大错误次数
    "confidence_threshold": 0.7  # 模板匹配置信度阈值
}

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

def optimized_find_and_click(region, templates, confidence=None, max_attempts=2, grayscale=False):
    """优化的模板查找和点击函数"""
    if confidence is None:
        confidence = CONFIG["confidence_threshold"]
    if max_attempts is None:
        max_attempts = CONFIG["max_attempts"]
    
    return find_and_click_template(region, templates, confidence, max_attempts,grayscale)

def run(region):
    """主运行函数 - 优化版"""
    print("[run] 开始执行任务流程")
    
    try:
        # 快速点击确认按钮和关闭按钮
        optimized_find_and_click(region, "sure.png",confidence=0.6)             
        time.sleep(CONFIG["short_delay"])
        time.sleep(2)
        time.sleep(2)
        optimized_find_and_click(region, "close.png",confidence=0.6)   
        time.sleep(CONFIG["short_delay"])
        time.sleep(2)
        time.sleep(2)
        optimized_find_and_click(region, "close.png",confidence=0.6)   
        time.sleep(CONFIG["short_delay"])
        # 点击公告
        optimized_find_and_click(region, "gonggao.png",confidence=0.6)
        time.sleep(CONFIG["short_delay"])
        
        # 礼物处理流程
        gift_found = optimized_find_and_click(region, "gift.png")
        if gift_found:
            time.sleep(CONFIG["short_delay"])
            optimized_find_and_click(region, "save.png")
            time.sleep(CONFIG["medium_delay"])
            optimized_find_and_click(region, "close.png")
            
        time.sleep(CONFIG["medium_delay"])
        
        # 礼物按钮和签到处理
        goods_found = optimized_find_and_click(region, ["goods.png","goods2.png","goods3.png"])
        if goods_found:
            time.sleep(CONFIG["medium_delay"])
            optimized_find_and_click(region, "tip.png")
            time.sleep(CONFIG["short_delay"])
            # 尝试签到 - 第一次
            qiandao1 = optimized_find_and_click(region, ["aim.png","aim1.png","aim4.png"],confidence=0.5)
            time.sleep(CONFIG["short_delay"])
            
            # 如果第一次没点到，再试一次 - 第二次
            qiandao2 = False
            if not qiandao1:
                qiandao2 = optimized_find_and_click(region, ["aim.png","aim1.png","aim4.png"],confidence=0.5)
                time.sleep(CONFIG["short_delay"])
            
            # 判断最终是否签到成功（只要有一次成功就算成功）
            qiandao = qiandao1 or qiandao2

            time.sleep(2)

            if qiandao:
                # 处理葫芦上限
                exitTop = optimized_find_and_click(region, "discard.png", confidence=0.5)
                exitTop = optimized_find_and_click(region, "discard.png", confidence=0.5)
                time.sleep(CONFIG["medium_delay"])
                optimized_find_and_click(region, "discardsure.png", confidence=0.6)
                time.sleep(CONFIG["medium_delay"])
                optimized_find_and_click(region, "discardsure.png", confidence=0.6)
                time.sleep(CONFIG["medium_delay"])
                optimized_find_and_click(region, "close.png",confidence=0.5)
                time.sleep(CONFIG["medium_delay"])
                # 签到成功处理
                optimized_find_and_click(region, "close.png",confidence=0.5)
                time.sleep(CONFIG["medium_delay"])
            else:
                # 签到失败处理（两次尝试都失败）
                from getWindows import roleList
                import json
                import os
                
                # 获取当前处理的角色名称
                failed_role = roleList[current_character_index] if current_character_index < len(roleList) else "Unknown"
                
                # 创建或追加到失败日志文件
                log_file = "failed_signins.json"
                failed_roles = []
                
                # 如果日志文件存在，读取现有内容
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            failed_roles = json.load(f)
                    except:
                        failed_roles = []
                
                # 添加当前失败的角色到列表
                if failed_role not in failed_roles:
                    failed_roles.append(failed_role)
                
                # 写入更新后的列表到文件
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(failed_roles, f, ensure_ascii=False, indent=2)
                
                print(f"[run] 签到失败（两次尝试均失败），已记录角色 {failed_role} 到 {log_file}")
                
                optimized_find_and_click(region, ["aim.png","aim1.png","aim4.png"],confidence=0.5)
                optimized_find_and_click(region, "close.png",confidence=0.5)
                time.sleep(CONFIG["medium_delay"])
                # # 点击消除提示的弹框，
                # optimized_find_and_click(region, "tip.png",confidence=0.5)
                # time.sleep(CONFIG["medium_delay"])
            # 领取底部进度条的箱子
            optimized_find_and_click(region, "footerbox.png",confidence=0.8,max_attempts = 3,grayscale = True)
            time.sleep(CONFIG["medium_delay"])
            optimized_find_and_click(region, "footerbox.png",confidence=0.8,max_attempts = 3,grayscale = True)
            time.sleep(CONFIG["medium_delay"])
            optimized_find_and_click(region, "null.png")
            time.sleep(CONFIG["short_delay"])
            time.sleep(CONFIG["medium_delay"])
            optimized_find_and_click(region, "close.png")
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
    """主循环 - 优化版"""
    global running, current_character_index, window_title
    
    error_count = 0
    max_errors = CONFIG["max_errors"]
    
    # 缓存窗口句柄和区域，避免重复查找
    cached_hwnd = None
    cached_region = None
    
    while not stop_event.is_set():
        if running:
            print(f"[主循环] 正在监听窗口: {window_title}")
            
            # 查找游戏窗口（使用缓存优化）
            if not cached_hwnd:
                hwnd = find_window_by_title(window_title)
                if hwnd:
                    cached_hwnd = hwnd
                    cached_region = get_window_position(hwnd)
                    print(f"[主循环] 缓存窗口区域: {cached_region}")
            else:
                hwnd = cached_hwnd
                region = cached_region
            
            if not hwnd:
                print("[主循环] 未找到游戏窗口")
                error_count += 1
                if error_count >= max_errors:
                    print("[主循环] 连续未找到游戏窗口次数过多，脚本将停止")
                    show_alert("未找到游戏窗口，脚本已停止")
                    stop_script()
                time.sleep(CONFIG["medium_delay"])
                continue
            else:
                error_count = 0  # 重置错误计数
                
                # 使用缓存的窗口区域
                region = cached_region
                print(f"[主循环] 使用窗口区域: {region}")
                
                time.sleep(CONFIG["short_delay"])
                
                # 选择角色
                result = cycle_select_roles(current_character_index)
                
                # 如果成功找到并点击了角色，则执行任务并更新索引
                if result:
                    print(f"[主循环] 角色选择成功，开始执行任务")
                    time.sleep(CONFIG["medium_delay"])
                    optimized_find_and_click(region, "close.png")
                    time.sleep(CONFIG["medium_delay"])
                    
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
            
            time.sleep(CONFIG["medium_delay"])  # 主循环间隔

def start_script():
    """启动脚本"""
    global running, cached_hwnd, cached_region
    running = True
    stop_event.clear()
    # 清除窗口缓存，确保重新查找最新窗口
    cached_hwnd = None
    cached_region = None
    print("\n===== 脚本已启动 =====")

def stop_script():
    """停止脚本"""
    global running, cached_hwnd, cached_region
    running = False
    stop_event.set()
    # 清除窗口缓存
    cached_hwnd = None
    cached_region = None
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