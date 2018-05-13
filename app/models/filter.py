from app import db
from sqlalchemy.dialects.mysql import TINYINT


class Filter(db.Model):
    __tablename__ = "filter"

    IS_DEFAULT_TRUE = 1
    IS_DEFAULT_FALSE = 0

    fil_id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255))
    created_dt = db.Column(db.DateTime)
    created_by = db.Column(db.String(255))
    is_default = db.Column(TINYINT)

    valid = db.Column(TINYINT)


class FilterLog(db.Model):
    __tablename__ = "fil_log"

    ACTION_INSERT = 0
    ACTION_UPDATE = 1
    ACTION_DELETE = 2

    log_id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True)
    fil_id = db.Column(db.BIGINT)
    action = db.Column(TINYINT, nullable=False)

    his_name = db.Column(db.String(255))
    his_path = db.Column(db.String(255))

    created_dt = db.Column(db.DateTime)

