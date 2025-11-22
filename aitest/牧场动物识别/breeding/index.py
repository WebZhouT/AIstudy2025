import cv2
import numpy as np
import pyautogui
import time
import os
import datetime
import datetime
from PIL import ImageGrab
from image_utils import find_image_position
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 导入自定义的图像工具模块
from image_utils import find_and_click_image, click_at_window_coord, mark_and_save_screenshot


from .One_carry_animals_out import carry_animals_out
from .Two_visit_neighbor import visit_neighbor,visit_neighbor_no_breed
from .Three_release_and_breed_animals import release_and_breed_animals
from .Four_release_and_breed_animals import return_home_and_release
# 动物携带拜访繁殖
def animal_breeding():
    # 默认先去拜访邻居然后回家
    visit_neighbor_no_breed(0)
    print('动物携带拜访繁殖')
    # 1. 携带出游
    carry_animals_out()
    
    # 2. 点击管理员拜访邻居
    visit_neighbor()
    
    # 3. 放出动物繁殖回收
    release_and_breed_animals()
    
    # 4. 点击管理员回家放出
    return_home_and_release()
    # 第二次拜访邻居
    visit_neighbor_no_breed(1)



