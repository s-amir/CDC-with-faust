import time

import requests

url = "http://connect:8083/connectors/"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Load the JSON data from your request.json file
with open("request.json", "r") as file:
    data = file.read()

# Make the POST request
response = requests.post(url, headers=headers, data=data)
time.sleep(4)
