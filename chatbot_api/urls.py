from django.urls import path
from .views import home

# Try to import from api_render (simplified version for Render), 
# fall back to regular api if not available
try:
    from .api_render import QueryView, FileUploadView
    print("Using simplified API for Render deployment")
except ImportError:
    from .api import ChatbotQueryView as QueryView, FileUploadView
    print("Using full API implementation")

urlpatterns = [
    path('', home, name='home'),
    path('api/query/', QueryView.as_view(), name='chatbot-query'),
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
]
