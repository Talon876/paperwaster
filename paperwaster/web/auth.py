import json
import time
from flask import url_for, request, redirect, current_app, flash
from rauth import OAuth2Service

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH'][provider_name]
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('page.oauth_callback', provider=self.provider_name,
                        _external=True, _scheme=current_app.config['SCHEME'])

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_cls in cls.__subclasses__():
                provider = provider_cls()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]

class TwitchSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitchSignIn, self).__init__('twitch')
        self.service = OAuth2Service(
            name='twitch',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url='https://api.twitch.tv/kraken/oauth2/authorize',
            access_token_url='https://api.twitch.tv/kraken/oauth2/token',
            base_url='https://api.twitch.tv/',
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='',
            response_type='code',
            redirect_uri=self.get_callback_url(),
        ))

    def callback(self):
        if 'code' not in request.args:
            flash('Failed to login', 'warning')
            return None
        oauth_session = self.service.get_auth_session(data={
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_callback_url(),
        }, decoder=json.loads)

        me = oauth_session.get('/kraken', headers={
            'Authorization': 'OAuth {}'.format(oauth_session.access_token),
            'Accept': 'application/vnd.twitchtv.v5+json',
        }, bearer_auth=False).json()
        return me['token']['user_name']
