import traceback
import argparse
import json
import yaml
import irc.bot
import irc.strings
import redis

from paperwaster import logger, parse_message, publish
from paperwaster.web.app import db, create_app
from paperwaster.models import User, Message, Command

class PrinterBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, password=None, r=None, config=None):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname)
        self.channel = channel
        self.r = r
        self.config = config
        logger.info('Created irc bot')

    def on_welcome(self, c, e):
        logger.info('Joining channel {}'.format(self.channel))
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self._handle_message(c, e)

    def on_pubmsg(self, c, e):
        self._handle_message(c, e)

    def _handle_message(self, c, e):
        try:
            msg = e.arguments[0]
            nick = e.source.nick
            with create_app(self.config).app_context():
                user = self._get_user(nick)
                logger.info('{}: {}'.format(nick, msg.encode('ascii', 'ignore')))
                cmd = publish(parse_message(msg), r=self.r)
                self._save_cmd(cmd, user)
                self._save_msg(msg, user)
        except Exception as ex:
            traceback.print_exc()
            logger.warn('Unexpected error while handling message')

    def _get_user(self, nick):
        u = User.query.filter_by(twitch_id=nick).first()
        if not u:
            logger.info('Creating user for {}'.format(nick))
            u = User(twitch_id=nick, nickname=nick, email=None)
            db.session.add(u)
            db.session.commit()
        return u

    def _save_cmd(self, cmd, user):
        if not cmd: return
        cmd_name = cmd['cmd']
        del cmd['cmd']
        c = Command(cmd=cmd_name, data=json.dumps(cmd), user=user)
        db.session.add(c)
        db.session.commit()

    def _save_msg(self, msg, user):
        m = Message(body=msg, user=user)
        db.session.add(m)
        db.session.commit()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', '-c', help='path to config file', default='config.yaml')
    args = ap.parse_args()
    config = yaml.safe_load(open(args.config))
    r = redis.StrictRedis.from_url(config['redis_uri'])
    bot = PrinterBot(
        channel=config['bot']['channel'],
        nickname=config['bot']['nickname'],
        server=config['bot']['server'],
        password=config['bot']['password'],
        config=args.config,
        r=r
    )
    try:
        bot.start()
    except KeyboardInterrupt:
        print('Cya!')
