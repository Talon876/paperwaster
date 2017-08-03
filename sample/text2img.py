#!/usr/bin/env python
from paperwaster import converter
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('msg', help='Message to print')
ap.add_argument('--size', '-s', help='Font size', default=24, type=int)
args = ap.parse_args()

img = converter.text_to_image(args.msg, font_path=converter.fonts['hack'], font_size=args.size)
img.save('hmm.bmp')
