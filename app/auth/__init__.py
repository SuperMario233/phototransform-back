# coding=utf-8
from flask import Blueprint
from expiringdict import ExpiringDict


auth = Blueprint('auth', __name__)

# 全局字典, 用来存储sessionKey - username值
sessionKey2Username = ExpiringDict(
    max_len=10000,  # 最多同时在线人数
    max_age_seconds=60 * 60 * 4  # 登录状态自动过期时间
)