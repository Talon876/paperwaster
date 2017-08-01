#!/usr/bin/env python

import json
import redis
import sys
import time
import argparse
import traceback

from PIL import Image
import StringIO

from paperwaster import converter
from paperwaster.tprinter import ThermalPrinter

ap = argparse.ArgumentParser()
ap.add_argument('--redis', '-r', help='redis uri e.g. redis://any:password@host:port')
ap.add_argument('--publish', help='Path to image to publish, will subscribe if empty')
args = ap.parse_args()

r = redis.StrictRedis.from_url(args.redis)

if args.publish:
    try:
        print('Publishing {}'.format(args.publish))
        r.publish('paperwaster:messages', args.publish)
    except:
        traceback.print_exc()
else:
    print('Subscribing')
    p = r.pubsub()
    p.subscribe('paperwaster:messages')
    printer = ThermalPrinter()
    printer.set_defaults()
    while True:
        payload = p.get_message()
        if payload:
            if payload['type'] == 'subscribe':
                print('Subscribed to {}'.format(payload['channel']))
            else:
                try:
                    data = payload['data']
                    print('Received image code {}'.format(data))
                    img = converter.code_to_image(data)
                    printer.print_image(img)
                except Exception:
                    traceback.print_exc()
