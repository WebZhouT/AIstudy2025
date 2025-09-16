# 图像识别
from rapidocr_onnxruntime import RapidOCR
import ctypes  # 用于系统弹窗
from win10toast import ToastNotifier
# 初始化通知器 (放在全局变量处)
toaster = ToastNotifier()
import keyboard
import threading
import pyautogui
import time
import win32gui

# 全部操作完毕后出现提示信息
def show_alert(message, use_toast=True):
    """显示提醒（可选择Toast或传统弹窗）"""
    if use_toast:
        toaster.show_toast(
            "提醒",
            message,
            duration=5,
            threaded=True
        )
    else:
        ctypes.windll.user32.MessageBoxW(0, message, "提醒", 1)

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

# 点击藏宝图
def click_treasure_maps(locations, x, y, width, height):
    """根据坐标数组依次点击藏宝图"""
    # 这里可以根据需要扩展点击逻辑
    print(f"找到{len(locations)}个藏宝图位置")
    for loc in locations:
        if not running:  # 检查是否已停止
            break
        pyautogui.click(loc.left + loc.width//2, loc.top + loc.height//2)
        time.sleep(0.5)

# 新增: 通用图片匹配和点击函数
def find_and_click_image(image_path, confidence=0.8, region=None, click=True):
    """
    通用的图片匹配和点击函数
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    click: 是否点击匹配位置
    
    返回:
    匹配位置或None
    """
    try:
        if region:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
        else:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
        if location and click:
            pyautogui.click(location.left + location.width//2, location.top + location.height//2)
            time.sleep(0.5)  # 添加点击后的延迟
            
        return location
    except pyautogui.ImageNotFoundException:
        return None

# 新增: 查找所有匹配图片的位置
def find_all_images(image_path, confidence=0.8, region=None):
    """
    查找所有匹配的图片位置
    
    参数:
    image_path: 图片路径
    confidence: 匹配相似度
    region: 匹配区域 (left, top, width, height)
    
    返回:
    匹配位置列表
    """
    try:
        if region:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence, region=region))
        else:
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence))
        return locations
    except pyautogui.ImageNotFoundException:
        return []  # 返回空列表而不是抛出异常

# 全局变量控制运行状态
running = False
stop_event = threading.Event()

# 藏宝图
img_content = "treasure_map.png"
# 左侧仓库区域
img_left = "left_warehouse.png"
# 右侧道具/行囊区域
img_right = "right_prop.png"
# 底部切换仓库按钮
footer_btn = "footerbtn.png"
# 目标仓库
target_warehouse = "target_warehouse.png"
# 道具栏和行囊栏的物品都需要匹配藏宝图存入到仓库中
# 道具栏按钮
prop = "prop.png"
# 行囊栏按钮
bag = "bag.png"
# 选中的目标藏宝图
bag_item = "bag_item.png"
# 存入仓库按钮
save_bag = "save_bag.png"
# 藏宝图结果
map_result = "map_result.png"
# 地图区域
area = [
    {
      'name':"傲来国",
      'png':"./areabtn/1.png"
    },    
    
    {
      'name':"东海湾",
      'png':"./areabtn/2.png"
    },{
      'name':"江南野外",
      'png':"./areabtn/3.png"
    },
    {
      'name':"帅驼岭",
      'png':"./areabtn/4.png"
    },
    {
      'name':"狮驼岭",
      'png':"./areabtn/4.png"
    },
    {
      'name':"朱紫国",
      'png':"./areabtn/5.png"
    },
    {
      'name':"北俱芦洲",
      'png':"./areabtn/6.png"
    },
    {
      'name':"花果山",
      'png':"./areabtn/7.png"
    },
    {
      'name':"长寿郊外",
      'png':"./areabtn/8.png"
    },
    {
      'name':"大唐国境",
      'png':"./areabtn/9.png"
    },
    {
      'name':"五庄观",
      'png':"./areabtn/10.png"
    },
    {
      'name':"大唐境外",
      'png':"./areabtn/11.png"
    },
    {
      'name':"麒麟山",
      'png':"./areabtn/12.png"
    },
    {
      'name':"建邺城",
      'png':"./areabtn/13.png"
    },    {
      'name':"建邮城",
      'png':"./areabtn/13.png"
    },
    {
      'name':"墨家村",
      'png':"./areabtn/14.png"
    },
    {
      'name':"女儿村",
      'png':"./areabtn/15.png"
    },
    {
      'name':"普陀山",
      'png':"./areabtn/16.png"
    }
]
# 新增: 从OCR结果中提取地图区域信息
def extract_coordinates(ocr_text):
    """
    从OCR识别结果中提取地图区域信息
    
    参数:
    ocr_text: OCR识别的文字内容
    
    返回:
    地图区域名称或None
    """
    # 遍历地图区域列表，检查OCR结果中是否包含对应地名
    for area_item in area:
        if area_item['name'] in ocr_text:
            return area_item['name']
    
    return None

# 新增: OCR识别函数
def ocr_image_recognition(region=None):
    """
    对指定区域进行OCR文字识别
    
    参数:
    region: 识别区域 (left, top, width, height)
    
    返回:
    识别到的文字内容
    """
    try:
        # 初始化OCR
        ocr = RapidOCR()
        
        # 截取指定区域或全屏
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
            
        # 保存临时截图用于OCR识别
        temp_image = "temp_ocr_image.png"
        screenshot.save(temp_image)
        
        # 进行OCR识别
        result, _ = ocr(temp_image)
        
        # 提取识别到的文字
        if result:
            recognized_text = '\n'.join([item[1] for item in result])
            print(f"OCR识别结果:\n{recognized_text}")
            
            # 新增: 提取地图区域信息
            matched_area = extract_coordinates(recognized_text)
            if matched_area:
                print(f"匹配到地图区域1: {matched_area}")
            else:
                print("未匹配到任何地图区域")
                
            return recognized_text
        else:
            print("未识别到任何文字")
            return ""
    except Exception as e:
        print(f"OCR识别出错: {e}")
        return ""

# 主函数包含所有程序逻辑
def main_loop():
    error_count = 0  # 添加错误计数器
    max_errors = 10  # 最大连续错误次数
    # 定义图片内容
    global running, current_character_index  # 声明所有需要的全局变量
    window_title = "Phone-E6EDU20429087631" 
    while not stop_event.is_set():
        if running:
            # 根据右侧道具/行囊区域的图片，匹配到窗口内的区域获取到对应的匹配区域
            # 这里假设已经获取到窗口句柄hwnd和位置信息
            try:
                print(f"[主循环] 正在监听窗口: {window_title}")
                # 查找游戏窗口
                hwnd = find_window_by_title(window_title)  # 需要替换为实际的游戏窗口标题
                if not hwnd:
                    print("未找到游戏窗口")
                    error_count += 1
                    if error_count >= max_errors:
                        print("连续未找到游戏窗口次数过多，脚本将停止")
                        show_alert("未找到游戏窗口，脚本已停止")
                        stop_script()
                    time.sleep(1)
                    continue
                else:
                    error_count = 0  # 重置错误计数
                    
                x, y, width, height = get_window_position(hwnd)
                
                # 截取右侧道具/行囊区域
                right_region = pyautogui.screenshot(region=(x + width//2, y, width//2, height - 50))  # 假设右半部分为道具/行囊区域
                right_region.save(img_right)
                
                # 匹配道具栏
                prop_location = find_and_click_image(prop, confidence=0.8)
                treasure_found = False
                
                if prop_location:
                    # 检查道具栏是否存在藏宝图，限定在右侧区域
                    try:
                        treasure_in_prop = find_and_click_image(
                            img_content, 
                            confidence=0.8, 
                            region=(x + width//2, y, width//2, height - 50),
                            click=False
                        )
                    except pyautogui.ImageNotFoundException:
                        treasure_in_prop = None
                        
                    if treasure_in_prop:
                        # 道具栏存在藏宝图，返回所有可点击的藏宝图对象，限定在右侧区域
                        try:
                            treasure_locations = find_all_images(img_content, confidence=0.8, region=(x + width//2, y, width//2, height - 50))
                        except pyautogui.ImageNotFoundException:
                            treasure_locations = []
                        print(f"在道具栏找到{len(treasure_locations)}个藏宝图")
                        # 点击第一个藏宝图后停止循环操作
                        if treasure_locations and running:
                            # 只点击第一个找到的藏宝图
                            first_treasure = treasure_locations[0]
                            pyautogui.click(first_treasure.left + first_treasure.width//2, first_treasure.top + first_treasure.height//2)
                            print("已点击第一个藏宝图，停止继续查找")
                            time.sleep(1)
                            treasure_found = True
                            # 点击藏宝图后进行OCR识别
                            print("正在进行藏宝图结果OCR识别...")
                            # 修改: 先匹配藏宝图结果区域，再进行OCR识别
                            try:
                                result_location = pyautogui.locateOnScreen(map_result, confidence=0.4, region=(x, y, width, height))
                            except pyautogui.ImageNotFoundException:
                                result_location = None
                            if result_location:
                                # 基于找到的结果区域进行OCR识别
                                recognized_text = ocr_image_recognition(region=(
                                    int(result_location.left), 
                                    int(result_location.top), 
                                    int(result_location.width), 
                                    int(result_location.height)
                                ))
                                # 提取匹配到的地图区域名称并打印
                                matched_area = extract_coordinates(recognized_text)
                                if matched_area:
                                  print(f'匹配到地图区域2: {matched_area}')
                                  # 点击切换仓库按钮
                                  find_and_click_image(footer_btn, confidence=0.8)
                                  time.sleep(1)
                                  # 匹配当前窗口中刚才匹配的matched_area文字所在位置并进行点击
                                  # 使用OCR查找matched_area在屏幕上的具体位置并点击
                                  try:
                                      # 查找对应的区域图片并点击
                                      for area_item in area:
                                          if area_item['name'] == matched_area:
                                              # 切换仓库进行点击
                                              find_and_click_image(area_item['png'], confidence=0.9)
                                              time.sleep(1)
                                              # 仓库切换完毕后，对选中的地图目标点击2次会从当前的道具/行囊内存储到仓库
                                              find_and_click_image(bag_item, confidence=0.8)
                                              time.sleep(1)
                                              # 点击存入仓库
                                              find_and_click_image(save_bag, confidence=0.9)
                                              break
                                  except Exception as e:
                                      print(f"查找并点击匹配区域时出错: {e}")
                            else:
                                print("未找到藏宝图结果区域")
                                recognized_text = ""
                            # 点击藏宝图后停止脚本
                            print("已找到并点击藏宝图，脚本已停止2")
                            # stop_script()
                            continue
                            # break  # 跳出当前循环
                            
                # 如果道具栏没有找到藏宝图，则检查行囊栏
                if not treasure_found:
                    try:
                        bag_location = find_and_click_image(bag, confidence=0.8)
                    except pyautogui.ImageNotFoundException:
                        bag_location = None
                    if bag_location:
                        # 点击行囊栏
                        pyautogui.click(bag_location.left + bag_location.width//2, bag_location.top + bag_location.height//2)
                        time.sleep(1)  # 等待界面更新
                        
                        # 检查行囊栏是否存在藏宝图，限定在右侧区域
                        try:
                            treasure_locations = find_all_images(img_content, confidence=0.8, region=(x + width//2, y, width//2, height - 50))
                        except pyautogui.ImageNotFoundException:
                            treasure_locations = []
                            
                        if treasure_locations:
                            print(f"在行囊栏找到{len(treasure_locations)}个藏宝图")
                            # 点击第一个藏宝图后停止循环操作
                            if treasure_locations and running:
                                # 只点击第一个找到的藏宝图
                                first_treasure = treasure_locations[0]
                                pyautogui.click(first_treasure.left + first_treasure.width//2, first_treasure.top + first_treasure.height//2)
                                print("已点击第一个藏宝图，停止继续查找")
                                time.sleep(1)
                                treasure_found = True
                                # 点击藏宝图后进行OCR识别
                                print("正在进行藏宝图结果OCR识别...")
                                # 修改: 先匹配藏宝图结果区域，再进行OCR识别
                                try:
                                    result_location = pyautogui.locateOnScreen(map_result, confidence=0.4, region=(x, y, width, height))
                                except pyautogui.ImageNotFoundException:
                                    result_location = None
                                if result_location:
                                    # 基于找到的结果区域进行OCR识别
                                    recognized_text = ocr_image_recognition(region=(
                                        int(result_location.left), 
                                        int(result_location.top), 
                                        int(result_location.width), 
                                        int(result_location.height)
                                    ))
                                    # 提取匹配到的地图区域名称并打印
                                    matched_area = extract_coordinates(recognized_text)
                                    if matched_area:
                                      print(f'匹配到地图区域2: {matched_area}')
                                      # 点击切换仓库按钮
                                      find_and_click_image(footer_btn, confidence=0.8)
                                      time.sleep(1)
                                      # 匹配当前窗口中刚才匹配的matched_area文字所在位置并进行点击
                                      # 使用OCR查找matched_area在屏幕上的具体位置并点击
                                      try:
                                          # 查找对应的区域图片并点击
                                          for area_item in area:
                                              if area_item['name'] == matched_area:
                                                  # 切换仓库进行点击
                                                  find_and_click_image(area_item['png'], confidence=0.8)
                                                  time.sleep(1)
                                                  # 仓库切换完毕后，对选中的地图目标点击2次会从当前的道具/行囊内存储到仓库
                                                  find_and_click_image(bag_item, confidence=0.8)
                                                  # 点击存入仓库
                                                  find_and_click_image(save_bag, confidence=0.6)
                                                  break
                                      except Exception as e:
                                          print(f"查找并点击匹配区域时出错: {e}")
                                else:
                                    print("未找到藏宝图结果区域")
                                    recognized_text = ""
                                # 点击藏宝图后停止脚本
                                print("已找到并点击藏宝图，脚本已停止")
                                # stop_script()
                                continue
                                # break  # 跳出当前循环
                                
                # 如果都没有找到藏宝图，则提示并停止脚本
                if not treasure_found:
                    show_alert("整理已经结束，未找到更多藏宝图")
                    stop_script()
                        
            except Exception as e:
                error_count += 1
                # 修改: 打印详细的异常信息
                print(f"发生错误: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()  # 打印完整的错误堆栈信息
                if error_count >= max_errors:
                    print("连续错误次数过多，脚本将停止")
                    show_alert("程序出现连续错误，脚本已停止")
                    stop_script()
                    break  # 修改: 确保在停止脚本后退出循环
                time.sleep(1)
                continue
        time.sleep(0.1)  # 避免CPU占用过高

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
    except Exception as e:  # 添加: 捕获主循环外的异常
        print(f"\n程序发生未处理的异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_event.set()
        keyboard.unhook_all()

if __name__ == "__main__":
    main()