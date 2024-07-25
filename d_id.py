import requests
import json

# D-ID API 엔드포인트
api_url = "https://api.d-id.com/v1/video"

# D-ID API 키
api_key = "amhqYW5nMDUwMUBnbWFpbC5jb20:KMSpc_ZRgWFlZsDn8Ygd0";

# 헤더
headers = {
    "Authorization": f"Bearer amhqYW5nMDUwMUBnbWFpbC5jb20:KMSpc_ZRgWFlZsDn8Ygd0",
    "Content-Type": "application/json"
}

# 비디오 생성 요청 데이터
payload = {
    "source_url": "https://example.com/image.jpg",  # 이미지 URL
    "script": {
        "type": "text",
        "input": "Hello, this is a test video."  # 스크립트 텍스트
    },
    "config": {
        "stitch": True
    }
}

# 요청 보내기
response = requests.post(api_url, headers=headers, data=json.dumps(payload))

# 응답 확인
if response.status_code == 200:
    video_data = response.json()
    video_url = video_data['video_url']
    print(f"Video URL: {video_url}")
else:
    print(f"Failed to create video: {response.status_code}")
    print(response.text)
