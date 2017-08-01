# coding: utf-8

from serial import Serial
from struct import unpack
from time import sleep

class ThermalPrinter(object):
    """
        Thermal printing library that controls the "micro panel thermal printer" sold in
        shops like Adafruit and Sparkfun (e.g. http://www.adafruit.com/products/597).
        Mostly ported from Ladyada's Arduino library
        (https://github.com/adafruit/Adafruit-Thermal-Printer-Library) to run on
        BeagleBone and Raspberry Pi.

        Currently handles printing image data and text, but the rest of the
        built-in functionality like underlining and barcodes are trivial
        to port to Python when needed.

        If on BeagleBone or similar device, remember to set the mux settings
        or change the UART you are using. See the beginning of this file for
        default setup.

        Thanks to Matt Richardson for the initial pointers on controlling the
        device via Python.

        @author: Lauri Kainulainen
    """

    SERIALPORT = '/dev/serial0'

    BAUDRATE = 19200
    TIMEOUT = 3

    printer = None

    _ESC = chr(27)

    # These values (including printDensity and printBreaktime) are taken from
    # lazyatom's Adafruit-Thermal-Library branch and seem to work nicely with bitmap
    # images. Changes here can cause symptoms like images printing out as random text.
    # Play freely, but remember the working values.
    # https://github.com/adafruit/Adafruit-Thermal-Printer-Library/blob/0cc508a9566240e5e5bac0fa28714722875cae69/Thermal.cpp

    # Set "max heating dots", "heating time", "heating interval"
    # n1 = 0-255 Max printing dots, Unit (8dots), Default: 7 (64 dots)
    # n2 = 3-255 Heating time, Unit (10us), Default: 80 (800us)
    # n3 = 0-255 Heating interval, Unit (10us), Default: 2 (20us)
    # The more max heating dots, the more peak current will cost
    # when printing, the faster printing speed. The max heating
    # dots is 8*(n1+1). The more heating time, the more density,
    # but the slower printing speed. If heating time is too short,
    # blank page may occur. The more heating interval, the more
    # clear, but the slower printing speed.

    def __init__(self, heatTime=80, heatInterval=2, heatingDots=7, serialport=SERIALPORT):
        self.printer = Serial(serialport, self.BAUDRATE, timeout=self.TIMEOUT)
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(64)) # @   - initialize
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(55)) # 7   - print settings
        self.printer.write(chr(heatingDots))  # Heating dots (20=balance of darkness vs no jams) default = 20
        self.printer.write(chr(heatTime)) # heatTime Library default = 255 (max)
        self.printer.write(chr(heatInterval)) # Heat interval (500 uS = slower, but darker) default = 250

        # Description of print density from page 23 of the manual:
        # DC2 # n Set printing density
        # Decimal: 18 35 n
        # D4..D0 of n is used to set the printing density. Density is 50% + 5% * n(D4-D0) printing density.
        # D7..D5 of n is used to set the printing break time. Break time is n(D7-D5)*250us.
        printDensity = 15 # 120% (? can go higher, text is darker but fuzzy)
        printBreakTime = 15 # 500 uS
        self.printer.write(chr(18))
        self.printer.write(chr(35))
        self.printer.write(chr((printDensity << 4) | printBreakTime))

        self.reset()

    def offline(self):
        # Take the printer offline. Print commands sent after this will be
        # ignored until 'online' is called.
        self.printer.write(self._ESC)
        self.printer.write(chr(61))
        self.printer.write(chr(0))

    def online(self):
        # Take the printer back online. Subsequent print commands will be obeyed.
        self.printer.write(self._ESC)
        self.printer.write(chr(61))
        self.printer.write(chr(1))

    def sleep(self):
        # Put the printer into a low-energy state immediately.
        self.sleep_after(1)  # Can't be 0, that means 'don't sleep'

    def sleep_after(self, seconds):
        # Put the printer into a low-energy state after the given number
        # of seconds.
        if seconds:
            sleep(seconds)
            self.printer.write(self._ESC)
            self.printer.write(chr(56))
            self.printer.write(chr(seconds))
            self.printer.write(chr(seconds >> 8))

    def wake(self):
        # Wake the printer from a low-energy state.
        self.printer.write(chr(255))
        sleep(0.05)
        self.printer.write(self._ESC)
        self.printer.write(chr(56))
        self.printer.write(chr(0))
        self.printer.write(chr(0))

    def has_paper(self):
        # Check the status of the paper using the printer's self reporting
        # ability. SerialTX _must_ be connected!
        status = -1
        self.printer.write(self._ESC)
        self.printer.write(chr(118))
        self.printer.write(chr(0))
        for i in range(0, 9):
            if self.printer.inWaiting():
                status = unpack('b', self.printer.read())[0]
                break
            sleep(0.01)
        return not bool(status & 0b00000100)

    def reset(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(64))

    def linefeed(self, number=1):
        for _ in range(number):
            self.printer.write(chr(10))

    def justify(self, align="L"):
        pos = 0
        align = align.upper()
        if align == "L":
            pos = 0
        elif align == "C":
            pos = 1
        elif align == "R":
            pos = 2
        self.printer.write(self._ESC)
        self.printer.write(chr(97))
        self.printer.write(chr(pos))

    def bold(self, on=True):
        self.printer.write(self._ESC)
        self.printer.write(chr(69))
        self.printer.write(chr(on))

    def font_b(self, on=True):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(on))

    def underline(self, on=True):
        self.printer.write(self._ESC)
        self.printer.write(chr(45))
        self.printer.write(chr(on))

    def inverse(self, on=True):
        self.printer.write(chr(29))
        self.printer.write(chr(66))
        self.printer.write(chr(on))

    def upsidedown(self, on=True):
        self.printer.write(self._ESC)
        self.printer.write(chr(123))
        self.printer.write(chr(on))

    def set_defaults(self):
        self.online()
        self.justify('L')
        self.inverse(False)
        self.bold(False)
        self.fontsize('S')
        self.upsidedown(False)

    def fontsize(self, size='S'):
        pos = 0
        size = size.upper()
        if size == 'L':
            pos = 0x11
        elif size == 'M':
            pos = 0x01
        elif size == 'S':
            pos = 0x00
        self.printer.write(chr(29))
        self.printer.write(chr(33))
        self.printer.write(chr(pos))
        self.printer.write(chr(10))

    def print_text(self, msg, chars_per_line=None):
        """ Print some text defined by msg. If chars_per_line is defined,
            inserts newlines after the given amount. Use normal '\n' line breaks for
            empty lines. """
        if not chars_per_line:
            self.printer.write(msg)
            sleep(0.2)
        else:
            l = list(msg)
            le = len(msg)
            for i in xrange(chars_per_line + 1, le, chars_per_line + 1):
                l.insert(i, '\n')
            self.printer.write("".join(l))
            sleep(0.2)

    def convert_pixel_array_to_binary(self, pixels, w, h):
        """ Convert the pixel array into a black and white plain list of 1's and 0's
            width is enforced to 384 and padded with white if needed. """
        black_and_white_pixels = [1] * 384 * h
        if w > 384:
            print "Bitmap width too large: %s. Needs to be under 384" % w
            return False
        elif w < 384:
            print "Bitmap under 384 (%s), padding the rest with white" % w

        for i, p in enumerate(pixels):
            black_and_white_pixels[i % w + i / w * 384] = 0 if p == 0 else 1

        return black_and_white_pixels

    def print_image(self, img):
        #from PIL import Image
        #i = Image.open("example-lammas.png")
        data = list(img.getdata())
        w, h = img.size
        self.print_bitmap(data, w, h)

    def print_bitmap(self, pixels, w, h, do_lf=False):
        """ Best to use images that have a pixel width of 384 as this corresponds
            to the printer row width.

            pixels = a pixel array of 1 or 0
            w = width of image
            h = height of image

            Example code with PIL:
                import Image, ImageDraw
                i = Image.open("lammas_grayscale-bw.png")
                data = list(i.getdata())
                w, h = i.size
                p.print_bitmap(data, w, h)
        """
        counter = 0

        black_and_white_pixels = self.convert_pixel_array_to_binary(pixels, w, h)
        print_bytes = []

        # read the bytes into an array
        for rowStart in xrange(0, h, 256):
            chunk_height = 255 if (h - rowStart) > 255 else h - rowStart
            print_bytes += (18, 42, chunk_height, 48)

            for i in xrange(0, 48 * chunk_height):
                # read one byte in
                byt = 0
                for xx in xrange(8):
                    pixel_value = black_and_white_pixels[counter]
                    counter += 1
                    # check if this is black
                    if pixel_value == 0:
                        byt += 1 << (7 - xx)

                print_bytes.append(byt)

        # output the array all at once to the printer
        # might be better to send while printing when dealing with
        # very large arrays...
        for b in print_bytes:
            self.printer.write(chr(b))

        if do_lf:
            self.linefeed()
