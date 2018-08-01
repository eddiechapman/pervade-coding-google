import os
from flask import render_template, session, redirect, url_for, request, flash
import requests
from datetime import datetime
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from app import app
from app.forms import CodingForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if 'credentials' not in session:
        return redirect('authorize')
    return redirect('coding')


@app.route('/coding', methods=['GET', 'POST'])
def coding():
    if 'credentials' not in session:
        return redirect('authorize')

    if 'current_row' not in session:
        session['current_row'] = 2

    service = initialize_api()
    results = request_award_data(service)
    award = sort_results(results)
    form = CodingForm()

    if request.method == 'POST':
        write_coding_data(service, form)
        session['current_row'] += 1
        flash('Coding data submitted for award' + award['title'])
        return redirect(url_for('coding'))

    return render_template('coding.html', award=award, form=form)


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


def initialize_api():
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    service = googleapiclient.discovery.build(
        app.config['API_SERVICE_NAME'],
        app.config['API_VERSION'],
        credentials=credentials
    )
    session['credentials'] = credentials_to_dict(credentials)

    return service


def request_award_data(service):
    # Set request variables
    spreadsheet_id = app.config['SPREADSHEET_ID']
    header_range = app.config['HEADER_ROW']
    current_range = current_read_range()
    ranges = [header_range, current_range]
    major_dimension = app.config['MAJOR_DIMENSION']

    # Call API with request variables
    request_read = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges,
        majorDimension=major_dimension
    )
    results = request_read.execute()

    return results


def sort_results(results):
    award = {}
    column_names = results['valueRanges'][0]['values'][0]
    current_row = results['valueRanges'][1]['values'][0]
    for name, cell in zip(column_names, current_row):
        award[name] = cell

    return award


def current_read_range():
    return 'Sheet1!A{0}:{1}{0}'.format(
        session['current_row'],
        app.config['COLUMN_READ_END']
    )

def current_write_range():
    return 'Sheet1!{1}{0}:{2}{0}'.format(
        session['current_row'],
        app.config['COLUMN_WRITE_START'],
        app.config['COLUMN_WRITE_END']
    )

def write_coding_data(service, form):
    # API request variables
    spreadsheet_id = app.config['SPREADSHEET_ID']
    range = current_write_range()
    major_dimension = app.config['MAJOR_DIMENSION']
    value_input_option = 'RAW'
    print(range)

    # Data to be written
    value_range_body = {
        "range": range,
        "majorDimension": major_dimension,
        "values": [[
            form.pervasive_data.data,
            form.data_science.data,
            form.big_data.data,
            form.case_study.data,
            form.data_synonyms.data,
            # Records current date and time in UTC standard format
            str(datetime.utcnow())
        ]]
    }
    # Send request
    request_write = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        valueInputOption=value_input_option,
        range=range,
        body=value_range_body
    )
    # Execute request
    response = request_write.execute()



