# -*- coding: utf-8 -*-

from . import _
from . import require, UserLoggedInEvent, Principal
from cromlech.browser import exceptions, getSession
from dolmen.forms.base import FAILURE, SuccessMarker, HIDDEN
from dolmen.forms.base import Fields, action
from grokcore.component import name, context
from ul.browser.components import Form
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
        title=_(u'Username'),
        required=True)

    password = Password(
        title=_(u"Password"),
        required=True)

    came_from = TextLine(
        title=_(u"Initial destination"),
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

    def credentials_managers(self):
        site = getSite()
        if site is not None:
            for credential in getattr(site, 'credentials', []):
                yield getUtility(ICredentials, name=credential)

    @action(_(u'Login'))
    def log_me(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE

        credendials_managers = list(self.credentials_managers())
        if credendials_managers is None:
            self.flash(_(u"Missing credentials."))
            return SuccessMarker('Login failed', False)

        for credentials_manager in credendials_managers:
            result = credentials_manager.log_in(self.request, **data)
            if isinstance(result, SuccessMarker):
                self.flash(result.name)
                return result
            elif result:
                session = getSession()
                session['username'] = data['username']
                self.flash(_(u"Login successful."))
                principal = self.make_principal(id=data['username'])
                self.request.principal = principal
                notify(UserLoggedInEvent(principal))
                camefrom = data.get('camefrom', self.url(self.context))
                return SuccessMarker(
                    'Login successful', True, url=camefrom,
                    code=302)

        self.flash(_(u'Login failed.'))
        return FAILURE
