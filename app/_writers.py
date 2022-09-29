from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime


def writeAverages(jsonData, tab):
    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    spreadsheet_id = '11-DCc6jBqsNfSMFqzxSvN7RFxk2R-EVpzAh2kLIMcyM'
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    clearRange = tab + "!A:D"
    headersRange = tab + "!A1:D1"
    tsRange = tab + "!F1:G1"

    # First clear existing
    sheet.values().clear(spreadsheetId=spreadsheet_id, range=clearRange).execute()

    # Now the headers
    values = [
        ['Location', 'Ambient', 'Chilled', 'Frozen'],
    ]
    data = {'values': values}
    sheet.values().update(spreadsheetId=spreadsheet_id, body=data, range=headersRange,
                          valueInputOption='USER_ENTERED').execute()

    # Now the full data
    values = []
    outCount = 0
    for mfc in jsonData:
        ambient = jsonData[mfc]['Ambient']
        chilled = jsonData[mfc]['Chilled']
        frozen = jsonData[mfc]['Frozen']
        values.append([mfc, ambient, chilled, frozen])
        outCount = outCount + 1

    dataRange = tab + "!A2:D" + str(outCount + 1)

    data = {'values': values}
    sheet.values().update(spreadsheetId=spreadsheet_id, body=data, range=dataRange,
                          valueInputOption='USER_ENTERED').execute()

    # Then the timestamp
    timestamp = datetime.datetime.now().strftime("%d-%b-%Y, %H:%M:%S")
    values = [
        ["Last updated at:", timestamp]
    ]
    data = {'values': values}
    sheet.values().update(spreadsheetId=spreadsheet_id, body=data, range=tsRange,
                          valueInputOption='USER_ENTERED').execute()


def writeHistoric(jsonData, howFarBack, tab):
    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    spreadsheet_id = '11-DCc6jBqsNfSMFqzxSvN7RFxk2R-EVpzAh2kLIMcyM'
    service = build('sheets', 'v4', credentials=creds)

    # determine the date range
    bookends = jsonData['Bookends']
    itr = 0
    for mfc in bookends:
        if itr == 0:
            earliest = bookends[mfc]['Earliest']
            latest = bookends[mfc]['Latest']
            itr = itr + 1
        else:
            if bookends[mfc]['Earliest'] < earliest:
                earliest = bookends[mfc]['Earliest']
            if bookends[mfc]['Latest'] < latest:
                latest = bookends[mfc]['Latest']

    cutoff = latest - datetime.timedelta(days=howFarBack)

    if cutoff < earliest:
        cutoff = earliest

    diff = (latest - earliest).days
    diff = diff + 1
    finalCol = num_to_col_letters(diff)

    # Define ranges and headers
    sheet = service.spreadsheets()
    clearRange = tab + "!A:" + finalCol
    headersRange = tab + "!A1:" + finalCol + "1"
    innerValues = ['Location']
    dateItr = cutoff
    while dateItr <= latest:
        innerValues.append(dateItr.strftime("%d-%b"))
        dateItr = dateItr + datetime.timedelta(days=1)
    values = [
        innerValues,
    ]

    # Now clear existing
    sheet.values().clear(spreadsheetId=spreadsheet_id, range=clearRange).execute()

    # Now print the headers
    data = {'values': values}
    sheet.values().update(spreadsheetId=spreadsheet_id, body=data, range=headersRange,
                          valueInputOption='USER_ENTERED').execute()

    # Now the full data
    output = jsonData['Data']
    values = []
    outCount = 0
    for mfc in output:
        innerValues = [mfc]
        dateItr = cutoff
        vals = output[mfc]
        while dateItr <= latest:
            if dateItr in vals:
                innerValues.append(vals[dateItr][tab])
            else:
                innerValues.append('')
            dateItr = dateItr + datetime.timedelta(days=1)

        values.append(innerValues)
        outCount = outCount + 1

    dataRange = tab + "!A2:" + finalCol + str(outCount + 1)

    data = {'values': values}
    sheet.values().update(spreadsheetId=spreadsheet_id, body=data, range=dataRange,
                          valueInputOption='USER_ENTERED').execute()


def num_to_col_letters(num):
    letters = ''
    while num:
        mod = (num - 1) % 26
        letters += chr(mod + 65)
        num = (num - 1) // 26
    return ''.join(reversed(letters))