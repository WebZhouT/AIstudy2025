import win32gui
import time
import win32ui
import win32con
from PIL import Image
import pywintypes

def get_window_info(hwnd):
    """获取指定窗口的详细信息"""
    try:
        # 首先验证窗口句柄是否仍然有效
        if not win32gui.IsWindow(hwnd):
            return None
            
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        return {
            "handle": hwnd,
            "title": title,
            "class": class_name,
            "position": (left, top),
            "size": (width, height),
            "rect": (left, top, right, bottom)
        }
    except pywintypes.error as e:
        print(f"获取窗口信息时出错 (句柄: {hwnd}): {e}")
        return None

def print_window_info(hwnd):
    """打印窗口信息"""
    info = get_window_info(hwnd)
    if info is None:
        print(f"\n窗口句柄 {hwnd} 无效或窗口已关闭")
        return
    
    print("\n窗口详细信息:")
    print(f"句柄: {info['handle']}")
    print(f"标题: '{info['title']}'")
    print(f"类名: '{info['class']}'")
    print(f"位置: (X={info['position'][0]}, Y={info['position'][1]})")
    print(f"大小: 宽={info['size'][0]}px, 高={info['size'][1]}px")
    print(f"坐标: {info['rect']}")

def capture_window(hwnd, filename="window_capture.png"):
    """截取指定窗口的图像并保存(改进版)"""
    try:
        if not win32gui.IsWindow(hwnd):
            print(f"无法截图 - 窗口句柄 {hwnd} 无效")
            return False

        # 确保窗口可见且未最小化
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)  # 等待窗口激活

        # 获取窗口尺寸(考虑DPI缩放)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # 使用窗口DC而非客户区DC
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        # 创建位图对象
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        
        # 尝试使用PrintWindow API作为备用方案
        try:
            saveDC.SelectObject(saveBitMap)
            result = win32gui.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            if not result:
                raise RuntimeError("PrintWindow API调用失败")
        except:
            # 如果PrintWindow失败，回退到BitBlt
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        # 转换为PIL图像
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        # 尝试增强图像质量
        if sum(im.convert("L").point(lambda x: 255 if x > 250 else 0).getextrema()) == 0:
            print("警告: 截图可能为空白，尝试备用方案...")
            im = Image.new('RGB', (width, height), (255, 255, 255))  # 空白替代
            
        im.save(filename, quality=95)
        print(f"窗口截图已保存为: {filename}")
        return True

    except Exception as e:
        print(f"截图失败 (句柄: {hwnd}): {str(e)}")
        return False
    finally:
        # 资源释放(保持不变)
        pass
def flash_top_window(duration=5, capture=False):
    """检测置顶窗口并输出信息"""
    start_time = time.time()
    print(f"\n开始检测{duration}秒内的置顶窗口...")
    
    last_hwnd = None
    while time.time() - start_time < duration:
        try:
            current_hwnd = win32gui.GetForegroundWindow()
            if current_hwnd != last_hwnd:
                print_window_info(current_hwnd)
                if capture and current_hwnd and win32gui.IsWindow(current_hwnd):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"window_{timestamp}.png"
                    capture_window(current_hwnd, filename)
                last_hwnd = current_hwnd
            time.sleep(0.1)
        except Exception as e:
            print(f"检测窗口时发生错误: {e}")
            time.sleep(0.5)  # 发生错误后稍作等待

if __name__ == "__main__":
    # 延迟5秒执行
    time.sleep(5)
    # 检测当前置顶窗口并截图
    flash_top_window(duration=5, capture=True)
    
    # 如果只想截图特定窗口，可以这样使用:
    # hwnd = int(input("请输入窗口句柄: "))
    # if win32gui.IsWindow(hwnd):
    #     capture_window(hwnd, "specific_window.png")
    # else:
    #     print("无效的窗口句柄")