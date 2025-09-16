from flask_restplus import fields, Namespace
from ..util.exts import *


class UserDTO:
    login_model = auth_ns.model("login_model",{
        "message":fields.String,
        "token":fields.String,
        "username":fields.String,
        "email":fields.String,
        "id":fields.Integer

    })
    user_login_data_model = auth_ns.model("user_login_data_model",{
        "email": fields.String,
        "password": fields.String
    })
    user_login_error_model = auth_ns.model("user_login_error_model", {
        "message":fields.String
    })
    user_list_model = auth_ns.model("user_list_model",{
        "total_number":fields.Integer,
        "users":fields.List(fields.Nested(login_model))
    })

    user_logout_data_model = auth_ns.model("user_logout_data_model",{
        "token":fields.String
    })

    user_logout_model = auth_ns.model("user_logout_model",{
        "message":fields.String
    })

    user_register_data_model = auth_ns.model("user_register_data_model",{
        "email":fields.String,
        "password":fields.String,
        "username":fields.String
    })

    user_register_model = auth_ns.model("user_register_model", {
        "message":fields.String,
        "username":fields.String
    })

    user_register_error_model = auth_ns.model("user_register_error_model", {
        "message":fields.String
    })

    user_profile_data_model = user_ns.model("user_profile_data_model", {
        "token":fields.String,
        "username":fields.String
    })

    user_profile_model = user_ns.model("user_profile_model", {
        "id":fields.Integer,
        "username":fields.String,
        "email":fields.String,
        "image_QR_code":fields.String,
        "image_user":fields.String
    })

    user_profile_error_model = user_ns.model("user_profile_error_model", {
        "message":fields.String
    })



class RecipeDTO:
    # recipe_detail_data_model = recipe_ns.model("recipe_detail_data_model",{
    #     "id":fields.Integer,
    #     "image":fields.String,
    #     "recipe_image":fields.String,
    #     "type":fields.String,
    #     "cook_method":fields.String,
    #     "ingredients":fields.String,
    #     "recipe_name":fields.String,
    #     "num_of_like":fields.Integer,
    #     "description":fields.String,
    #     "cooking_time":fields.String,
    #     "steps_words":fields.String,
    #     "rank":fields.Integer,
    #     "update_time":fields.DateTime,
    #     "contributor_name":fields.String,
    #     "users":fields.Nested({
    #             "id":fields.Integer,
    #             "username":fields.String,
    #             "email":fields.String,
    #             "image_QR_code":fields.String,
    #             "image_user":fields.String
    #         }),
    #     "comments":fields.Nested({
    #         "username":fields.String,
    #         "image_user":fields.String,
    #         "comment_time":fields.DateTime,
    #         "content":fields.String,
    #     }),
    # })

    recipe_detail_error_model = user_ns.model("recipe_detail_error_model", {
        "message":fields.String
    })