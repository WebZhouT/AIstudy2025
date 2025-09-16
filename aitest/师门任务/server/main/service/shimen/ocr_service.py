# 师门 OCR 服务
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np

class ShimenOCRService:
    def __init__(self):
        # 初始化 OCR 引擎
        self.ocr = RapidOCR()
    
    def recognize_text(self, image):
        """
        识别图像中的文字
        :param image: 输入图像
        :return: 识别结果
        """
        # 对图像进行 OCR 识别
        result, elapse = self.ocr(image)
        return result, elapse
    
    def find_text_in_image(self, image, target_text):
        """
        在图像中查找指定文字
        :param image: 输入图像
        :param target_text: 目标文字
        :return: 是否找到以及位置信息
        """
        ocr_result, _ = self.recognize_text(image)
        if ocr_result:
            for text_info in ocr_result:
                if len(text_info) > 1 and target_text in text_info[1]:
                    return True, text_info[0]  # 返回文字位置信息
        return False, None