# -*- coding: utf-8 -*-

from . import require
from . import _
from cromlech.browser import exceptions
from grokcore.component import name, context
from ul.browser.components import Page


class UnauthorizedPage(Page):
    name('')
    context(exceptions.HTTPUnauthorized)
    require('zope.Public')

    def render(self):
        obj = self.context.__parent__
        self.flash(_(u"This page is protected and you're not allowed. Please login."))
        self.redirect(self.url(obj) + '/login?form.field.came_from=' + self.url(self.context.location))


class ForbiddenPage(Page):
    name('')
    context(exceptions.HTTPForbidden)
    require('zope.Public')

    def render(self):
        return _(u"This page is protected and you don't have the credentials.")
