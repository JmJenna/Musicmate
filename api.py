import requests
import base64
import json
import datetime

Client_ID = '3c6203e07eb94cb189e83be3799443cf'
Client_Secret = '18dc97d8bb574fec9b441c53ed1d1f2e' 

endpoint = "https://accounts.spotify.com/api/token"

# python 3.x version
encoded = base64.b64encode("{}:{}".format(Client_ID, Client_Secret).encode('utf-8')).decode('ascii')

headers = {"Authorization": "Basic {}".format(encoded)}

payload = {"grant_type": "client_credentials"}

response = requests.post(endpoint, data=payload, headers=headers)

access_token = json.loads(response.text)['access_token']

headers = {"Authorization": "Bearer {}".format(access_token)}

now = datetime.datetime.now()


## Spotify Search API

params = {
    "q": "blackpink",
    "type":"track",
    "limit": "1"
}

r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

rjson = r.json()

trac = rjson["tracks"]["items"]


playlist = requests.get("https://api.spotify.com/v1/playlists/6vDGVr652ztNWKZuHvsFvx",
                        headers={"Content-Type":"application/json", "Authorization": "Bearer {}".format(access_token)})

deepmusic_id = "6vDGVr652ztNWKZuHvsFvx"
user_id = "ptrchyq2nqqbzfg55mzghjre1m"


