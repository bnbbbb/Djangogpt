# from django.shortcuts import render
# from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .serializers import ConversationSerializer, ChatSerializer
from dotenv import load_dotenv
from .models import Chat, Conversation
import openai
import os


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

class ChatList(APIView):
    permission_classes = [IsAuthenticated]
    print(permission_classes)
    def get(self, request):
        chats = Chat.objects.filter(participants = request.user).order_by('-id')
        serialized = ChatSerializer(chats, many=True)
        return Response(serialized.data)
    def post(self, request):
        title = request.data.get('title')
        if title:
            chat = Chat.objects.create(title=title)
            chat.participants.add(request.user)

            # 채팅방 생성과 동시에 첫 번째 메시지를 생성
            response = request.data.get('response')
            if response:
                Conversation.objects.create(chat=chat, sender=request.user, response=response)

            return Response({'message': 'Chat created successfully.'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Title is required.'}, status=status.HTTP_400_BAD_REQUEST)

class ChatView(APIView):
    # permission_classes = [IsAuthenticated]
        
    def get(self, request):
        
        prompt = Conversation.objects.all()
        serialized_prompt = ConversationSerializer(prompt, many = True) # 직렬화
        return Response(serialized_prompt.data)
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        sender = request.user
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
            conversation = Conversation(prompt=prompt, response=response, sender = sender)
            conversation.save()

            session_conversations.append({'prompt': prompt, 'response': response})
            request.session['conversations'] = session_conversations
            request.session.modified = True

            return Response({'response': response}, status=status.HTTP_200_OK)

        return Response({'error': 'Prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)

