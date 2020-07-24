# project/api/model.py

import datetime
from project import db
from marshmallow import Schema, fields, post_load


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()

    #  反序列化
    @post_load
    def make_user(self, data):
        return User(**data)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.created_at = datetime.datetime.utcnow()

    # # 自定义序列化 fail
    # def keys(self):
    #     # keys()方法返回值为一个序列，用于告诉dict，当前dict()的key值
    #     return ['id','username','email','created_at']

    # def __getitem__(self,item):
    #     return getattr(self,item)
