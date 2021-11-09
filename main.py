from O365 import Account, Connection
import email
import imaplib
import os
import getpass
import time
from datetime import datetime
import requests
import json
import base64
requests.packages.urllib3.disable_warnings() # suppress SSL certificate warnings when ssl_verify=False

def microsoftOutlook():
    print("\n")
    print("Logs")
    print('_' * 10)
    ## OAUTH authentication
    # the default protocol will be Microsoft Graph
    # the default authentication method will be "on behalf of a user"
    credentials = (registration_clientID, registration_clientSecret)
    account = Account(credentials)
    if account.authenticate(scopes=['Mail.ReadWrite', 'offline_access', 'User.Read']):   
        mailbox = account.mailbox()
        folder = mailbox.get_folder(folder_name=sync_folder)
        query = folder.new_query().on_attribute('subject').contains(sync_subjectCriteria)

        while 1:
            now = datetime.now()
            print(now.strftime("%d/%m/%Y %H:%M:%S") + ": Checking for new mail")
            messages = folder.get_messages(query=query, download_attachments=True)
            for message in messages:
                if not (message.is_read) and (message.has_attachments):
                    for att in message.attachments:
                        if '.csv' in att.name:
                            print(now.strftime("%d/%m/%Y %H:%M:%S") + ": " + 'Downloading "{fileName}" from email titled "{subject}" received on the "{dateReceived}".'.format(fileName=att.name, subject=message.subject, dateReceived=message.received))
                            request_cookie = {'UserSession': (api_Cookie.decode('utf-8'))}
                            request_file = {'file': (base64.b64decode(att.content))}
                            request_value = {'category': api_inventoryCategoryId}
                            response = requests.post(api_endpoint, cookies=request_cookie, files=request_file, data=request_value, verify=False)
                            print (now.strftime("%d/%m/%Y %H:%M:%S") + ": Data Imported " + str(response.content.decode('utf-8')))  
                    message.mark_as_read()
            Connection.refresh_token                
            time.sleep(sync_frequency)

def imapServer():
    print("\n")
    print("Logs")
    print('_' * 10)
    ## Mail fetch and download
    while 1: ## repeat every x seconds
        now = datetime.now()
        mail = imaplib.IMAP4_SSL(mail_host)
        print(now.strftime("%d/%m/%Y %H:%M:%S") + ": " + str(mail.welcome.decode('utf-8')))
        mail.login(mail_login, mail_pass)
        mail.select(sync_folder)
        type, data = mail.search(None, '(UNSEEN SUBJECT "' + sync_subjectCriteria +'")')
        mail_ids = data[0]
        id_list = mail_ids.split()

        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)' )
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8') # converts byte literal to string removing b''
            email_message = email.message_from_string(raw_email_string)
                
            for part in email_message.walk(): # downloading attachments
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                if '.csv' in fileName:
                    subject = str(email_message).split("Subject: ", 1)[1].split("\n", 1)[0]
                    dateReceived = str(email_message).split("Date: ", 1)[1].split("\n", 1)[0]
                    print(now.strftime("%d/%m/%Y %H:%M:%S") + ": " + 'Downloaded "{file}" from email titled "{subject}" received on the "{dateReceived}".'.format(file=fileName, subject=subject, dateReceived=dateReceived))
    
                    request_cookie = {'UserSession': (api_Cookie.decode('utf-8'))}
                    request_file = {'file': part.get_payload(decode=True)}
                    request_value = {'category': api_inventoryCategoryId}

                    response = requests.post(api_endpoint, cookies=request_cookie, files=request_file, data=request_value, verify=False)
                    print (now.strftime("%d/%m/%Y %H:%M:%S") + ": Data Imported " + str(response.content.decode('utf-8')))
        mail.logout()
        time.sleep(sync_frequency)

print("See README for usage instructions")
## Preconfiguration steps
print("\n")
print("Sync Settings")
print('_' * 10)
sync_frequency = int(input("Mail Sync Frequency (s): "))
sync_folder = input("Mail Server Folder Name: ")
sync_subjectCriteria  = input("Subject Criteria: ")
print("\n")
print("API Settings")
print('_' * 10)
api_endpoint = input("API Host: ") + '/api/inventory/import.php'
api_sessionKey = getpass.getpass(prompt='API Session Key: ')
api_inventoryCategoryId = int(input("Inventory Category ID: "))
## Creation of cookie for WebIMS auth
api_Cookie_json = []
api_Cookie_json.append({"SessionId":api_sessionKey})
api_Cookie = base64.b64encode(str(json.dumps(api_Cookie_json[0])).encode('ascii'))

print("\n")
print("Mailbox Type")
print('_' * 10)
mailbox_type = input("Mailbox Type (1 - IMAP, 2 - Microsoft Outlook): ")
if mailbox_type == '1':
    print("\n")
    print("IMAP Server Settings")
    print('_' * 10)
    mail_host = input("Mail Server: ")
    mail_login = input("Username: ")
    mail_pass = getpass.getpass()
    imapServer()
if mailbox_type == '2':
    print("\n")
    print("Application Registration")
    print('_' * 10)
    registration_clientID = input("Client ID: ")
    registration_clientSecret = getpass.getpass(prompt='Client Secret: ')
    microsoftOutlook()