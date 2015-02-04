# -*- coding: utf-8 -*-

from ul.browser.components import Form
from dolmen.forms.base import Fields, action
from grokcore.component import name, context
from . import require, UserLoggedInEvent, Principal

from cromlech.browser import exceptions, getSession
from dolmen.forms.base import SUCCESS, FAILURE, SuccessMarker, HIDDEN
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import Interface
from zope.schema import TextLine, Password


class ICredentials(Interface):

    def assert_credentials(username, password):
        """Returns a boolean
        """


class ILoginForm(Interface):

    username = TextLine(
        title=u'Username',
        required=True)

    password = Password(
        title=u"Password",
        required=True)

    came_from = TextLine(
        title=u"Initial destination",
        required=False)


class Login(Form):
    name('login')
    context(Interface)
    require('zope.Public')

    fields = Fields(ILoginForm)
    fields['came_from'].mode = HIDDEN
    fields['came_from'].ignoreRequest = False
    fields['username'].ignoreRequest = False

    ignoreRequest = True
    
    def make_principal(self, **kwargs):
        return Principal(**kwargs)

    def get_credentials_managers(self):
        site = getSite()
        credendials_managers = []
        if site is not None:
            for credential in getattr(site, 'credentials', []):
                # we need to handle lookup errors here
                utility = getUtility(ICredentials, name=credential)
                credendials_managers.append(utility)
        return credendials_managers

    @action(u'Login')
    def log_me(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE

        credendials_managers = self.get_credentials_managers()
        if credentials_managers is None:
            self.flash(u"Missing credentials.")
            return SuccessMarker('Login failed', False)

        for credentials_manager in credentials_managers:
            account = credentials_manager.log_in(**data)
            if account:
                session = getSession()
                session['username'] = data['username']
                self.flash(u"Login successful.")
                principal = self.make_principal(id=data['username'])
                self.request.principal = principal
                notify(UserLoggedInEvent(principal))
                camefrom = data.get('camefrom', self.url(self.context))
                return SuccessMarker(
                    'Login successful', True, url=camefrom,
                    code=302)

        self.flash(u'Login failed.')
        return FAILURE
