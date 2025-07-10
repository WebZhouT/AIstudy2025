# 关键词映射筛选出全部个股
import json

# 热点板块关键词映射
sector_keywords = {
    "人工智能（AI）板块": ["人工智能", "AI", "脑机接口", "机器视觉", "多模态AI", "DeepSeek", "AIGC", "ChatGPT"],
    "算力/数据中心板块": ["算力", "数据中心", "东数西算", "云计算", "云办公", "云服务", "服务器", "IDC", "数据要素"],
    "智能汽车板块": ["智能汽车", "无人驾驶", "车联网", "智能座舱", "汽车电子", "新能源汽车", "华为汽车", "小米汽车", "特斯拉", "比亚迪"],
    "金融科技板块": ["金融科技", "移动支付", "数字货币", "区块链", "互联网金融", "虚拟资产", "稳定币"],
    "军工/地缘安全板块": ["军工", "军民融合", "国防", "无人机", "航空发动机", "大飞机", "海工装备", "地缘安全", "军工信息化"]
}

def filter_stocks_by_sector(stock_data):
    """
    根据板块关键词筛选股票
    :param stock_data: 股票数据列表
    :return: 按板块分类的股票字典
    """
    sector_stocks = {sector: [] for sector in sector_keywords}
    
    for stock in stock_data:
        concepts = stock["所属概念"].split(";")
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in concepts for keyword in keywords):
                # 提取关键信息
                simplified_stock = {
                    "股票代码": stock["股票代码"],
                    "股票简称": stock["股票简称"],
                    "现价（元）": stock["现价（元）"],
                    "涨跌幅(%)": stock["涨跌幅(%)"],
                    "所属概念": stock["所属概念"]
                }
                sector_stocks[sector].append(simplified_stock)
                
    return sector_stocks

# 示例使用
if __name__ == "__main__":
    # 从JSON文件加载数据（实际使用时替换为您的文件路径）
    with open('股票池.json', 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    
    # 筛选股票
    result = filter_stocks_by_sector(stock_data)
    
    # 打印结果
    for sector, stocks in result.items():
        print(f"\n===== {sector} ({len(stocks)}只) =====")
        for stock in stocks:
            print(f"{stock['股票代码']} {stock['股票简称']} "
                  f"| 现价: {stock['现价（元）']}元 "
                  f"| 涨跌幅: {stock['涨跌幅(%)']}% "
                  f"| 概念: {stock['所属概念'][:30]}...")