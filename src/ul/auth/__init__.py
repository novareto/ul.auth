# -*- coding: utf-8 -*-

from zope.interface import Interface, implementer
from cromlech.security import Principal, unauthenticated_principal


unauthenticated_principal.roles = set()
unauthenticated_principal.permissions = set()


class Principal(Principal):

    def __init__(self, id, **attrs):
        self.id = id
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
