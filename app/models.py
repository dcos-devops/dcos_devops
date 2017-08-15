from datetime import datetime
from sqlalchemy.sql.elements import Null
from . import db


class Icinga_info(db.Model):
    __tablename__ = 'icinga_info'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime())
    level = db.Column(db.VARCHAR)
    host = db.Column(db.VARCHAR)
    ip = db.Column(db.VARCHAR)
    service = db.Column(db.VARCHAR)
    message = db.Column(db.VARCHAR)


class Host(db.Model):
    __tablename__ = 'host'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.VARCHAR(60), default=Null, nullable=True)
    ip = db.Column(db.VARCHAR(100), default=Null, nullable=True)
    cpu = db.Column(db.Integer, default=Null, nullable=True)
    mem = db.Column(db.Integer, default=Null, nullable=True)
    created_timestamp = db.Column(db.DateTime(), default=datetime.utcnow)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.VARCHAR(255), default=Null)


class Host_tag_relation(db.Model):
    __tablename__ = 'host_tag_relation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_id = db.Column(db.Integer, nullable=False)
    tag_name = db.Column(db.VARCHAR(60), nullable=False)
