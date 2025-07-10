import csv
import json

def json_to_csv(json_file, csv_file):
    # 从JSON文件读取数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 定义要导出的字段
    selected_fields = ["序号", "股票代码", "股票简称", "涨停原因类别", "流通市值"]
    
    # 写入CSV文件
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=selected_fields)
        
        # 写入表头
        writer.writeheader()
        
        # 写入数据行
        for row in data:
            # 处理缺失字段，使用空字符串作为默认值
            selected_row = {
                field: row.get(field, "")  # 使用get方法避免KeyError
                for field in selected_fields
            }
            writer.writerow(selected_row)
    
    print(f"CSV文件已生成：{csv_file}")

# 使用示例
if __name__ == "__main__":
    input_json = "涨停个股.json"  # 输入JSON文件名
    output_csv = "涨停个股.csv"   # 输出CSV文件名
    json_to_csv(input_json, output_csv)