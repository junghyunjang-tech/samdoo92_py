from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import re

# 환경 변수 로드
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']
print(API_KEY)

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)
app.secret_key = 'supersecretkey'

assistant_id = "asst_MxqorhgXLjXncMMQVnAJGbAY"

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

def extract_text(data):
    result = []
    for message in data:
        for content in message['content']:
            text = content['text']['value']
            name_pattern =  r"안녕하세요,\s*([가-힣]+)님"
            score_pattern = r"평가 점수:\s*(\d\.\d)/5점"

            # 정규 표현식 검색
            name_match = re.search(name_pattern, text)
            score_match = re.search(score_pattern, text)

            # 검색된 결과 출력
            if name_match and score_match:
                name = name_match.group(1)
                score = score_match.group(1)
                print(f"이름: {name}")
                print(f"평가 점수: {score}")
            else:
                print("이름 또는 평가 점수를 찾을 수 없습니다.")
    return result

@app.route('/')
def index():
    if 'reset_done' not in session:
        return redirect(url_for('reset'))

    messages = session.get('messages', [])
    html = ''
    for item in messages:
        role_class = 'assistant' if item['role'] == 'assistant' else 'user'
        for content_block in item['content']:
            if 'text' in content_block and 'value' in content_block['text']:
                text_value = content_block['text']['value'].replace('&nbsp;', ' ')
                html += f'<div class="message {role_class}">{text_value}</div>\n'

    return render_template('index.html', my_variable=html)

@app.route('/reset', methods=['GET'])
def reset():
    session['messages'] = get_initial_messages()
    thread = client.beta.threads.create()
    session['thread_id'] = thread.id
    reset_message = client.beta.threads.messages.create(
        session['thread_id'],
        role="assistant",
        content="안녕하세요. 나이스지니데이타 대표 김민수입니다. 면접 시작하겠습니다."
    )
    session['reset_done'] = True
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

        scroe_message = extract_text(serialized_messages)
        print("scroe_message :: " + scroe_message )

    except Exception as e:
        print(f"An error occurred: {e}")

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
