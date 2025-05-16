from django.urls import path
from .views import home
import os

# Check if running on Render (via environment variable)
RENDER = os.environ.get('RENDER', 'False').lower() == 'true'

if RENDER:
    try:
        # Use simplified API for Render deployment 
        from .api_render import QueryView, FileUploadView
        print("Using simplified API for Render deployment")
    except ImportError:
        # Fallback to full API if there's an issue with the import
        from .api import ChatbotQueryView as QueryView, FileUploadView
        print("Fallback to full API implementation")
else:
    # Use full API implementation for local development
    from .api import ChatbotQueryView as QueryView, FileUploadView
    print("Using full API implementation")

urlpatterns = [
    path('', home, name='home'),
    path('api/query/', QueryView.as_view(), name='chatbot-query'),
    path('api/upload/', FileUploadView.as_view(), name='file-upload'),
]
