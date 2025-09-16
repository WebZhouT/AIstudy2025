from flask_restplus import Namespace

# 新闻控制器(数据爬取存入数据库)
news_ns = Namespace("news", description="新闻信息的增删改查")
# foods_ns = Namespace("foods", description="产品分类的增删改查")
# # 收藏控制器
# collect_ns = Namespace("collect", description="收藏信息的增删改查")
# # 分类信息的控制器
# sort_ns = Namespace("collect", description="分类信息的增删改查")
# # 用户控制器
# users_index_ns = Namespace("user_index", description="用户登录注册以及基本信息显示")
# users_order_ns = Namespace("user_order", description="用户订单信息增删改查")
# users_userdata_ns = Namespace("user_userdata", description="用户信息的增删改查")