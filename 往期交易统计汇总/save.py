import csv
import json
def csv_to_json(csv_filename, json_filename):
    data = []
    with open(csv_filename, 'r', encoding='utf-8', errors='ignore') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            extracted_data = {
                "number": row["订单编号"],
                "title": row["宝贝标题 "].strip(),
                "price": row["总金额"],
                "payTime": row["订单付款时间 "].strip()
            }
            data.append(extracted_data)
    
    # 写入 JSON 文件
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

csv_to_json('ExportOrderList202505112129.csv', 'orders.json')