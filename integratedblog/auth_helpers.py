from datetime import datetime, timedelta
from flask import abort, current_app, request, session, url_for
from oauth2client.client import OAuth2WebServerFlow
import functools


SESSION_VARIABLES = ['admin_id', 'login_expiration']


def get_oauth2_flow():
    blog_data = current_app.config.get('BLOG_DATA')
    redirect_uri = request.url_root[:-1] + url_for('blog_pages.oauth2callback')
    return OAuth2WebServerFlow(client_id = blog_data['oauth_client_id'],
                               client_secret = blog_data['oauth_client_secret'],
                               scope = "email",
                               redirect_uri = redirect_uri)


""" Returns a tuple of login_succeeded (Boolean for whether email address is an
authorized email address), and email (email address string that Google OAuth
returned) """
def try_to_log_in_from_oauth2_callback(auth_code):
    credentials = get_oauth2_flow().step2_exchange(auth_code)
    email = credentials.id_token["email"]
    authorized_emails = current_app.config.get('BLOG_DATA')['authorized_emails']
    if email in authorized_emails:
        set_logged_in_admin(email)
        return True, email
    else:
        return False, email


# If not logged in, return False. Else, return the admin's email address.
def logged_in_admin():
    if (all([True if s in session else False for s in SESSION_VARIABLES]) and
        session['login_expiration'] > datetime.now()):
        return session['admin_id']
    else:
        clear_logged_in_admin()
        return False


def set_logged_in_admin(email):
    session['admin_id'] = email
    session['login_expiration'] = datetime.now() + timedelta(hours=5)


def clear_logged_in_admin():
    for variable in SESSION_VARIABLES:
        if variable in session:
            del session[variable]


# Login/authentication wrapper
def require_admin_login(f):
    @functools.wraps(f)
    def require_admin_login_wrapper(*args, **kwargs):
        if logged_in_admin():
            return f(*args, **kwargs)
        else:
            print "Someone tried to access %s while not logged in" % request.url_rule
            abort(404)
    return require_admin_login_wrapper
