from pynput.mouse import Controller
import time
import math

mouse = Controller()

def smooth_move_to(x, y, duration=0.5, steps=60):
    """
    平滑移动鼠标到指定坐标（带动画效果）
    
    参数:
    - x, y: 目标坐标
    - duration: 移动总时间（秒）
    - steps: 移动步数（越多越平滑）
    """
    current_x, current_y = mouse.position
    step_time = duration / steps
    
    for step in range(steps + 1):
        # 计算当前进度（0到1之间）
        progress = step / steps
        # 使用缓动函数让移动更自然（可选）
        # progress = math.sin(progress * math.pi / 2)  # 缓入效果
        progress = progress ** 0.5  # 缓出效果
        
        # 计算中间坐标
        intermediate_x = current_x + (x - current_x) * progress
        intermediate_y = current_y + (y - current_y) * progress
        
        # 移动鼠标
        mouse.position = (int(intermediate_x), int(intermediate_y))
        time.sleep(step_time)

# 使用示例
if __name__ == "__main__":
    print("当前鼠标位置:", mouse.position)
    smooth_move_to(1638, 494)  # 移动到屏幕(500,500)位置
    print("移动后位置:", mouse.position)