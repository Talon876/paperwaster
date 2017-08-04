from flask import Blueprint, request, render_template, redirect, url_for

from paperwaster.web.app import db, red, logger
from paperwaster import publish_message

page = Blueprint('page', __name__)

@page.route('/')
def index():
    return render_template('index.html')

@page.route('/send-message', methods=['POST'])
def send_message():
    msg = request.form.get('message')
    if msg:
        logger.info('Sending {} to printer'.format(msg.encode('ascii', 'ignore')))
        publish_message(msg, font='hack', size=28, r=red)
    return redirect(url_for('page.index'))
