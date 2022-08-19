# -*- coding: utf-8 -*-

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import URLSafeTimedSerializer, BadSignature
from wtforms import Form, PasswordField, validators, StringField


class ItsdangerousSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None):
        def on_update(self_context):
            self_context.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.modified = False


class ItsdangerousSessionInterface(SessionInterface):
    #: the salt that should be applied in config as SESSION_SALT option for the
    #: signing of cookie based sessions.
    salt = ''
    session_class = ItsdangerousSession

    def get_serializer(self, app):
        if not app.secret_key:
            return None
        return URLSafeTimedSerializer(app.secret_key, salt=self.salt)

    def open_session(self, app, request_context):
        s = self.get_serializer(app)
        if s is None:
            return None
        val = request_context.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session_context, response):
        domain = self.get_cookie_domain(app)
        if not session_context:
            if session_context.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        expires = self.get_expiration_time(app, session_context)
        val = self.get_serializer(app).dumps(dict(session_context))
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires, httponly=True,
                            domain=domain)


class LoginForm(Form):
    login = StringField('Login', [validators.Length(min=2, max=25)])
    password = PasswordField('Password', [validators.Length(min=6, max=256)])
