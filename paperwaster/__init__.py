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
    r = r or redis.StrictRedis.from_url(redis_uri)
    r.publish('paperwaster:messages', json.dumps({'type': 'image_code', 'image_code': ic}))

def publish_message(msg, font, size, r=None, redis_uri=None):
    r = r or redis.StrictRedis.from_url(redis_uri)
    payload = {
        'type': 'message',
        'message': msg,
        'font': font,
        'size': size
    }
    r.publish('paperwaster:messages', json.dumps(payload))


def subscribe(redis_uri=None, r=None, printer=None):
    logger.info('Subscribing')
    r = r or redis.StrictRedis.from_url(redis_uri)
    p = r.pubsub()
    p.subscribe('paperwaster:messages')
    printer = printer or ThermalPrinter()
    printer.set_defaults()
    while True:
        payload = p.get_message()
        if not payload: continue
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
    if command['type'] == 'image_code':
        logger.info('Printing image code {}'.format(command['image_code']))
        img = converter.code_to_image(command['image_code'])
        printer.print_image(img)
    elif command['type'] == 'message':
        command['message'] = command['message'].encode('ascii', 'ignore')
        logger.info('Printing message {message} (font: {font} {size})'.format(**command))
        img = converter.text_to_image(command['message'],
                                      font_path=converter.fonts[command['font']],
                                      font_size=command['size'])
        printer.print_image(img)
    else:
        logger.info('Unknown command type {}'.format(command))

