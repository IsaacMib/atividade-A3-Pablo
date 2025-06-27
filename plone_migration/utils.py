import requests
import json
from urllib.parse import urlparse, urlunparse

def GetToken(url, login, password):
    # Extrai a base da URL usando urllib
    parsed = urlparse(url)
    url_base = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
    url_login = url_base + "/@login"

    payload = json.dumps({
        "login": login,
        "password": password
    })
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url_login, headers=headers, data=payload)

    print(response.text)

    data = response.json()

    return data['token']

def GetDataObject(token,obj):
  payload = ""
  headers = {
    'Authorization': 'Bearer '+token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
  response = requests.request("GET", obj, headers=headers, data=payload)

  return response

