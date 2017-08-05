import datetime as dt
from flask import Blueprint, request, render_template, redirect, url_for, g, flash, current_app, jsonify
from flask_login import login_user, logout_user, current_user, login_required

from paperwaster.web.app import db, red, logger, lm
from paperwaster.web.auth import OAuthSignIn
from paperwaster.models import User, Message
from paperwaster import publish, publish_message, publish_image_code, parse_message

page = Blueprint('page', __name__)

@page.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = dt.datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@page.context_processor
def inject_template_vars():
    return {
        'debug': current_app.config.get('DEBUG', False)
    }

@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))

@page.route('/')
def index():
    return render_template('index.html', title='Home',
                           show_stream=request.args.get('stream')!='no')

@page.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Your Profile')

@page.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('page.index'))

@page.route('/authorize/<provider>')
def authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@page.route('/callback/<provider>')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    social_username = oauth.callback()
    if not social_username:
        flash('Login failed', 'danger')
        return redirect(url_for('page.index'))

    user = User.query.filter_by(twitch_id=social_username).first()
    if not user:
        user = User(twitch_id=social_username, nickname=social_username)
        logger.info('Adding new user {}'.format(user))
        db.session.add(user)
        db.session.commit()
    user.last_login = dt.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('page.index'))


@page.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    if data and data.get('msg'):
        logger.info('Sending {} to printer'.format(data['msg'].encode('ascii', 'ignore')))
        publish_message(data['msg'], font='hack', size=28, r=red)
    return jsonify({}), 200

@page.route('/send-image', methods=['POST'])
def send_image():
    data = request.get_json()
    if data and data.get('code'):
        logger.info('Sending image code {} to printer'.format(data['code'].encode('ascii', 'ignore')))
        publish_image_code(data['code'], r=red)
    return jsonify({}), 200
