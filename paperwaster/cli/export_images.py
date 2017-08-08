#!/usr/bin/env python
from paperwaster.converter import code_to_image
from paperwaster.web.app import db, create_app
from paperwaster.models import User, Command
import argparse
import json

def main():
    pass

if __name__=='__main__':
    main()
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    args = ap.parse_args()
    with create_app(args.config).app_context():
        img_codes = Command.query.filter(Command.cmd=='image').all()
        for c in img_codes:
            img_code = json.loads(c.data)['code']
            img = code_to_image(img_code)
            img.save('imgs/{}-{}.png'.format(c.timestamp.strftime('%Y-%m-%d_%H-%M-%S'), c.user_id))
            print(c.timestamp)
            print(img_code)
        #u = User(twitch_id=args.twitch, nickname=args.twitch, email=args.email)
        #db.session.add(u)
        #db.session.commit()
