DEBUG = True


# Google Sheets API authentication variables
CLIENT_SECRETS_FILE = 'client_secret.json' or os.environ.get('CLIENT_SECRETS_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'

# Google Sheets API read/write variables
SPREADSHEET_ID = '11nf3AlDsj_E53rlmReC1cq4nevIg8quGpn46tR2MwSs'
HEADER_ROW = 'Sheet1!A1:Q1'
COLUMN_READ_END = 'Q'
COLUMN_WRITE_START = 'J'
COLUMN_WRITE_END = 'Q'
MAJOR_DIMENSION = 'ROWS'


