#!/usr/bin/env python
import os
import traceback
from paperwaster.converter import code_to_image
from paperwaster.web.app import db, create_app
from paperwaster.models import User, Command
from dateutil import parser
import argparse
import json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    ap.add_argument('--out', '-o', help='directory to output images to', default='imgs')
    ap.add_argument('--after', '-a', help='filter to images after this date', required=True)
    args = ap.parse_args()
    if not os.path.isdir(args.out):
        os.makedirs(args.out)
    with create_app(args.config).app_context():
        after_date = parser.parse(args.after)
        img_codes = Command.query.filter(Command.cmd=='image', Command.timestamp>=after_date).all()
        print('Exporting {} images after {}'.format(len(img_codes), after_date.isoformat()))
        for c in img_codes:
            try:
                img_code = json.loads(c.data)['code']
                fn = '{}/{}-{}.png'.format(args.out, c.timestamp.strftime('%Y-%m-%d_%H-%M-%S'), c.user_id)
                if not os.path.exists(fn):
                    img = code_to_image(img_code)
                    img.save(fn)
                else:
                    print('{} already exists - skipping'.format(fn))
            except Exception:
                traceback.print_exc()
                print('Failed to convert image code {}'.format(img_code))

if __name__=='__main__':
    main()
