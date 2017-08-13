from . import db


class Icinga_info(db.Model):
    __tablename__ = 'icinga_info'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    time = db.Column(db.DateTime())
    level = db.Column(db.VARCHAR)
    host = db.Column(db.VARCHAR)
    ip = db.Column(db.VARCHAR)
    service = db.Column(db.VARCHAR)
    message = db.Column(db.VARCHAR)
