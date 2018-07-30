import os
from flask import render_template, session, redirect, url_for, request, flash
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if 'credentials' not in session:
        return redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    # This may be moved to a seperate view
    # Initialize the Google API
    service = googleapiclient.discovery.build(
        app.config['API_SERVICE_NAME'],
        app.config['API_VERSION'],
        credentials=credentials
    )

    session['credentials'] = credentials_to_dict(credentials)

    # Pull values from spreadsheet
    results = service.spreadsheets().values().get(
        spreadsheetId='11nf3AlDsj_E53rlmReC1cq4nevIg8quGpn46tR2MwSs',
        range='A1:I5',
        majorDimension='ROWS'
    ).execute()

    # Display a sample result
    return results['values'][0][0]


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.config['CLIENT_SECRETS_FILE'], scopes=app.config['SCOPES'])

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='false')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.config['CLIENT_SECRETS_FILE'],
        app.config['SCOPES'],
        state=state
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('login'))


# TODO: This doesn't seem to be working. Able to call API afterward w/o logging in.
@app.route('/logout')
def logout():
    if 'credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        flash('Credentials successfully revoked.')
        return render_template('index.html')
    else:
        flash('An error occurred.')
        return render_template('index.html')

@app.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    flash ('Credentials have been cleared.')
    return render_template('index.html')



def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
            }