import time
import redis
import json
import logging
import traceback

logformat = '%(asctime)s %(threadName)-14s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.INFO, format=logformat)
logger = logging.getLogger('paperwaster')

from paperwaster import converter
from paperwaster.tprinter import ThermalPrinter


def publish_image_code(ic, r=None, redis_uri=None):
    return publish({
        'cmd': 'image',
        'code': ic,
    }, r=r, redis_uri=redis_uri)

def publish_message(msg, font, size, r=None, redis_uri=None):
    return publish({
        'cmd': 'print',
        'msg': msg,
        'font': font,
        'size': size
    }, r=r, redis_uri=redis_uri)

def publish(command, r=None, redis_uri=None):
    if command['cmd'] == 'nop': return
    r = r or redis.StrictRedis.from_url(redis_uri)
    logger.info('Publishing {}'.format(command))
    r.publish('paperwaster:messages', json.dumps(command))
    return command

def subscribe(redis_uri=None, r=None, printer=None):
    logger.info('Subscribing')
    r = r or redis.StrictRedis.from_url(redis_uri)
    p = r.pubsub()
    p.subscribe('paperwaster:messages')
    printer = printer or ThermalPrinter()
    printer.set_defaults()
    while True:
        payload = p.get_message()
        if not payload:
            time.sleep(0.1)
            continue
        if payload['type'] == 'subscribe':
            logger.info('Subscribed to {}'.format(payload['channel']))
        else:
            try:
                command = json.loads(payload['data'])
                _handle_command(printer, command)
            except Exception as ex:
                logger.error('Exception occurred while processing {}'.format(payload))
                traceback.print_exc()

def _handle_command(printer, command):
    logger.info('Handling command {}'.format(command))
    if command['cmd'] == 'print':
        command['msg'] = command['msg'].encode('ascii', 'ignore')
        logger.info('Printing message {msg} (font: {font} {size})'.format(**command))
        img = converter.text_to_image(command['msg'],
                                      font_path=converter.fonts[command['font']],
                                      font_size=command['size'])
        printer.print_image(img)
    elif command['cmd'] == 'image':
        logger.info('Printing image code {}'.format(command['code']))
        img = converter.code_to_image(command['code'])
        printer.print_image(img, do_lf=True)
    elif command['cmd'] == 'reset':
        printer.reset()
        printer.set_defaults()
    elif command['cmd'] == 'linefeed':
        printer.linefeed()
    else:
        logger.info('Unknown command type {}'.format(command))

size_map = {
    'tiny': 12,
    'small': 18,
    'medium': 26,
    'large': 32,
}

def parse_message(msg):
    cmd = msg.split(' ')[0]
    arg = msg[len(cmd)+1:]
    if cmd.lower() in ['print'] and arg:
        return {'cmd': 'print', 'msg': arg, 'font': 'hack', 'size': 22}

    elif cmd.lower() in ['tiny'] and arg:
        return {'cmd': 'print', 'msg': arg, 'font': 'hack-bold', 'size': 12}

    elif cmd.lower() in ['small'] and arg:
        return {'cmd': 'print', 'msg': arg, 'font': 'hack-bold', 'size': 18}

    elif cmd.lower() in ['medium'] and arg:
        return {'cmd': 'print', 'msg': arg, 'font': 'hack', 'size': 26}

    elif cmd.lower() in ['large'] and arg:
        return {'cmd': 'print', 'msg': arg, 'font': 'hack', 'size': 32}

    elif cmd.lower() in ['image', 'img', 'image_code'] and arg:
        return {'cmd': 'image', 'code': arg}

    elif cmd.lower() in ['moar', 'linefeed']:
        return {'cmd': 'linefeed'}

    elif cmd.lower() in ['reset']:
        return {'cmd': 'reset'}

    else:
        return {'cmd': 'nop', 'msg': msg}

