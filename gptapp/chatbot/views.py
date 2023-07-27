# from django.shortcuts import render
# from django.views import View
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import openai
import os
from .models import Conversation
from .serializers import ConversationSerializer


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


# class ChatView(View):
#     def get(self, request, *args, **kwargs):
#         print(openai.api_key)
#         conversations = request.session.get('conversations', [])
#         return render(request, 'chat/chat.html', {'conversations': conversations})

#     def post(self, request, *args, **kwargs):
#         prompt = request.POST.get('prompt')
#         if prompt:
#             # 이전 대화 기록 가져오기
#             session_conversations = request.session.get('conversations', [])
#             previous_conversations = "\n".join([f"User: {c['prompt']}\nAI: {c['response']}" for c in session_conversations])
#             prompt_with_previous = f"{previous_conversations}\nUser: {prompt}\nAI:"

#             # ChatGPT와 상호작용하여 응답 받기
#             model_engine = "text-davinci-003"
#             completions = openai.Completion.create(
#                 engine=model_engine,
#                 prompt=prompt_with_previous,
#                 max_tokens=1024,
#                 n=5,
#                 stop=None,
#                 temperature=0.5,
#             )
#             response = completions.choices[0].text.strip()

#             # 대화 기록에 새로운 응답 추가
#             conversation = Conversation(prompt=prompt, response=response)
#             conversation.save()

#             session_conversations.append({'prompt': prompt, 'response': response})
#             request.session['conversations'] = session_conversations
#             request.session.modified = True

#         return self.get(request, *args, **kwargs)
# class 


class ChatView(APIView):
    permission_classes = [IsAuthenticated]
        
    def get(self, request):
        
        prompt = Conversation.objects.all()
        serialized_prompt = ConversationSerializer(prompt, many = True) # 직렬화
        return Response(serialized_prompt.data)
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        if prompt:
            # 이전 대화 기록 가져오기
            session_conversations = request.session.get('conversations', [])
            previous_conversations = "\n".join([f"User: {c['prompt']}\nAI: {c['response']}" for c in session_conversations])
            prompt_with_previous = f"{previous_conversations}\nUser: {prompt}\nAI:"

            # ChatGPT와 상호작용하여 응답 받기
            model_engine = "text-davinci-003"
            completions = openai.Completion.create(
                engine=model_engine,
                prompt=prompt_with_previous,
                max_tokens=1024,
                n=5,
                stop=None,
                temperature=0.5,
            )
            response = completions.choices[0].text.strip()

            # 대화 기록에 새로운 응답 추가
            conversation = Conversation(prompt=prompt, response=response)
            conversation.save()

            session_conversations.append({'prompt': prompt, 'response': response})
            request.session['conversations'] = session_conversations
            request.session.modified = True

            return Response({'response': response}, status=status.HTTP_200_OK)

        return Response({'error': 'Prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)


class ChatList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        pass
    def post(self, request):
        pass