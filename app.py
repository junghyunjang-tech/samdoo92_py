from flask import Flask, render_template, request, redirect, url_for, session, jsonify,send_file
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import re
import pandas as pd
from datetime import datetime
import requests
from pathlib import Path
# 환경 변수 로드
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
DID_KEY = os.getenv("DID_API_KEY")

print(API_KEY)

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

assistant_id = "asst_MxqorhgXLjXncMMQVnAJGbAY"

# 업로드된 파일을 저장할 폴더를 설정합니다.
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 초기 메시지 설정
initial_message = {
    "id": "initial",
    "role": "assistant",
    "content": [{"text": {"value": "안녕하세요. 나이스지니데이타 대표 김민수입니다. 면접 시작하겠습니다."}}]
}

def get_initial_messages():
    return [initial_message]

def serialize_message(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": [
            {"text": {"value": content_block.text.value}}
            for content_block in message.content if hasattr(content_block, 'text') and hasattr(content_block.text, 'value')
        ]
    }

def serialize_message_forRetreive(message):
    content_values = [block.text.value for block in message.content if hasattr(block, 'text') and hasattr(block.text, 'value')]
    return {
        "id": message.id,
        "role": message.role,
        "content": " ".join(content_values)
    }

def extract_text(data):
    extracted_data = []
    for message in data:
        for content in message['content']:
            text = content['text']['value']
            name_pattern = r"(?:안녕하세요|hello),\s*([가-힣a-zA-Z]+)님"
            score_pattern = r"\s*([\d.]+)/100"

            name_match = re.search(name_pattern, text)
            score_match = re.search(score_pattern, text)

            now = datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
            print("현재 날짜와 시간:", formatted_now)

            if name_match and score_match:
                name = name_match.group(1)
                score = float(score_match.group(1))
                extracted_data.append({"name": name, "score": score, "thread_id": session['thread_id'], "created_dt": formatted_now})
                print(f"이름: {name}, 평가 점수: {score}")
            else:
                print("이름 또는 평가 점수를 찾을 수 없습니다.")

    if 'extracted_data' in session:
        existing_thread_ids = {entry['thread_id'] for entry in session['extracted_data']}
        new_data = [entry for entry in extracted_data if entry['thread_id'] not in existing_thread_ids]
        session['extracted_data'].extend(new_data)
    else:
        session['extracted_data'] = extracted_data

    df = pd.DataFrame(session['extracted_data'])
    df['score'] = pd.to_numeric(df['score'])
    df_sorted = df.sort_values(by='score', ascending=False).reset_index(drop=True)
    df_sorted['rank'] = df_sorted.index + 1  # 순위 추가

    session['extracted_data'] = df_sorted.to_dict(orient='records')  # DataFrame을 딕셔너리로 변환하여 세션에 저장
    print("정렬된 데이터:", session['extracted_data'])  # 정렬된 데이터 출력

    return session['extracted_data']




@app.route('/')
def index():
    if 'reset_done' not in session:
        reset()
        return redirect(url_for('reset'))

    messages = session.get('messages', [])
    html = ''
    for item in messages:
        role_class = 'assistant' if item['role'] == 'assistant' else 'user'
        for content_block in item['content']:
            if 'text' in content_block and 'value' in content_block['text']:
                text_value = content_block['text']['value'].replace('&nbsp;', ' ')
                html += f'<div class="message {role_class}">{text_value}</div>\n'

    extracted_data = session.get('extracted_data', [])
    print("세션에 저장된 정렬된 데이터:", extracted_data)  # 세션 데이터 출력
    # Split threads by date
    today = datetime.now().strftime("%Y-%m-%d")
    today_threads = [thread for thread in extracted_data if thread['created_dt'][:10] == today]
    past_week_threads = [thread for thread in extracted_data if thread['created_dt'][:10] != today]

    return render_template('index.html', my_variable=html, today_threads=today_threads, past_week_threads=past_week_threads, extracted_data=extracted_data)
    # return render_template('index.html', my_variable=html, extracted_data=extracted_data)


@app.route('/reset', methods=['GET'])
def reset():
    # Reset messages and thread_id while keeping extracted_data and ranking
    extracted_data = session.get('extracted_data', [])
    ranking = session.get('ranking', [])
    if 'messages' in session:
        del session['messages']
    session['messages'] = get_initial_messages()
    thread = client.beta.threads.create()
    session['thread_id'] = thread.id
    reset_message = client.beta.threads.messages.create(
        session['thread_id'],
        role="assistant",
        content="안녕하세요. 나이스지니데이타 대표 김민수입니다. 면접 시작하겠습니다."
    )
    session['reset_done'] = True
    session['extracted_data'] = extracted_data  # Preserve extracted data
    session['ranking'] = ranking  # Preserve ranking data

    # 파일 삭제 경로 설정
    file_path = os.path.join('static', 'audio', 'speech.mp3')

    # 파일이 존재하면 삭제
    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for('index'))

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    thread_id = session.get('thread_id')

    if not thread_id:
        return redirect(url_for('index'))

    try:
        thread_message2 = client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        while run.status != "completed":
            print("status 확인 중", run.status)
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        messages = client.beta.threads.messages.list(thread_id=thread_id).data
        serialized_messages = [serialize_message(message) for message in messages]

        first_message = get_first_assistant_message_from_list(serialized_messages)

        file_path = os.path.join('static', 'audio', 'speech.mp3')

        # 파일이 존재하면 삭제
        if os.path.exists(file_path):
            os.remove(file_path)

        #speech_file_path를 /static/audio/speech.mp3로 설정
        base_path = Path(__file__).parent
        speech_file_path = base_path / "static" / "audio" / "speech.mp3"

        response = client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=first_message
        )
        response.stream_to_file(speech_file_path)

        print('serialized_messages', serialized_messages)
        if 'messages' in session:
            del session['messages']
        session['messages'] = serialized_messages

        session['reset_done'] = False

        score_message = extract_text(serialized_messages)
        print("score_message :: ", score_message)



    except Exception as e:
        print(f"An error occurred: {e}")

    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and file.filename.endswith('.txt'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            thread_id = session.get('thread_id')

            if not thread_id:
                return redirect(url_for('index'))

            try:
                thread_message2 = client.beta.threads.messages.create(
                    thread_id,
                    role="user",
                    content=file_content
                )

                run = client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id
                )

                while run.status != "completed":
                    print("status 확인 중", run.status)
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )

                messages = client.beta.threads.messages.list(thread_id=thread_id).data
                serialized_messages = [serialize_message(message) for message in messages]
                print('serialized_messages', serialized_messages)
                if 'messages' in session:
                    del session['messages']
                session['messages'] = serialized_messages
                session['reset_done'] = False

                score_message = extract_text(serialized_messages)
                print("score_message :: ", score_message)

                first_message = get_first_assistant_message_from_list(serialized_messages)

                file_path = os.path.join('static', 'audio', 'speech.mp3')

                # 파일이 존재하면 삭제
                if os.path.exists(file_path):
                    os.remove(file_path)

                #speech_file_path를 /static/audio/speech.mp3로 설정
                base_path = Path(__file__).parent
                speech_file_path = base_path / "static" / "audio" / "speech.mp3"

                response = client.audio.speech.create(
                    model="tts-1",
                    voice="fable",
                    input=first_message
                )
                response.stream_to_file(speech_file_path)

            except Exception as e:
                print(f"An error occurred: {e}")

        except UnicodeDecodeError as e:
            print(f"An error occurred while reading the file: {e}")
            return "파일 인코딩 에러가 발생했습니다. UTF-8 인코딩을 사용해주세요.", 400

    return redirect(url_for('index'))

@app.route('/retrieve_thread', methods=['POST'])
def retrieve_thread():
    thread_id = request.form['thread_id']
    try:
        thread_messages = client.beta.threads.messages.list(thread_id=thread_id).data
        print(thread_messages)
        serialized_messages = [serialize_message_forRetreive(message) for message in thread_messages]
        print(serialized_messages)
        if 'messages' in session:
            del session['messages']
        session['messages'] = serialized_messages
        session['thread_id'] = thread_id  # Save the current thread_id in the session

        # 첫 번째 assistant 역할의 메시지를 선택
        first_assistant_message = get_first_assistant_message_from_list(serialized_messages)
        if first_assistant_message:
            session['first_assistant_message'] = first_assistant_message

        return jsonify({"status": "success", "messages": serialized_messages})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/get_first_assistant_message', methods=['POST'])
def get_first_assistant_message():
    messages = session.get('messages', [])
    first_message = get_first_assistant_message_from_list(messages)
    print("first_message")
    print(first_message)

    if not first_message:
        return jsonify({"status": "error", "message": "No assistant messages found."}), 400

    name_pattern = r"(?:안녕하세요|hello),\s*([가-힣a-zA-Z]+)님"
    score_pattern = r"\s*([\d.]+)/100"

    name_match = re.search(name_pattern, first_message)
    score_match = re.search(score_pattern, first_message)

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    print("현재 날짜와 시간:", formatted_now)

    result_text = "";
    if name_match and score_match:
        name = name_match.group(1)
        score = float(score_match.group(1))
        result_text = "안녕하세요," + name + "님 면접 최종점수는" + str(score) + "입니다. 수고하셨습니다.";
        print("result_text")
        print(result_text)
    # 파일 삭제 경로 설정
    # file_path = os.path.join('static', 'videos', 'output_video.mp3')
    #
    # # 파일이 존재하면 삭제
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    #
    # url = "https://api.d-id.com/talks"
    # payload = {
    #     "source_url": "https://bigeye.nicebizmap.co.kr/static/bigEye/images/photo.png",  # 여기서 실제 비디오 URL로 대체하세요
    #     "script": {
    #         "type": "text",
    #         "input": result_text,
    #         # "input": "안녕하세요. 삼두구이입니다. 크레딧관계로 테스트말로 대체합니다.",
    #         "subtitles": "false",
    #         "provider": {
    #             "type": "microsoft",
    #             "voice_id": "ko-KR-InJoonNeural"
    #         }
    #     },
    #     "config": {
    #         "fluent": "false",
    #         "pad_audio": "0.0"
    #     }
    # }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {DID_KEY}"
    }

    # create_talk_response = requests.post(url, json=payload, headers=headers)
    # str_status_code = str(create_talk_response.status_code)
    # print("str_status_code")
    # print(str_status_code)
    # result_str = str_status_code[:-1]
    # if int(result_str) != 20:
    #     return jsonify({"status": "error", "message": "Failed to create talk."}), create_talk_response.status_code
    #
    # talk_info = create_talk_response.json()
    # talk_id = talk_info.get('id')
    # print(talk_id)
    talk_id = "tlk_Smml45RinCzkmtA4nMrhD";

    if not talk_id:
        return jsonify({"status": "error", "message": "Talk ID not found."}), 400

    talk_url = f"https://api.d-id.com/talks/{talk_id}"
    video_dir = 'static/videos'
    video_path = os.path.join(video_dir, "output_video.mp4")

    # 이미 파일이 존재하는지 확인
    if os.path.exists(video_path):
        os.remove(video_path)  # 기존 파일 삭제

    while True:
        response = requests.get(talk_url, headers=headers)
        str_status_code = str(response.status_code)
        print("str_status_code2")
        print(str_status_code)
        result_str = str_status_code[:-1]
        print("result_str2")
        print(result_str)
        if int(result_str) == 20:
            talk_info = response.json()
            video_url = talk_info.get('result_url')
            if video_url:
                video_response = requests.get(video_url)
                str_video_status_code = str(video_response.status_code)
                result_video_str = str_video_status_code[:-1]
                if int(result_video_str) == 20:
                    with open(video_path, "wb") as file:
                        file.write(video_response.content)
                    return jsonify({"status": "success", "message": "Video downloaded successfully.", "video_path": video_path}), 200
                else:
                    return jsonify({"status": "error", "message": f"Failed to download video. Status code: {video_response.status_code}"}), video_response.status_code
            else:
                time.sleep(10)
        else:
            return jsonify({"status": "error", "message": f"Failed to get talk info. Status code: {response.status_code}"}), response.status_code


@app.route('/audio_download', methods=['POST'])
def audio_download():
    messages = session.get('messages', [])
    print("messages :: ")
    print(messages)
    first_message = get_first_assistant_message_from_list(messages)
    print("first_message :: ")
    print(first_message)
    # 파일 삭제 경로 설정
    file_path = os.path.join('static', 'audio', 'speech.mp3')

    # 파일이 존재하면 삭제
    if os.path.exists(file_path):
        os.remove(file_path)

    #speech_file_path를 /static/audio/speech.mp3로 설정
    base_path = Path(__file__).parent
    speech_file_path = base_path / "static" / "audio" / "speech.mp3"

    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=first_message
    )
    response.stream_to_file(speech_file_path)

    return jsonify({"status": "success", "message": "Video downloaded successfully."}), 200

@app.route('/get_audio_file', methods=['GET'])
def get_audio_file():
    audio_file_path = "static/audio/speech.mp3"

    if os.path.exists(audio_file_path):
        return send_file(audio_file_path, as_attachment=True)
    else:
        return jsonify({"error": "Audio file not found."}), 404

def get_first_assistant_message_from_list(messages):
    for message in messages:
        if message['role'] == 'assistant':
            content = message['content']
            # content가 문자열인 경우
            if isinstance(content, str):
                return content
            # content가 리스트인 경우
            elif isinstance(content, list):
                for content_block in content:
                    if isinstance(content_block, dict):
                        # 'text' 키가 있고 그 안에 'value'가 있는 경우
                        if 'text' in content_block and 'value' in content_block['text']:
                            return content_block['text']['value']
                    # content_block이 문자열일 경우
                    elif isinstance(content_block, str):
                        return content_block
    return None

def get_first_assistant_message_from_list_reversed(messages):
    # 메시지를 역순으로 정렬
    for message in reversed(messages):
        if message['role'] == 'assistant':
            for content_block in message['content']:
                if 'text' in content_block and 'value' in content_block['text']:
                    return content_block['text']['value']
    return None
if __name__ == "__main__":
    app.run(debug=True, port=5000)
