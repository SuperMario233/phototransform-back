# coding=utf-8
from flask import request, jsonify
from app.models.member import Member, MemberLog
from app.auth import auth, sessionKey2Username
from app.auth.authorize import authorize
from app import db
import datetime


@auth.route('/sign-in', methods=['POST'])
def sign_in():
    """一个返回JSON数据接口的设计示例"""
    username = request.values.get('userName')
    pwd = request.values.get('pwd')

    with db.Session() as session:

        pwds = session.query(Member.password).filter(db.and_(
            Member.username == username,
            Member.valid == 1,
        )).all()

        if len(pwds) == 0 or pwds[0] != pwd:
            return jsonify(dict(
                statusCode="401"
            ))
        else:
            sessionKey = getSessionKey(username)
            sessionKey2Username[sessionKey] = username
            return jsonify(dict(
                statusCode="200",
                sessionKey=""
            ))


@auth.route('/sign-up', methods=['POST'])
def sign_up():
    username = request.values.get('userName')
    pwd = request.values.get('pwd')
    nickname = request.values.get('nickname')
    sex = request.values.get('sex')
    mobile = request.values.get('mobile')
    birthday = request.values.get('birthday')
    portrait = request.values.get('portrait')

    with db.Session() as session:

        rs = session.query(Member.username).filter(db.and_(
            Member.username == username
        )).all()

        if len(rs) != 0:
            return jsonify(dict(
                statusCode="401"
            ))
        else:
            sessionKey = generateNewSessionKey(username)
            sessionKey2Username[sessionKey] = username
            session.add(Member(
                username=username,
                password=pwd,
                nickname=nickname,
                sex=Member.SEX_FEMALE if sex == "F" else Member.SEX_MALE,
                mobile=mobile,
                birthday=datetime.datetime.strptime(birthday, "%Y-%m--%d"),
                portrait=portrait,  # 应当是一个图片
                created_dt=datetime.datetime.now(),
                valid=Member.VALID_VALID
            ))
            session.add(MemberLog(
                username=username,
                action=MemberLog.ACTION_INSERT
            ))
            return jsonify(dict(
                statusCode="200",
                sessionKey=""
            ))

@authorize
@auth.route('/modify-user', methods=['POST'])
def modify_user():
    username = request.values.get('userName')
    pwd = request.values.get('pwd')
    nickname = request.values.get('nickname')
    sex = request.values.get('sex')
    mobile = request.values.get('mobile')
    birthday = request.values.get('birthday')
    portrait = request.values.get('portrait')

    with db.Session() as session:

        rs = session.query(Member).filter(db.and_(
            Member.username == username
        )).all()

        if len(rs) == 0:
            return jsonify(dict(
                statusCode="401"
            ))
        else:
            member = rs[0]

            session.add(MemberLog(
                username=username,
                action=MemberLog.ACTION_UPDATE,

                his_nickname=member.nickname,
                his_sex=member.sex,
                his_password=member.password,
                his_mobile=member.mobile,
                his_email=member.email,
                his_birthday=member.birthday,
                his_portrait=member.portrait,

                created_dt=datetime.datetime.now(),
            ))

            member.update({
                'username': username,
                'password': pwd,
                'nickname': nickname,
                'sex': Member.SEX_FEMALE if sex == "F" else Member.SEX_MALE,
                'mobile': mobile,
                'birthday': datetime.datetime.strptime(birthday, "%Y-%m--%d"),
                'portrait': portrait,  # 应当是一个图片
            })
            
            return jsonify(dict(
                statusCode="200",
                sessionKey=""
            ))

@authorize
@auth.route('/get-userinfo', methods=['POST'])
def get_userinfo():
    sessionKey = request.values.get("sessionKey")
    username = sessionKey2Username.get(sessionKey)

    with db.Session() as session:

        members = session.query(Member).filter(db.and_(
            Member.username == username
        )).all()

        # todo 定义新的两个model
        histories = session.query(MemberUseLog).filter(db.and_(
            MemberUserLog.username == username
        )).all()

        favorites = session.query(MemberStar).filter(db.and_(
            MemberStar.username == username
        )).all()

        if len(members) == 0:
            return jsonify(dict(
                statusCode="400"
            ))
        else:
            member = members[0]

            return jsonify(dict(
                statusCode="200",
                nickName=member.nickname,
                portrait=member.portrait,
                sex=member.sex,
                history='\t'.join(list(map(lambda history: history.fil_id, histories))),
                favority='\t'.join(list(map(lambda favorite: favorite.fil_id, favorites)))
            ))



# todo 根据username获取sessionKey
def getSessionKey(username):
    return sessionKey

# todo
def generateSessionKey(username):
    return sessionKey