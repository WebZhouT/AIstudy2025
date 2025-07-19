import cv2
import numpy as np

def find_image_position(screenshot_path, template_path, threshold=0.8):
    """
    获取模板图片在屏幕截图中的位置和尺寸信息
    
    参数:
        screenshot_path: 屏幕截图文件路径
        template_path: 模板图片文件路径
        threshold: 匹配阈值(0-1),默认0.8
    
    返回:
        字典包含匹配区域的位置和尺寸信息:
        {
            'x': 左上角x坐标,
            'y': 左上角y坐标,
            'width': 匹配区域宽度,
            'height': 匹配区域高度,
            'confidence': 匹配置信度
        }
        如果未找到匹配区域则返回None
    """
    # 读取截图和模板图片
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    
    if screenshot is None or template is None:
        raise ValueError("无法读取图片文件")
    
    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 检查匹配结果是否超过阈值
    if max_val < threshold:
        return None
    
    # 获取模板尺寸
    h, w = template.shape[:2]
    
    # 计算匹配区域坐标和尺寸
    x, y = max_loc
    position_info = {
        'x': x,
        'y': y,
        'width': w,
        'height': h,
        'confidence': float(max_val)
    }
    
    return position_info

# 示例用法
if __name__ == "__main__":
    # 示例文件路径 - 实际使用时需要替换
    screenshot_file = "screenshot.png"
    template_file = "template.png"
    
    try:
        position = find_image_position(screenshot_file, template_file)
        if position:
            print(f"找到匹配区域: x={position['x']}, y={position['y']}, "
                  f"width={position['width']}, height={position['height']}, "
                  f"置信度: {position['confidence']:.2f}")
        else:
            print("未找到匹配区域")
    except Exception as e:
        print(f"发生错误: {str(e)}")