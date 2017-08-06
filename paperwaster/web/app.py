import yaml
import logging

from flask import Flask
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_login import LoginManager, current_user

db = SQLAlchemy()
red = FlaskRedis()
lm = LoginManager()
lm.login_view = 'page.login'
limiter = Limiter(key_func=lambda: unicode(current_user.twitch_id))

logger = logging.getLogger('paperwaster.web')
from paperwaster.web.blueprints import api
from paperwaster.web.blueprints import page

# gunicorn -b 0.0.0.0:5000 --access-logfile - --reload "paperwaster.web.app:create_app()""
def create_app(config_file=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('paperwaster.web.config.settings')
    app.config.from_pyfile('settings.py', silent=True)
    if config_file:
        logger.debug('Loading config from {}'.format(config_file))
        config = yaml.safe_load(open(config_file))
        app.config.update(config['web'])

    app.register_blueprint(page)
    app.register_blueprint(api)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    extensions(app)

    return app

def extensions(app):
    db.init_app(app)
    red.init_app(app)
    lm.init_app(app)
    limiter.init_app(app)

import paperwaster.models
