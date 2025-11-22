import cv2
from PIL import ImageGrab
import numpy as np
# 获取窗口句柄位置、信息以及提示工具函数
from getWindows import find_window_by_title, get_window_position, show_alert, focus_window, window_title
# 管理员识别配置
aim = [
    "管理员", 
    ["./image/admin.png", "./image/admin2.png", "./image/admin3.png", "./image/admin4.png"], 
    0.6,  # 相似度阈值
    (0, 145, 0)  # 标记框颜色
]
def recognize_simple_target(target_config):
    """
    简化版目标识别 - 适用于单个目标识别
    target_config: [目标名称, 图片路径列表, 相似度阈值, 标记颜色]
    """
    name, image_paths, confidence_threshold, color = target_config
    
    # 捕获屏幕
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        return None 
    
    # 获取窗口区域
    x, y, width, height = get_window_position(hwnd)
    region = (x, y, x + width, y + height)
    
    # 截取窗口区域
    screenshot = ImageGrab.grab(bbox=region)
    screen_image = np.array(screenshot)
    screen_image = cv2.cvtColor(screen_image, cv2.COLOR_RGB2BGR)
    gray_screen = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
    
    # 遍历所有模板图片进行匹配
    for image_path in image_paths:
        template = cv2.imread(image_path, 0)
        if template is None:
            continue
            
        # 模板匹配
        result = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence_threshold)
        
        # 处理匹配结果
        for pt in zip(*locations[::-1]):
            center_x = x + pt[0] + template.shape[1] // 2
            center_y = y + pt[1] + template.shape[0] // 2
            
            # 标记并保存截图
            marked_image = screen_image.copy()
            top_left = (pt[0], pt[1])
            bottom_right = (pt[0] + template.shape[1], pt[1] + template.shape[0])
            cv2.rectangle(marked_image, top_left, bottom_right, color, 2)
            cv2.putText(marked_image, f"{name}: {result[pt[1], pt[0]]:.2f}", 
                       (pt[0], pt[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # # 保存截图
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            # filename = f"detection_screenshots/simple_{name}_{timestamp}.png"
            # cv2.imwrite(filename, marked_image)
            
            return {
                'x': center_x,
                'y': center_y,
                'name': name,
                'confidence': result[pt[1], pt[0]]
            }
    
    return None