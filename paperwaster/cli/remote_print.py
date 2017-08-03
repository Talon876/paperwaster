#!/usr/bin/env python
import argparse
import yaml

from paperwaster import publish_image_code, publish_message

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    ap.add_argument('--message', '-m', help='message to print')
    ap.add_argument('--font', '-f', help='name of the font to use', default='hack')
    ap.add_argument('--size', '-s', help='size of font', default=24, type=int)
    ap.add_argument('--image', '-i', help='image code to print')
    args = ap.parse_args()
    config = yaml.safe_load(open(args.config))
    if args.message:
        publish_message(args.message, args.font, args.size, redis_uri=config['redis_uri'])

    if args.image:
        publish_image_code(args.image, redis_uri=config['redis_uri'])

if __name__ == '__main__':
    main()
