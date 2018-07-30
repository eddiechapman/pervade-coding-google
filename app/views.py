import os
import flask
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from app import app

@app.route('/')
@app.route('/index')


@app.route('/login')
def login():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        app.config['API_SERVICE_NAME'], app.config['API_VERSION'], credentials
    )

    return render_template('coding.html', service=service)

