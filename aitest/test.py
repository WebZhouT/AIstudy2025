
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
from openai import OpenAI

# 初始化 OCR 引擎
ocr = RapidOCR()
messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "科举知识问答", "content": "根据以下问题输出匹配的那一行文字信息，内容中有换行，以换行符为分界线输出包含答案的那一行文字信息"},
    ]

def recognize_text(image_path):
    """
    识别图片中的文本（保留中文、英文、数字和常见标点符号）
    :param image_path: 图片路径
    :return: 识别到的文本
    """
    try:
        # 读取图片
        print(f"正在读取图片: {image_path}")
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # 执行 OCR 识别
        print("正在进行OCR识别...")
        result, _ = ocr(img_array)
        
        # 检查是否有识别结果
        if not result:
            print("OCR未识别到任何文字")
            return "未识别到有效文字"
        
        # 提取所有文本
        recognized_texts = []
        for text_info in result:
            if text_info and len(text_info) > 1:
                text = text_info[1]
                recognized_texts.append(text)
        
        print("OCR识别结果：")
        print("\n".join(recognized_texts))
        
        # 将OCR结果合并为字符串
        ocr_text = "\n".join(recognized_texts)
        
        print("正在调用DeepSeek API...")
        client = OpenAI(
            api_key="sk-4ccd657ec2ca4f6d807de1ae4c393e06", 
            base_url="https://api.deepseek.com"
        )
        
        # 创建当前调用的消息列表（避免全局变量累积）
        current_messages = [
            {"role": "system", "content": "你是一个科举知识问答助手，请根据问题输出包含答案的那一行文字"},
            {"role": "user", "content": ocr_text}
        ]
        
        print("发送给DeepSeek的内容:", current_messages)
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=current_messages,
                stream=False
            )
            print("API响应状态:", response)  # 打印整个响应对象
            ai_response = response.choices[0].message.content
            return ai_response
        except Exception as api_error:
            print(f"API调用错误: {str(api_error)}")
            return f"API调用错误: {str(api_error)}"
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return f"识别过程中发生错误: {str(e)}"

if __name__ == "__main__":
    # 识别文本并获取可视化结果
    print("程序开始运行...")
    result = recognize_text(f"./screenshots/ee112864dc3544ad945edf2a4200a584.jpg")
    print("\n最终返回结果:", result)
