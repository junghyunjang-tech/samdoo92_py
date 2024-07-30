import requests
import time
import os

# 생성된 talk의 ID
talk_id = "tlk_TAq4lE6uzNnKz-Z-Ae8gj"  # 생성된 ID로 대체하세요

url = f"https://api.d-id.com/talks/{talk_id}"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik53ek53TmV1R3ptcFZTQjNVZ0J4ZyJ9.eyJodHRwczovL2QtaWQuY29tL2ZlYXR1cmVzIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9zdHJpcGVfcHJvZHVjdF9pZCI6InByb2RfTHpsZmVjaUdaaVpLTG0iLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9jdXN0b21lcl9pZCI6ImN1c19RWWFLR09JNlpvTzNnOSIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3Byb2R1Y3RfbmFtZSI6InByby1tb250aC02MCIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3N1YnNjcmlwdGlvbl9pZCI6InN1Yl8xUGhUOXlKeEVLWjJ6QXluNWVJUE5uTkkiLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9iaWxsaW5nX2ludGVydmFsIjoibW9udGgiLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9wbGFuX2dyb3VwIjoiZGVpZC1wcm8iLCJodHRwczovL2QtaWQuY29tL3N0cmlwZV9wcmljZV9pZCI6InByaWNlXzFOazNzSkp4RUtaMnpBeW5lanZwcTBweCIsImh0dHBzOi8vZC1pZC5jb20vc3RyaXBlX3ByaWNlX2NyZWRpdHMiOiI2MCIsImh0dHBzOi8vZC1pZC5jb20vY2hhdF9zdHJpcGVfc3Vic2NyaXB0aW9uX2lkIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9jaGF0X3N0cmlwZV9wcmljZV9jcmVkaXRzIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9jaGF0X3N0cmlwZV9wcmljZV9pZCI6IiIsImh0dHBzOi8vZC1pZC5jb20vcHJvdmlkZXIiOiJnb29nbGUtb2F1dGgyIiwiaHR0cHM6Ly9kLWlkLmNvbS9pc19uZXciOmZhbHNlLCJodHRwczovL2QtaWQuY29tL2FwaV9rZXlfbW9kaWZpZWRfYXQiOiIyMDI0LTA3LTI4VDA5OjEzOjA0LjI0MFoiLCJodHRwczovL2QtaWQuY29tL29yZ19pZCI6IiIsImh0dHBzOi8vZC1pZC5jb20vYXBwc192aXNpdGVkIjpbIlN0dWRpbyJdLCJodHRwczovL2QtaWQuY29tL2N4X2xvZ2ljX2lkIjoiIiwiaHR0cHM6Ly9kLWlkLmNvbS9jcmVhdGlvbl90aW1lc3RhbXAiOiIyMDI0LTA3LTI2VDE2OjU3OjUzLjYxNloiLCJodHRwczovL2QtaWQuY29tL2FwaV9nYXRld2F5X2tleV9pZCI6InU0eWVhaWlhYTIiLCJodHRwczovL2QtaWQuY29tL3VzYWdlX2lkZW50aWZpZXJfa2V5IjoidXNnXzUydmptTjhGTVhrbDVYVi1WaEp3VyIsImh0dHBzOi8vZC1pZC5jb20vaGFzaF9rZXkiOiJmdHFsM1k1MmFsdUkybC1aN29aR1oiLCJodHRwczovL2QtaWQuY29tL3ByaW1hcnkiOnRydWUsImh0dHBzOi8vZC1pZC5jb20vZW1haWwiOiJ5b24ycGFuZ0BnbWFpbC5jb20iLCJodHRwczovL2QtaWQuY29tL3BheW1lbnRfcHJvdmlkZXIiOiJzdHJpcGUiLCJpc3MiOiJodHRwczovL2F1dGguZC1pZC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDI1MDE0NjQ1NTQwMDI3NjUwMDAiLCJhdWQiOlsiaHR0cHM6Ly9kLWlkLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kLWlkLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MjIyMzAyNTksImV4cCI6MTcyMjMxNjY1OSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCByZWFkOmN1cnJlbnRfdXNlciB1cGRhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoiR3pyTkkxT3JlOUZNM0VlRFJmM20zejNUU3cwSmxSWXEifQ.X7bd_uydyJTlQysx1wLqKAtxKvyFUhLdHEmREeSo2nikv0H-OwTdxB6xz_Ma0kF1Nmdo3IBNWmCQfxIx8BuoGUTzxOTdBnrJ5-jL5oLHHco2R-kREYhMebsRqkzxJy467ezASFvghM2rSvaJuXc3bpeJcAfHOP-dMM6QyfObAzvdStj0DqOUgmd9I05KuN4o0ciWdk5q8aL0KbH82MOFhJu9A7oqx-TeC48nCHhGeYyJ7Bvn4LRY-9zx3pBVwkTpMnLWdq3o4psPSEXUpeHJjwQczIAHjEtoEwrLR9-IgjkyaytsmfoXMLDym6PaKIhe1DWUuF-N6MheRem0W9OerQ"
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
