# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ul.auth')

from zope.interface import Interface, implementer
from cromlech.security import Principal, unauthenticated_principal
from grokcore.security import require

# Convenient import
require

unauthenticated_principal.roles = set()
unauthenticated_principal.permissions = set()


class Principal(Principal):

    def __init__(self, **attrs):
        self.id = attrs.get('id', u'')
        self.title = attrs.get('title', u'')
        self.description = attrs.get('description', u'')
        self.roles = attrs.get('roles', set())
        self.permissions = attrs.get('permissions', set())


class IUserLoggedInEvent(Interface):
    """Event triggered when a user logged in.
    """


@implementer(IUserLoggedInEvent)
class UserLoggedInEvent(object):

    def __init__(self, principal):
        self.principal = principal


from .browser import ICredentials, ILoginForm, Login
from .publication import SecurePublication, secured_view
from .policy import GenericSecurityPolicy
