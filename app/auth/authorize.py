# -*- coding: utf-8 -*-
from functools import wraps
from flask import request, jsonify
from app.auth import sessionKey2Username


# 装饰器函数. 从请求中检查sessionKey参数并从全局变量中检查有没有相应的sessionKey
# todo 需要做登录状态检查的接口都要带上这个装饰器
def authorize(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        sessionKey = request.values.get('sessionKey')

        username = sessionKey2Username.get(sessionKey) if sessionKey else None
        if not username:
            jsonify(dict(
                statusCode="403"  # 无权限状态码
            ))
        else:
            return fn(*args, **kwargs)

    return wrapper
