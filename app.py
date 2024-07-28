from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import re
import pandas as pd
from datetime import datetime

# 환경 변수 로드
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
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
            name_pattern = r"안녕하세요,\s*([가-힣]+)님"
            score_pattern = r"평가 점수:\s*([\d.]+)/5점"

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
        session['extracted_data'].extend(extracted_data)
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
        print('serialized_messages', serialized_messages)
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
                session['messages'] = serialized_messages
                session['reset_done'] = False

                score_message = extract_text(serialized_messages)
                print("score_message :: ", score_message)

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
        serialized_messages = [serialize_message_forRetreive(message) for message in thread_messages]
        session['messages'] = serialized_messages
        session['thread_id'] = thread_id  # Save the current thread_id in the session
        return jsonify({"status": "success", "messages": serialized_messages})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
