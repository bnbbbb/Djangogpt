from django.shortcuts import render
from django.views import View
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



class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_call_count(self, request):
        # 사용자별 세션 변수 이름 설정
        user_call_count_key = f"user_{request.user.id}_call_count"

        # 세션 변수가 존재하는 경우 현재 호출 횟수 반환, 없는 경우 0 반환
        return request.session.get(user_call_count_key, 0)

    def update_user_call_count(self, request, count):
        # 사용자별 세션 변수 이름 설정
        user_call_count_key = f"user_{request.user.id}_call_count"

        # 세션에 현재 호출 횟수 저장
        request.session[user_call_count_key] = count
        request.session.modified = True

    def get(self, request):
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

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

            # 사용자의 호출 횟수 확인
            call_count = self.get_user_call_count(request)

            # 하루에 다섯 번 이상 호출한 경우 에러 응답 반환
            if call_count >= 5:
                return Response({'error': 'You have exceeded the daily usage limit.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 대화 기록에 새로운 응답 추가
            chat = Chat.objects.filter(participants=sender).order_by('-id').first()

            if not chat:
                chat = Chat.objects.create(title="New Chat")
                chat.participants.add(sender)

            conversation_data = {
                'prompt': prompt, 
                'response': response,
                'sender': sender.id,
                'chat': chat.id,
                'call_count':call_count,
            }

            serializer = ConversationSerializer(data=conversation_data)
            if serializer.is_valid():
                serializer.save()

                session_conversations.append({'prompt': prompt, 'response': response})
                request.session['conversations'] = session_conversations
                request.session.modified = True

                # 사용자의 호출 횟수 증가
                call_count += 1
                self.update_user_call_count(request, call_count)

                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)



class NewChat(APIView):
    def get_chat_title(self):
        # ChatView의 첫 번째 prompt를 가져와서 채팅 제목으로 사용
        first_chat = Conversation.objects.first()
        if first_chat:
            return first_chat.prompt
        return "New Chat"

    def get(self, request):
        serializer = ChatSerializer()
        print(serializer)

    def post(self, request, *args, **kwargs):
        sender = request.user

        # ChatView의 첫 번째 prompt를 가져와서 채팅 제목으로 사용
        chat_title = self.get_chat_title()

        # 새로운 채팅 생성
        chat = Chat.objects.create(title=chat_title)
        chat.participants.add(sender)

        # ChatSerializer를 사용하여 채팅 정보를 직렬화하고 응답 데이터로 반환
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)





    