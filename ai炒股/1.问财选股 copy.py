import os
import requests
import time
def crawl_and_save(url, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.iwencai.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'sec-ch-ua-platform': "Windows",
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    }
    try:
        # 发送HTTP请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 使用时间戳作为唯一文件名
        timestamp = str(int(time.time()))
        filename = os.path.join(output_dir, f"iwencai_result_{timestamp}.html")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return f"页面保存成功: {filename}"
    
    except Exception as e:
        return f"爬取失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    txt = '筛选出流通市值在10亿到80亿之间的所有个股；剔除所有利空消息个股；剔除科创板和北交所&querytype=stock'
    # 生成防缓存标识addSign=1750473318854
    addSign = str(int(time.time() * 1000))
    query_str = txt + '&addSign=' + addSign  # 使用 + 连接字符串
    url = "https://www.iwencai.com/unifiedwap/result?w=" + query_str  # 使用 + 连接字符串
    result = crawl_and_save(url, "saved_pages")  # 这里传入url而非str
    print(result)


