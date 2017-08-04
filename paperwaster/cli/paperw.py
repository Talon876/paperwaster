#!/usr/bin/env python
import argparse
import yaml
from paperwaster import subscribe
from paperwaster.tprinter import ThermalPrinter

class NullPrinter(object):
    def set_defaults(self): pass
    def print_image(self, img):
        img.save('out.bmp')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    args = ap.parse_args()
    config = yaml.safe_load(open(args.config))
    printer = ThermalPrinter(**config['printer']) if 'printer' in config else NullPrinter()
    try:
        subscribe(config['redis_uri'], printer=printer)
    except KeyboardInterrupt:
        print('Cya!')

if __name__ == '__main__':
    main()
