# -*- coding: utf-8 -*-

from .utils import getPermissionForRole
from zope.security.checker import CheckerPublic
from zope.security.simplepolicies import ParanoidSecurityPolicy


class GenericSecurityPolicy(ParanoidSecurityPolicy):
    public = frozenset(('zope.Public', CheckerPublic))

    @staticmethod
    def get_permissions(principal):
        permissions = principal.permissions
        for role in principal.roles:
            permissions |= getPermissionForRole(role)
        return permissions

    def checkPermission(self, permission, object):
        if permission in self.public:
            return True

        for participation in self.participations:
            permissions = self.get_permissions(participation.principal)
            if permission in permissions:
                return True
        return False
