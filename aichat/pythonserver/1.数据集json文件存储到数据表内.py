import json
import mysql.connector
from mysql.connector import Error

def insert_search_results(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)  # 读取单个搜索结果

        # 将单个结果包装成列表
        all_search_data = [raw_data]

        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'aichat'
        }

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        sql = """
        INSERT INTO search_results (
            search_id, status, json_endpoint, created_at, processed_at,
            google_light_url, raw_html_file, total_time_taken, engine,
            search_query, location_requested, location_used, google_domain,
            hl, gl, device, query_displayed, organic_results_state,
            organic_result_position_1, organic_result_title_1, organic_result_link_1,
            organic_result_displayed_link_1, organic_result_snippet_1,
            organic_result_extensions_1, organic_result_rating_1,
            organic_result_reviews_1, organic_result_position_2,
            organic_result_title_2, organic_result_link_2,
            organic_result_displayed_link_2, organic_result_snippet_2,
            organic_result_position_3, organic_result_title_3,
            organic_result_link_3, organic_result_displayed_link_3,
            organic_result_snippet_3, related_question_question_1,
            related_question_snippet_1, related_question_title_1,
            related_question_link_1, related_question_displayed_link_1,
            related_question_more_results_link_1, related_question_question_2,
            related_question_snippet_2, related_question_title_2,
            related_question_link_2, related_question_displayed_link_2,
            related_question_more_results_link_2
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for data in all_search_data:
            # 处理主数据部分
            search_metadata = data.get('search_metadata', {})
            search_parameters = data.get('search_parameters', {})
            search_information = data.get('search_information', {})
            organic_results = data.get('organic_results', [])
            related_questions = data.get('related_questions', [])

            # 处理时间字段（安全方式）
            created_at = search_metadata.get('created_at', '').replace(' UTC', '') or None
            processed_at = search_metadata.get('processed_at', '').replace(' UTC', '') or None

            values = [
                search_metadata.get('id'),
                search_metadata.get('status'),
                search_metadata.get('json_endpoint'),
                created_at,
                processed_at,
                search_metadata.get('google_light_url'),
                search_metadata.get('raw_html_file'),
                search_metadata.get('total_time_taken'),
                search_parameters.get('engine'),
                search_parameters.get('q'),
                search_parameters.get('location_requested'),
                search_parameters.get('location_used'),
                search_parameters.get('google_domain'),
                search_parameters.get('hl'),
                search_parameters.get('gl'),
                search_parameters.get('device'),
                search_information.get('query_displayed'),
                search_information.get('organic_results_state'),
            ]

            # 处理前3条organic结果
            for i in range(3):
                result = organic_results[i] if i < len(organic_results) else {}
                values += [
                    result.get('position'),
                    result.get('title'),
                    result.get('link'),
                    result.get('displayed_link'),
                    result.get('snippet'),
                    ', '.join(result.get('extensions', [])) if i == 0 and result.get('extensions') else None,
                    result.get('rating') if i == 0 else None,
                    result.get('reviews') if i == 0 else None
                ][:8 if i == 0 else 5]  # 第一个结果取8个字段，其他取5个

            # 处理前2条相关问题
            for i in range(2):
                question = related_questions[i] if i < len(related_questions) else {}
                values += [
                    question.get('question'),
                    question.get('snippet'),
                    question.get('title'),
                    question.get('link'),
                    question.get('displayed_link'),
                    question.get('more_results_link')
                ]

            # 执行插入
            cursor.execute(sql, values)
            print("数据插入成功")

        connection.commit()
        print(f"成功插入{len(all_search_data)}条数据")

    except Error as e:
        print(f"数据库错误: {e}")
        connection.rollback()
    except Exception as e:
        print(f"其他错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 调用函数
insert_search_results('./fileData/1.json')