import cv2
import numpy as np
import pyautogui
import time
import os
import datetime
from PIL import ImageGrab
from image_utils import find_image_position
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot
from role_selector import current_role
# 获得牧场管理员目标匹配方法
from recognize_simple_target import aim,recognize_simple_target
# 鼠标拖拽指定区域识别文字
from drag_scroll import find_drag_area_and_scroll
# 角色拜访配置
role_neighbors_config = {
    '佑手': {
        'neighbors': ['残枫', '妙手', '芊'],  # 拜访的3个用户
        'breed_neighbor_index': 0  # 第一个邻居需要繁殖
    },
    '鱼的仓库2': {
        'neighbors': ['药材料234', '鱼的仓库', '环仓库3'],
        'breed_neighbor_index': 0
    }
    # 可以继续添加其他角色
}
def visit_neighbor():
    """拜访需要繁殖的邻居（第一个邻居）"""
    print('\n=== 点击管理员拜访邻居（需要繁殖）===')
    
    # 获取当前角色的配置
    role_config = role_neighbors_config.get(current_role)
    if not role_config:
        print(f"未找到角色 {current_role} 的配置")
        return
    
    neighbors = role_config['neighbors']
    
    if not neighbors:
        print("未配置拜访邻居")
        return
    
    # 获取需要繁殖的邻居名称（第一个）
    breed_neighbor_name = neighbors[0]  # 第一个邻居需要繁殖
    print(f"角色 {current_role} 需要拜访并繁殖的邻居: {breed_neighbor_name}")
    # 设置最大循环次数防止无限循环
    max_attempts = 12
    attempt_count = 0
    
    while attempt_count < max_attempts:
        attempt_count += 1
        print(f"\n--- 第 {attempt_count} 轮搜索 ---")
        # 找到牧场管理员并进行点击操作
        admin_position = recognize_simple_target(aim)    
        if admin_position:
            print(f"找到管理员，位置: {admin_position}，相似度: {admin_position.get('confidence', 0):.2f}")
            hwnd = find_window_by_title(window_title)
            click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
            time.sleep(1)
            # 点击牧场之友按钮
            find_and_click_image('./breeding_image/friend.png', confidence=0.65)
            time.sleep(1)
            # 无论find_drag_area_and_scroll是否成功，我们都退出循环，因为已经点击了管理员
            # 第一次尝试执行牧场操作
            # 如果找到管理员就跳出外面的循环
            # 点击拜访邻居文字
            leave_coordinates = find_drag_area_and_scroll('./breeding_image/scroll.png',breed_neighbor_name)
            if leave_coordinates:
              x, y = leave_coordinates
              click_at_window_coord(hwnd,x, y)
              time.sleep(1)
              # 点击拜访按钮
              find_and_click_image('./breeding_image/visite.png', confidence=0.65)
              time.sleep(1)
              # 点击关闭按钮
              find_and_click_image('./breeding_image/close.png', confidence=0.65)
              print(f"拜访邻居"+breed_neighbor_name+"成功")
            else:
                print("未找到离开牧场选项")
            break
        else:
            print("未找到管理员")
            show_alert("未找到管理员")
            # 未找到管理员重复循环查找
            print("未找到管理员重复循环查找，拜访邻居")
            time.sleep(1)
        # 执行拜访操作
        # if perform_visit_neighbor(breed_neighbor_name, need_breed=True):
        #     print(f"成功拜访需要繁殖的邻居: {breed_neighbor_name}")
        # else:
        #     print(f"拜访需要繁殖的邻居失败: {breed_neighbor_name}")


def visit_neighbor_no_breed(neighbor_index):
    """
    只拜访不繁殖的邻居
    
    参数:
        neighbor_index: 邻居索引 (1代表第二个，2代表第三个)
    """
    print(f'\n=== 点击管理员拜访邻居（只拜访不繁殖）- 索引 {neighbor_index} ===')
    
    # 获取当前角色的配置
    role_config = role_neighbors_config.get(current_role)
    if not role_config:
        print(f"未找到角色 {current_role} 的配置")
        return
    
    neighbors = role_config['neighbors']
    
    if not neighbors or neighbor_index >= len(neighbors) or neighbor_index < 1:
        print(f"邻居索引 {neighbor_index} 无效")
        return
    
    # 获取只拜访的邻居名称
    visit_only_neighbor_name = neighbors[neighbor_index]
    print(f"角色 {current_role} 只拜访不繁殖的邻居: {visit_only_neighbor_name}")
    
    # 执行拜访操作
    # 点击拜访按钮
    find_and_click_image('./breeding_image/visite.png', confidence=0.65)
    time.sleep(1)
    # 点击关闭按钮
    find_and_click_image('./breeding_image/close.png', confidence=0.65)
    print(f"拜访邻居"+visit_only_neighbor_name+"成功")
    # 找到牧场管理员并进行点击操作
    # 设置最大循环次数防止无限循环
    max_attempts = 12
    attempt_count = 0
    
    while attempt_count < max_attempts:
        attempt_count += 1
        print(f"\n--- 第 {attempt_count} 轮搜索 ---")
        # 找到牧场管理员并进行点击操作
        admin_position = recognize_simple_target(aim)    
        if admin_position:
            print(f"找到管理员，位置: {admin_position}，相似度: {admin_position.get('confidence', 0):.2f}")
            hwnd = find_window_by_title(window_title)
            click_at_window_coord(hwnd,admin_position['x'], admin_position['y'])
            time.sleep(1)
            # 点击送我回去自己的牧场按钮
            find_and_click_image('./breeding_image/friend.png', confidence=0.65)
            time.sleep(1)
            # 无论find_drag_area_and_scroll是否成功，我们都退出循环，因为已经点击了管理员
            # 第一次尝试执行牧场操作
            # 如果找到管理员就跳出外面的循环
            # 点击拜访邻居文字
            leave_coordinates = find_drag_area_and_scroll('./breeding_image/scroll.png','请送我回去')
            if leave_coordinates:
              x, y = leave_coordinates
              click_at_window_coord(hwnd,x, y)
              time.sleep(1)
              print(f"回家成功")
            else:
                print("未找到请送我回去")
            break
        else:
            print("未找到管理员")
            show_alert("未找到管理员")
            # 未找到管理员重复循环查找
            print("未找到管理员重复循环查找，拜访邻居")
            time.sleep(1)
        
    # if perform_visit_neighbor(visit_only_neighbor_name, need_breed=False):
    #     print(f"成功拜访邻居: {visit_only_neighbor_name}")
    # else:
    #     print(f"拜访邻居失败: {visit_only_neighbor_name}")  