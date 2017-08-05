import traceback
import argparse

import yaml
import irc.bot
import irc.strings
import redis

from paperwaster import logger, publish_message, publish_image_code

class PrinterBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, password=None, r=None):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname)
        self.channel = channel
        self.r = r
        logger.info('Created irc bot')

    def on_welcome(self, c, e):
        logger.info('Joining channel {}'.format(self.channel))
        c.join(self.channel)

    def on_privmsg(self, c, e):
        try:
            self._handle_message(c, e)
        except Exception as ex:
            traceback.print_exc()
            logger.warn('Unexpected error while handling message')

    def on_pubmsg(self, c, e):
        try:
            self._handle_message(c, e)
        except Exception as ex:
            traceback.print_exc()
            logger.warn('Unexpected error while handling message')

    def _handle_message(self, c, e):
        msg = e.arguments[0]
        nick = e.source.nick
        logger.info('{}: {}'.format(nick, msg.encode('ascii', 'ignore')))
        cmd = msg.split(' ')[0]
        arg = msg[len(cmd)+1:]
        if arg:
            if cmd.lower() == 'print':
                publish_message(arg, font='hack', size=28, r=self.r)
            elif cmd.lower() in ['image', 'img', 'image_code']:
                publish_image_code(arg, r=self.r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    args = ap.parse_args()
    config = yaml.safe_load(open(args.config))
    r = redis.StrictRedis.from_url(config['redis_uri'])
    config['bot']['r'] = r
    bot = PrinterBot(**config['bot'])
    try:
        bot.start()
    except KeyboardInterrupt:
        print('Cya!')
