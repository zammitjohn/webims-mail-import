from datetime import datetime
import requests
import json
requests.packages.urllib3.disable_warnings() # suppress SSL certificate warnings when ssl_verify=False

def inventory_mail_import(endpoint, categoryId, sessionId, file):
    now = datetime.now()
    
    post_body_json = json.loads('{}')
    post_body_json.update({"sessionId":sessionId})
    post_body_json.update({"file":file})
    post_body_json.update({"category":categoryId})
    post_body_json.update({"isBase64EncodedContent":"1"})
    
    response = requests.post(endpoint, json=post_body_json, verify=False)

    if response.status_code == 200:
        print (now.strftime("%d/%m/%Y %H:%M:%S") + ": Data Imported " + str(response.content.decode('utf-8')))   
    else:
        print (now.strftime("%d/%m/%Y %H:%M:%S") + ": Failed to import!") 