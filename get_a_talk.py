import requests
import time
import os

# 생성된 talk의 ID
talk_id = "tlk_Smml45RinCzkmtA4nMrhD"  # 생성된 ID로 대체하세요

url = f"https://api.d-id.com/talks/{talk_id}"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik53ek53TmV1R3ptcFZTQjNVZ0J4ZyJ9.eyJodHRwczovL2QtaWQuY29tL2ZlYXR1cmVzIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9zdHJpcGVfcHJvZHVjdF9pZCI6InByb2RfTHpsZmVjaUdaaVpLTG0iLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9jdXN0b21lcl9pZCI6ImN1c19RWkhhTXluSERJbXpnVCIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3Byb2R1Y3RfbmFtZSI6InByby1tb250aC02MCIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3N1YnNjcmlwdGlvbl9pZCI6InN1Yl8xUGk5MWhKeEVLWjJ6QXluWlNmWFAycjYiLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9iaWxsaW5nX2ludGVydmFsIjoibW9udGgiLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9wbGFuX2dyb3VwIjoiZGVpZC1wcm8iLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9wcmljZV9pZCI6InByaWNlXzFOazNzSkp4RUtaMnpBeW5lanZwcTBweCIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3ByaWNlX2NyZWRpdHMiOiI2MCIsImh0dHBzOi8vZC1pZC5jb20vY2hhdF9zdHJpcGVfc3Vic2NyaXB0aW9uX2lkIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9jaGF0X3N0cmlwZV9wcmljZV9jcmVkaXRzIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9jaGF0X3N0cmlwZV9wcmljZV9pZCI6IiIsImh0dHBzOi8vZC1pZC5jb20vcHJvdmlkZXIiOiJnb29nbGUtb2F1dGgyIiwiaHR0cHM6Ly9kLWlkLmNvbS9pc19uZXciOmZhbHNlLCJodHRwczovL2QtaWQuY29tL2FwaV9rZXlfbW9kaWZpZWRfYXQiOiIyMDI0LTA3LTMwVDA5OjA1OjM5LjY4NloiLCJodHRwczovL2QtaWQuY29tL29yZ19pZCI6IiIsImh0dHBzOi8vZC1pZC5jb20vYXBwc192aXNpdGVkIjpbIlN0dWRpbyIsIkNoYXQiXSwiaHR0cHM6Ly9kLWlkLmNvbS9jeF9sb2dpY19pZCI6IiIsImh0dHBzOi8vZC1pZC5jb20vY3JlYXRpb25fdGltZXN0YW1wIjoiMjAyNC0wNy0yNVQwOTo0NTo0NC4yMDRaIiwiaHR0cHM6Ly9kLWlkLmNvbS9hcGlfZ2F0ZXdheV9rZXlfaWQiOiJ2c251a215MXA0IiwiaHR0cHM6Ly9kLWlkLmNvbS91c2FnZV9pZGVudGlmaWVyX2tleSI6InVzZ19rVDIycGFjRmhhQ05GbEpEc1J3Q2QiLCJodHRwczovL2QtaWQuY29tL2hhc2hfa2V5IjoiY3dBLUdIZFg5WDAzSFo4ZzlpNGJaIiwiaHR0cHM6Ly9kLWlkLmNvbS9wcmltYXJ5Ijp0cnVlLCJodHRwczovL2QtaWQuY29tL2VtYWlsIjoibmljZS5pbmp1bmdAZ21haWwuY29tIiwiaHR0cHM6Ly9kLWlkLmNvbS9wYXltZW50X3Byb3ZpZGVyIjoic3RyaXBlIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmQtaWQuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA1NzkyNTQzODQyOTYyNTk0NTE3IiwiYXVkIjpbImh0dHBzOi8vZC1pZC51cy5hdXRoMC5jb20vYXBpL3YyLyIsImh0dHBzOi8vZC1pZC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzIyMzMwNDk4LCJleHAiOjE3MjI0MTY4OTgsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgcmVhZDpjdXJyZW50X3VzZXIgdXBkYXRlOmN1cnJlbnRfdXNlcl9tZXRhZGF0YSBvZmZsaW5lX2FjY2VzcyIsImF6cCI6Ikd6ck5JMU9yZTlGTTNFZURSZjNtM3ozVFN3MEpsUllxIn0.3tROUts52Nc0boTcRQ8keRM5vvzYLWDExa-QHiOJU1LSJIACoI-mMFCirMXVIUlxjCAY6Xmgt44_5XlD81Y8pBxkTtW8T35pIXGWd6tKoV2XFShKpwoTKYfWkxoblShomFjW6CahVxnrfHWbKgI6zTjlh18a1nkTh3kqsIffDf3vxmg5z4UEhaMWDBjlsBm62Y1GujQB0HyV2WfZdiWunDI8Vw5Ynx4ASQzErSNyWiDCIuAFeBNdOn0JBSAyK-6uQG2dcMdL1BNRl28t_phVIFczjsUC4GXK6X58Tam_0kA6xEOVBq7IKu8DvOOO_9JkVPqzYa3JH49HO-2l8md31g"
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
