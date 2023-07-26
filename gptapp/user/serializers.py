from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['email']
        fields = '__all__'
    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)
    
    def validate(self, data):
        # 여기서 추가적인 유효성 검사를 진행할 수 있습니다.
        return data
        