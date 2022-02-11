# importing the requests library
from email import header
import requests
from requests import get


url = "https://pfeifferassistant.duckdns.org/api/services/light/turn_on"
headers = {
    f"Authorization": "Bearer {LONG_LIVED_TOKEN}",
    "content-type": "application/json",
}
  
# data to be sent to api
data = '{"entity_id": "light.schreibtisch","rgb_color":[255,0,0]}'
  
# sending post request and saving response as response object
r = requests.post(url, headers=headers, data = data)
  
# extracting response text 
pastebin_url = r.text
print("URL:%s"%pastebin_url)