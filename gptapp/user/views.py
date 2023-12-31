from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, LoginSerializer
from dotenv import load_dotenv

from allauth.socialaccount.models import SocialAccount
from json import JSONDecodeError
from django.http import JsonResponse
from django.views import View
from .models import User
import requests
from rest_framework.permissions import AllowAny
from django.middleware.csrf import get_token

import os

# Create your views here.

### Register
class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            # 유효한 데이터인 경우, 새로운 사용자 생성
            password = make_password(serializer.validated_data['password'])
            serializer.save(password=password, is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # 유효하지 않은 데이터인 경우, 오류 응답 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_csrf_token(request):
    csrf_token = get_token(request)
    print(csrf_token)
    return JsonResponse({'csrfToken': csrf_token})


### Login
class Login(APIView):
    def post(self, request):

        if request.user.is_authenticated:
            print(request.user)
            return Response({'detail': '이미 인증된 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginSerializer(data=request.data)
        # print(f"시리얼라이저는 유효한가? {serializer.is_valid()}")
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 사용자 인증 시도
            user = authenticate(request=request, email=email, password=password)

            print(f"인증된 유저? {user}")
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'message': '로그인에 성공하였습니다.', 'access_token': access_token,
                'email':email, 'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'message': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        # print(f"시리얼 라이저 에러: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def get(self, request):
        print(request.user)
        # print(request.META)
        logout(request)
        return Response({'message': '로그아웃에 성공하였습니다.'}, status=status.HTTP_200_OK)

# load_dotenv()

# state = os.getenv("STATE")
# BASE_URL = 'http://localhost:8000/'
# GOOGLE_CALLBACK_URI = BASE_URL + 'user/google/callback/'

# class GoogleLoginView(APIView):
#     def get(self, request):
#         scope = "https://www.googleapis.com/auth/userinfo.email"
#         client_id = os.getenv("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
#         return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


# class GoogleCallbackView(View):
#     def get(self, request):
#         client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
#         client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
#         code = request.GET.get('code')

#         # 1. 받은 코드로 구글에 access token 요청
#         token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
        
#         ### 1-1. json으로 변환 & 에러 부분 파싱
#         token_req_json = token_req.json()
#         error = token_req_json.get("error")

#         ### 1-2. 에러 발생 시 종료
#         if error is not None:
#             raise JSONDecodeError(error)

#         ### 1-3. 성공 시 access_token 가져오기
#         access_token = token_req_json.get('access_token')

#         #################################################################

#         # 2. 가져온 access_token으로 이메일값을 구글에 요청
#         email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
#         email_req_status = email_req.status_code
#         print(email_req_status)
#         ### 2-1. 에러 발생 시 400 에러 반환
#         if email_req_status != 200:
#             return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
        
#         ### 2-2. 성공 시 이메일 가져오기
#         email_req_json = email_req.json()
#         email = email_req_json.get('email')

#         # return JsonResponse({'access': access_token, 'email':email})

#         #################################################################

#         # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
#         try:
#             # 전달받은 이메일로 등록된 유저가 있는지 탐색
#             user = User.objects.get(email=email)

#             # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
#             social_user = SocialAccount.objects.get(user=user)

#             # 있는데 구글계정이 아니어도 에러
#             if social_user.provider != 'google':
#                 return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

#             # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
#             data = {'access_token': access_token, 'code': code}
#             accept = requests.post(f"{BASE_URL}user/google/login/finish/", data=data)
#             accept_status = accept.status_code

#             # 뭔가 중간에 문제가 생기면 에러
#             if accept_status != 200:
#                 return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

#             accept_json = accept.json()
#             accept_json.pop('user', None)
#             return JsonResponse(accept_json)

#         except User.DoesNotExist:
#             # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
#             data = {'access_token': access_token, 'code': code}
#             accept = requests.post(f"{BASE_URL}user/google/login/finish/", data=data)
#             accept_status = accept.status_code

#             # 뭔가 중간에 문제가 생기면 에러
#             if accept_status != 200:
#                 return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

#             accept_json = accept.json()
#             accept_json.pop('user', None)
#             return JsonResponse(accept_json)
            
#         except SocialAccount.DoesNotExist:
#             # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
#             return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        

# from dj_rest_auth.registration.views import SocialLoginView
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from allauth.socialaccount.providers.google import views as google_view

# class GoogleLogin(SocialLoginView):
#     adapter_class = google_view.GoogleOAuth2Adapter
#     callback_uri = GOOGLE_CALLBACK_URI
#     client_class = OAuth2Client