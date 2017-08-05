import datetime as dt

from paperwaster.web.app import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.String(255), index=True)
    nickname = db.Column(db.String(128), index=True)
    email = db.Column(db.String(255), index=True, unique=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    dots = db.Column(db.Integer, default=0, nullable=False)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    commands = db.relationship('Command', backref='user', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.twitch_id)

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    body = db.Column(db.String(1024))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<{}>'.format(self.body.encode('ascii', 'ignore'))

class Command(db.Model):
    __tablename__ = 'command'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    cmd = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    data = db.Column(db.String(2048))
