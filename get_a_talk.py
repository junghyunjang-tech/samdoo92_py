import requests
import time
import os

# 생성된 talk의 ID
talk_id = "tlk_Smml45RinCzkmtA4nMrhD"  # 생성된 ID로 대체하세요

url = f"https://api.d-id.com/talks/{talk_id}"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic bmljZS5pbmp1bmdAZ21haWwuY29t:2bDufGkqPavr-otW4Z23x"
}

talk_url = f"https://api.d-id.com/talks/{talk_id}"
video_dir = 'static/videos'
video_path = os.path.join(video_dir, "output_video.mp4")

# 이미 파일이 존재하는지 확인
if os.path.exists(video_path):
    os.remove(video_path)  # 기존 파일 삭제

# 비디오 파일 다운로드 루프
while True:
    response = requests.get(talk_url, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        talk_info = response.json()
        video_url = talk_info.get('result_url')
        if video_url:
            video_response = requests.get(video_url)
            if video_response.status_code == 200 or video_response.status_code == 201:
                with open(video_path, "wb") as file:
                    file.write(video_response.content)
                print("Video downloaded successfully.")
                break
            else:
                print(f"Failed to download video. Status code: {video_response.status_code}")
                break
        else:
            print("Video URL not available yet. Retrying in 10 seconds...")
            time.sleep(10)
    else:
        print(f"Failed to get talk info. Status code: {response.status_code}")
        break
