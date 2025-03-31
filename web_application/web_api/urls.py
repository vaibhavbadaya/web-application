from django.urls import path
from .views import FileUploadView, FileDownloadView, FileDeleteView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('files/', FileUploadView.as_view(), name='file_upload'),
    path('files/<str:filename>/', FileDownloadView.as_view(), name='file_download'),
    path('files/<str:filename>/delete/', FileDeleteView.as_view(), name='file_delete'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
