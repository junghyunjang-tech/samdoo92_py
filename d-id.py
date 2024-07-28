import requests

url = "https://api.d-id.com/talks"

payload = {
    "script": {
        "type": "text",
        "subtitles": "false",
        "provider": {
            "type": "microsoft",
            "voice_id": "en-US-JennyNeural"
        }
    },
    "config": {
        "fluent": "false",
        "pad_audio": "0.0"
    }
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer amhqYW5nMDUwMUBnbWFpbC5jb20:V6v45M2CJHf-iU-XybXHd"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)