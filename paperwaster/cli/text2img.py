#!/usr/bin/env python
from paperwaster import converter
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('msg', help='Message to print')
    ap.add_argument('--size', '-s', help='Font size', default=24, type=int)
    ap.add_argument('--out', '-o', help='Output filename', default='message.bmp')
    args = ap.parse_args()

    img = converter.text_to_image(args.msg, font_path=converter.fonts['hack'], font_size=args.size)
    img.save(args.out)

if __name__=='__main__':
    main()
