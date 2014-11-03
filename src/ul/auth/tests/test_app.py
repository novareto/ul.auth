# -*- coding: utf-8 -*-

import pytest
import transaction
from cromlech.browser import ILayout
from cromlech.browser import getSession, ILayout, IRequest
from cromlech.wsgistate import session_wrapper, WsgistateSession
from grokcore.component import adapter, implementer
from grokcore.component import testing
from ul.auth.app import AuthMiddleware
from infrae.testbrowser.browser import Browser
from zope.component import provideAdapter
from zope.configuration.config import ConfigurationMachine
from zope.interface import Interface


users = {
    'admin': 'admin',
    'user': 'test',
    }


SESSION_KEY = 'sk'


def session_middleware(app):
    def app_caller(environ, start_response):
        with transaction.manager as tm:
            with WsgistateSession(environ, SESSION_KEY, tm):
                return app(environ, start_response)
    return session_wrapper(app_caller, session_key=SESSION_KEY)
    

def echo_layout(view, request):
    def renderer(content, **layout_environ):
        return content
    return renderer
    

def setup_module(module):
    config = ConfigurationMachine()
    testing.grok('grokcore.component.meta')
    testing.grok('dolmen.forms.base')
    testing.grok('dolmen.forms.ztk')
    testing.grok('dolmen.view.meta')
    testing.grok('ul.browser')
    testing.grok('ul.auth.browser')
    config.execute_actions()
    provideAdapter(echo_layout, (IRequest, Interface), ILayout, name='')


def test_middleware():

    def application(environ, start_response):
        session = getSession()
        counter = session.setdefault('counter', 0)
        counter = session['counter'] = counter + 1
        body = str('Called %d times !' % counter)
        headers = [('Content-Type', 'text/html; charset=utf8'),
                    ('Content-Length', str(len(body)))]
        start_response('200 OK', headers)
        return [body]

    # we make sure the session is working
    wrapped = session_middleware(application)
    browser = Browser(wrapped)

    browser.open('/')
    assert browser.contents == 'Called 1 times !'

    browser.open('/')
    assert browser.contents == 'Called 2 times !'

    browser.open('/')
    assert browser.contents == 'Called 3 times !'

    # now, we add the auth
    wrapped = session_middleware(AuthMiddleware(users, 'TEST')(application))
    browser = Browser(wrapped)

    # The form is here
    browser.open('/')
    assert 'form.field.username' in browser.contents

    # We authenticate wrongly
    form = browser.get_form(id='form')
    username = form.get_control('form.field.username')
    password = form.get_control('form.field.password')
    username.value = 'wrong'
    password.value = 'access'
    
    assert form.get_control('form.action.login').click() == 200

    # The form shows up again because it was wrong
    assert 'form.field.username' in browser.contents
    form = browser.get_form(id='form')
    username = form.get_control('form.field.username')
    password = form.get_control('form.field.password')
    username.value = 'user'
    password.value = 'test'
    assert form.get_control('form.action.login').click() == 200

    # The content is now displayed
    # assert browser.contents == ''
