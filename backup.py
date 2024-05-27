import requests
import os
import subprocess

url = "https://engine.hyperbeam.com/v0/vm"

payload = {
    "hide_cursor": True,
    "quality": {"mode": "sharp"},
    "dark": True,
    "region": "NA",
    "timeout": {
        "absolute": 315360000,
        "inactive": 315360000,
        "offline": 315360000,
        "warning": 315360000,
    }
}
headers = {
    "Authorization": f"Bearer {os.getenv('CHILDREN')}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)

subprocess.run(["python", "main.py"])
