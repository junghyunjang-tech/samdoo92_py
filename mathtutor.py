from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path
import openai


load_dotenv()
current_directory = os.getcwd()
API_KEY = os.environ['OPENAI_API_KEY']
print(API_KEY)

client = OpenAI(api_key=API_KEY)

# my_assistant = client.beta.assistants.create(
#     instructions="지침 이 GPT는 나이스지니데이타의 김민수 대표(면접자, 평가자)님을 대신하여 면접 지원자를 평가하고 적절하게 질문을 해주는 역할을 합니다. 이 챗gpt가 적절한 질문을 하면 면접자가 답변을 하고 지원자의 답변을 수집합니다. 부정적인 단어 사용을 금지합니다. 면접 대화 후 각 지원자의 답변을 내부적으로 평가하여 책임감, 도전정신, 핵심을 보는 눈, 화합 능력을 바탕으로 순위를 매기고 최종 결과를 제공합니다. 이러한 평가 기준은 면접 대화 중에는 직접 언급되지 않으며, 평가와 스코어링할 때만 반영됩니다. 각 질문에 대해 최소 3개에서 최대 5개의 답변을 받은 후 다음 질문으로 넘어갑니다. 예를 들어, 질문 1에 대한 답변을 3-5개 받은 후 질문 2로 넘어가며, 질문 2에 대한 답변을 3-5개 받은 후 질문 3으로 넘어갑니다.",
#     name="삼두구이",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4o-mini",
# )
# print(my_assistant)

# assistant id -- asst_MxqorhgXLjXncMMQVnAJGbAY

# thread = client.beta.threads.create()
#
# print(thread)

# thread id -- thread_m8Vlo6ECI93xxrqjD7TmHvSd



# thread_message = client.beta.threads.messages.create(
#     "thread_m8Vlo6ECI93xxrqjD7TmHvSd",
#     role="user",
#     content="나는 장정현입니다.",
# )
# print(thread_message)

# message id = msg_FUiXII0QPeTZxAaZTWPoRJMs

# run = client.beta.threads.runs.create(
#     thread_id="thread_m8Vlo6ECI93xxrqjD7TmHvSd",
#     assistant_id="asst_MxqorhgXLjXncMMQVnAJGbAY"
# )
#
# print(run)


# run_id = run_2b0iUncclglJiIwgWN4lQwEr

# run = client.beta.threads.runs.retrieve(
#     thread_id="thread_m8Vlo6ECI93xxrqjD7TmHvSd",
#     run_id="run_V1SIgWEB6mIE9Hvwx9D12REO"
# )
#
# print(run)

# thread_messages = client.beta.threads.messages.list("thread_m8Vlo6ECI93xxrqjD7TmHvSd")
#
# print(thread_messages.data)
