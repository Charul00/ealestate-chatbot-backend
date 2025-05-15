from django.urls import path
from .views import home
from .api import ChatbotQueryView, FileUploadView

urlpatterns = [
    path('', home, name='home'),
    path('api/query/', ChatbotQueryView.as_view(), name='chatbot-query'),
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
]
