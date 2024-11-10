from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_sessions import SqlAlchemyBase
import sqlalchemy


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    is_seller = sqlalchemy.Column(sqlalchemy.Boolean)
    seller_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('sellers.id'))
    hashed_password = sqlalchemy.Column(sqlalchemy.String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
