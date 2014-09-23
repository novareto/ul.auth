# -*- coding: utf-8 -*-

from .app import AuthMiddleware
from cromlech.browser import exceptions
from cromlech.security import unauthenticated_principal
from grokcore.security import permissions
from grokcore.security.interfaces import IRole
from zope.component import getUtility
from zope.security import canAccess
from zope.security.management import getInteraction
from zope.security.proxy import removeSecurityProxy


def secured(users, realm, middleware=AuthMiddleware):
    """Decorator to secure my apps with.
    """
    def deco(app):
        auth = middleware(users, realm)
        return auth(app)
    return deco


def getPermissionForRole(role):
    role = getUtility(IRole, role)
    return set(permissions.bind().get(role))


def security_check(lookup):
    def check(*args, **kwargs):
        component = lookup(*args, **kwargs)
        if component is not None:
            if canAccess(component, '__call__'):
                return removeSecurityProxy(component)
            else:
                interaction = getInteraction()
                principal = interaction.participations[0].principal
                if principal is unauthenticated_principal:
                    raise exceptions.HTTPUnauthorized(component)
                else:
                    raise exceptions.HTTPForbidden(component)
        return None
    return check

