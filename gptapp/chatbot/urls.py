from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    # path('', views.chat_view, name='chat'),
]