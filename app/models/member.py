from app import db
from sqlalchemy.dialects.mysql import TINYINT


class Member(db.Model):
    __tablename__ = "member"

    SEX_MALE = 1
    SEX_FEMALE = 0
    VALID_INVALID = 0
    VALID_VALID = 1

    username = db.Column(db.String(64), primary_key=True, nullable=False)
    nickname = db.Column(db.String(64))
    sex = db.Column(TINYINT)
    password = db.Column(db.String(32))
    mobile = db.Column(db.String(32))
    email = db.Column(db.String(32))
    birthday = db.Column(db.DateTime)
    portrait = db.Column(db.String(32))
    qq = db.Column(db.String(32))
    is_qq_auth = db.Column(TINYINT)
    signature = db.Column(db.String(255))
    created_dt = db.Column(db.DateTime)
    valid = db.Column(TINYINT)

    __table_args__ = (
        db.Index("act_pwd_index", "account", "password")
    )


class MemberLog(db.Model):
    __tablename__ = "mem_log"

    ACTION_INSERT = 0
    ACTION_UPDATE = 1
    ACTION_DELETE = 2

    log_id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(64))
    action = db.Column(TINYINT, nullable=False)

    his_nickname = db.Column(db.String(64))
    his_sex = db.Column(TINYINT)
    his_password = db.Column(db.String(32))
    his_mobile = db.Column(db.String(32))
    his_email = db.Column(db.String(32))
    his_qq = db.Column(db.String(32))
    his_is_qq_auth = db.Column(TINYINT)
    his_signature = db.Column(db.String(255))

    created_dt = db.Column(db.DateTime)

