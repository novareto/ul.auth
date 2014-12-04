# -*- coding: utf-8 -*-

from . import UserLoggedInEvent
from barrel import form
from cromlech.browser import IPublicationRoot
from cromlech.browser import getSession, IResponseFactory
from cromlech.security import Interaction
from cromlech.security import Principal
from cromlech.webob import Request
from dolmen.view import query_view
from webob.exc import HTTPTemporaryRedirect
from zope.event import notify
from zope.interface import implementer
from zope.location import Location


def do_logout(global_conf, session_key):
    def logout(environ, start_response):
        session = environ[session_key].session
        if session is not None:
            if 'user' in session:
                del session['user']
        response = HTTPTemporaryRedirect(location='/')
        return response(environ, start_response)
    return logout


@implementer(IPublicationRoot, IResponseFactory)
class AuthMiddleware(Location, form.FormAuth):
    """
    """
    session_user_key = "user"

    def __init__(self, users, realm):
        self.users = users
        self.realm = realm

    def valid_user(self, username, password):
        """Is this a valid username/password? (True or False)"""
        account = self.users.get(username, None)
        if account is not None and account.password == password:
            notify(UserLoggedInEvent(Principal(username)))
            return True
        return False

    def session_dict(self, environ):
        ses = getSession()
        return ses

    def save_session(self):
        pass 

    def not_authenticated(self, environ, start_response):
        """Respond to an unauthenticated request with a form.
        """
        request = Request(environ)
        view = query_view(request, self, name='login')
        if view is None:
            raise NotImplementedError

        with Interaction():
            response = view()
        return response(environ, start_response)

    def __call__(self, app):
        """If request is not from an authenticated user, complain.
        """
        def security_traverser(environ, start_response):
            if self.authenticate(environ):
                return app(environ, start_response)
            return self.not_authenticated(environ, start_response)
        return security_traverser
