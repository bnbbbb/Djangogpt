from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    prompt = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='prompt')
    response = models.TextField()
    sender = models.ForeignKey(User ,on_delete=models.CASCADE, related_name='sent_prompt')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prompt}: {self.response}"


class Chat(models.Model):
    title = models.CharField(max_length=100)
    participants = models.ManyToManyField(User, related_name='chats')