from django.shortcuts import render
from django.conf import settings
from dotenv import load_dotenv
import openai
import os

def chat_view(request):
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    print(openai.api_key)
    # 사용자로부터 받은 입력을 가져옵니다.
    user_input = request.POST.get('user_input', '')

    # ChatGPT 모델을 초기화합니다.
    model = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ]
    )

    # ChatGPT를 사용하여 대화를 생성합니다.
    chat_response = model['choices'][0]['message']['content']

    context = {
        'user_input': user_input,
        'chat_response': chat_response
    }

    return render(request, 'chat/chat.html', context)
