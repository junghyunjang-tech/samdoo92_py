import requests

url = "https://api.heygen.com/v2/video/generate"

payload = {
    "test": True,
    "caption": False,
    "dimension": {
        "width": 1920,
        "height": 1080
    },
    "video_inputs": [
        {
            "type": "avatar",
            "text": "Hello, this is a test video.",
            "gender": "male",
            "skintone": "light",
            "voice": {
                "type": "text",
                "text_voice_id": "en_us_male_1"  # 'voice_id' 대신 'text_voice_id' 사용
            },
            "title": "Test Video"
        }
    ]
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": "ZTM1ODVkZDk2YjdhNGRhM2IxN2Y4ZmMzN2U1NWVmMzktMTcyMTg2ODc0Nw=="
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
