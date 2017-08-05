"""
Converts strings in to monochrome bitmaps using PIL
"""
import os
import textwrap
import string

from PIL import Image, ImageDraw, ImageFont

PRINTER_WIDTH = 384

font_files = [f for f in os.listdir(os.path.join(os.path.split(__file__)[0], 'fonts'))]
fonts = {os.path.splitext(f)[0]: os.path.join(os.path.split(__file__)[0], 'fonts', f) for f in font_files}

def text_to_image(msg, font=None, font_path=None, font_size=24, accurate=True):
    font = font if font else ImageFont.truetype(font_path, font_size)
    wrapper = textwrap.TextWrapper()

    # w is the widest and y is the tallest
    glyph_w, glyph_h = font.getsize('w')[0], font.getsize('y')[1]
    chars_per_line = PRINTER_WIDTH / glyph_w 
    wrapper.width = chars_per_line

    msg_lines = wrapper.wrap(msg)
    # lines may vary in height so loop over all of them when accurate is True
    # otherwise just count each line as the height of a 'y'
    height = sum([font.getsize(h)[1] for h in msg_lines]) if accurate else glyph_h * len(msg_lines)

    img = Image.new('1', (PRINTER_WIDTH, height), color='white')
    draw = ImageDraw.Draw(img)
    y = 0
    for line in msg_lines:
        h = font.getsize(line)[1]
        draw.text([0, y], line, font=font)
        y += h
    return img

def code_to_image(image_code, pixel_size=8, trim=True):
    image_data = ''.join([str(bin(int(s, 16)))[2:].zfill(32) for s in image_code.split('-')])
    num_rows = len(image_data) / (PRINTER_WIDTH / pixel_size)
    img = Image.new('1', (PRINTER_WIDTH, num_rows * pixel_size), color='white')
    draw = ImageDraw.Draw(img)

    for ty, row in enumerate(_chunks(image_data, PRINTER_WIDTH/pixel_size)):
        for tx, cell in enumerate(row):
            if cell == '1':
                x, y = tx*pixel_size, ty*pixel_size
                draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill='black')
    return trim_whitespace(img) if trim else img

def trim_whitespace(img):
    w, h = img.size
    top_row, btm_row = 0, 0
    # loop through each row, looking for the first and last rows with a black pixel
    for y in range(h):
        if 0 in [img.getpixel((x, y)) for x in range(w)]:
            top_row = y if top_row == 0 else top_row
            btm_row = y
    return img.crop((0, top_row, w, btm_row))

def _chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]
