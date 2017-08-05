#!/usr/bin/env python
import argparse
import datetime as dt
import pytz
timezone = pytz.timezone('America/Denver')

from paperwaster.web.app import db, create_app
from paperwaster.models import User, Message

def init_db():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    args = ap.parse_args()

    with create_app(args.config).app_context():
        db.create_all()

def add_user():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    ap.add_argument('--twitch', '-t', help='twitch id')
    ap.add_argument('--email', '-e', help='twitch id')
    args = ap.parse_args()
    with create_app(args.config).app_context():
        u = User(twitch_id=args.twitch, nickname=args.twitch, email=args.email)
        db.session.add(u)
        db.session.commit()

def message_import():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    ap.add_argument('filename', help='path to file')
    args = ap.parse_args()
    lines = [s.strip() for s in open(args.filename).readlines()]
    with create_app(args.config).app_context():
        for l in lines:
            time = l[12:20]
            h, m, s = [int(n) for n in time.split(':')]
            ts = dt.datetime(2017, 1, 7, h, m, s)
            # create utc naive dt object from the MDT timestamp
            ts = timezone.localize(ts).astimezone(pytz.utc).replace(tzinfo=None)
            msgline = l[27:]
            nick, msg = msgline.split(':', 1)
            msg = msg[1:]
            print('{},{},{}').format(ts, nick, msg)

            u = User.query.filter_by(twitch_id=nick).first()
            if not u:
                print('Creating {}'.format(nick))
                u = User(twitch_id=nick, nickname=nick, email=None, created_at=ts)
                db.session.add(u)
                db.session.commit()

            m = Message(timestamp=ts, body=msg, user=u)
            db.session.add(m)
            db.session.commit()



