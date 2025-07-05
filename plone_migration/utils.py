import requests
import json
from urllib.parse import urlparse, urlunparse
import time

def GetToken(url, login, password):
    # Extrai a base da URL usando urllib
    parsed = urlparse(url)
    url_base = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))

    # Ajuste para ambiente .rke.codataprd
    if ".rke.codataprd" in parsed.netloc and parsed.path.strip("/"):
        first_path = "/" + parsed.path.strip("/").split("/")[0]
        url_login = url_base + first_path + "/@login"
    else:
        url_login = url_base + "/@login"

    payload = json.dumps({
        "login": login,
        "password": password
    })
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url_login, headers=headers, data=payload,timeout=60)

    print(response.text)

    data = response.json()

    return data['token']

def GetDataObject(token, obj):
    payload = ""
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    for tentativa in range(3):  # 1 tentativa + 2 retries
        try:
            response = requests.request("GET", obj, headers=headers, data=payload, timeout=60)
            return response
        except Exception as e:
            if tentativa < 2:
                time.sleep(2)
                continue
            else:
                raise

def GetFile(url, token):
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    for tentativa in range(3):  # 1 tentativa + 2 retries
        try:
            response = requests.request("GET", url, headers=headers, data=payload, timeout=60)
            return response
        except Exception as e:
            if tentativa < 2:
                time.sleep(2)


