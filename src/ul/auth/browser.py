# -*- coding: utf-8 -*-

from os import path
from .app import AuthMiddleware
from dolmen.template import TALTemplate
from grokcore.component import context, name
from ul.browser import Page


class Login(Page):
    context(AuthMiddleware)
    name('login')
    template = TALTemplate(path.join(path.dirname(__file__), 'login.cpt'))

    title = message = u"Please log in"
    action = ""

    def update(self):
        self.username = self.request.environment.get(
            self.context.environ_user_key, '')

        self.userfield = self.context.user_field
        self.pwdfield = self.context.pass_field
        self.button = self.context.button
