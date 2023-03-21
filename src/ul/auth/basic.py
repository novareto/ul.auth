import string
import cgi
from cStringIO import StringIO


class BasicAuth(object):
    """HTTP Basic authentication middleware.

    Also the base class for other authentication methods.
    """

    session_key = 'barrel.session'
    session_user_key = 'barrel.user'
    realm = 'WSGIBarrel'
    users = None

    def __init__(self, app, users=None):
        """Take the app to wrap and optional settings."""
        self.app = app
        if users is not None:
            self.users = users
        elif self.users is None:
            self.users = []

    def valid_user(self, username, password):
        """Is this a valid username/password? (True or False)"""
        for usr, pwd in self.users:
            if username == usr and password == pwd:
                return True
        else:
            return False

    def session_dict(self, environ):
        """Get the session for caching username.

        The default place to look for a session is where
        flup puts it.
        """
        return environ.get(self.session_key)

    def save_session(self):
        """Save out the session.

        Replace with a do-nothing if you use a package that does
        not require you to explicitly save out sessions.
        """
        session = self.session_dict()
        if session is not None:
            return session.save()

    def cache_username(self, environ, username):
        """Store the username in a session dict if found.

        Also populates REMOTE_USER.
        """
        environ['REMOTE_USER'] = username
        session = self.session_dict(environ)
        if session is not None:
            session[self.session_user_key] = username

    def get_cached_username(self, environ):
        """Look for the username in the session if found.

        Also populates REMOTE_USER if it can.
        """
        session = self.session_dict(environ)
        if session is not None:
            return session.get(self.session_user_key)
        else:
            return None

    def username_and_password(self, environ):
        """Pull the creds from the AUTHORIZAITON header."""
        # Should I check the auth type here?
        auth_string = environ.get('HTTP_AUTHORIZATION')
        if auth_string is None:
            return ('', '')
        else:
            return auth_string[6:].strip().decode('base64').split(':')

    def authenticate(self, environ):
        """Is this request from an authenicated user? (True or False)"""
        username, password = self.username_and_password(environ)
        if username and password:
            if self.valid_user(username, password):
                self.cache_username(environ, username)
                return True
        else:
            username = self.get_cached_username(environ)
            if username is not None:
                self.cache_username(environ, username)
                return True

        return False

    def not_authenticated(self, environ, start_response):
        """Respond to an unauthenticated request with a 401."""
        start_response('401 Unauthorized',
                        [('WWW-Authenticate', 'Basic realm=' + self.realm)])
        return ["401 Unauthorized: Please provide credentials."]

    def __call__(self, environ, start_response):
        """If request is not from an authenticated user, complain."""
        if self.authenticate(environ):
            return self.app(environ, start_response)
            self.save_session()
        else:
            return self.not_authenticated(environ, start_response)


default_template = """<?xml version="1.0"?>
<!DOCTYPE html
  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
    <title>Form Auth</title>
</head>
<body>
    <h1>Resource Requires Authentication</h1>
    <form method="POST" action="">
        <fieldset>
            <legend>$message:</legend>
            <label for="$user_field">Username:</label>
            <input type="text"
                   name="$user_field"
                   id="$user_field"
                   value="$username"/>
            <br/>
            <label for="$pass_field">Password:</label>
            <input type="password" name="$pass_field" id="$pass_field"/>
            <br/>
            <button type="submit"
                    name="$button"
                    id="$button"
                    value="submit">Sign In</button>
        </fieldset>
    </form>
</body>
</html>"""


class FormAuth(BasicAuth):
    """Web Form authentication middleware."""

    user_field = 'username'
    pass_field = 'password'
    button = 'barrel-form-button'
    environ_user_key = 'barrel.form.username'

    first_message = "Please enter your username and password"
    failed_message = "Sign in failed; please try again"

    template = string.Template(default_template)

    def username_and_password(self, environ):
        """Pull the creds from the form encoded request body."""
        # How else can I tell if this is an auth request before reading?
        if environ.get('CONTENT_LENGTH'):
            clen = int(environ['CONTENT_LENGTH'])
            sio = StringIO(environ['wsgi.input'].read(clen))
            fs = cgi.FieldStorage(fp=sio,
                                  environ=environ,
                                  keep_blank_values=True)
            sio.seek(0)
            environ['wsgi.input'] = sio
            if fs.getlist(self.button):
                try:
                    username = fs[self.user_field].value
                    password = fs[self.pass_field].value
                    environ[self.environ_user_key] = username
                    return username, password
                except KeyError:
                    pass # silence

        return '', ''

    def not_authenticated(self, environ, start_response):
        """Respond to an unauthenticated request with a form."""
        start_response('200 OK', [('Content-Type', 'text/html')])
        username = environ.get(self.environ_user_key, '')
        if username:
            message = self.failed_message
        else:
            message = self.first_message
        return [self.template.safe_substitute(user_field=self.user_field,
                                              pass_field=self.pass_field,
                                              button=self.button,
                                              username=username,
                                              message=message,
                                              **environ)]
