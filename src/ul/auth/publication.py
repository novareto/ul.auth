# -*- coding: utf-8 -*-

from .utils import security_check as component_protector
from . import Principal, Interaction, unauthenticated_principal

from cromlech.dawnlight import DawnlightPublisher
from cromlech.dawnlight import ViewLookup, view_locator, query_view
from ul.browser.publication import Publication, base_model_lookup
from cromlech.browser import getSession
from zope.security.proxy import removeSecurityProxy


secured_view = ViewLookup(component_protector(view_locator(query_view)))


class SecurePublication(Publication):

    layers = None

    def get_publisher(
            self, view_lookup=secured_view, model_lookup=base_model_lookup):
        publisher = DawnlightPublisher(model_lookup, view_lookup)
        return publisher.publish

    def get_credentials(self, environ):
        session = getSession()
        user = environ.get('REMOTE_USER') or session.get('username')
        return user

    def principal_factory(self, username):
        if username:
            return Principal(id=username)
        return unauthenticated_principal

    def publish_traverse(self, request, site):
        user = self.get_credentials(request.environment)
        request.principal = self.principal_factory(user)
        with Interaction(request.principal):
            response = self.publish(request, site)
            response = removeSecurityProxy(response)
            return response
