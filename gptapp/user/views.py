from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth.hashers import make_password

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


### Login
class Login(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            print(request.user)
            return Response({'detail': '이미 인증된 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginSerializer(data=request.data)
        print(f"시리얼라이저는 유효한가? {serializer.is_valid()}")
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 사용자 인증 시도
            user = authenticate(request=request, email=email, password=password)

            print(f"인증된 유저? {user}")
            if user is not None:
                login(request, user)
                return Response({'message': '로그인에 성공하였습니다.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        print(f"시리얼 라이저 에러: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def get(self, request):
        print(request.user)
        logout(request)
        return Response({'message': '로그아웃에 성공하였습니다.'}, status=status.HTTP_200_OK)