from django.urls import path
from .views import FileUpload, FileDelete, DashboardView,FileDownload, get_files, register_user, custom_login, custom_refresh
from .views import user_profile
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('files/', FileUpload.as_view(), name='file-upload'),
    path('files/<str:filename>/', FileDownload, name='file-download'),
    path('files/delete/<str:filename>/', FileDelete.as_view(), name='file-delete'),
    path('files/list/', get_files, name='get-files'),
    path('register/', register_user, name='register'),
    path('login/', custom_login, name='login'),
    path('token/refresh/', custom_refresh, name='token-refresh'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'), 
    path('profile/', user_profile, name='user_profile'),
]
