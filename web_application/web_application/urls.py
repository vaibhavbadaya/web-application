from django.urls import path, include

urlpatterns = [
    path('api/', include('web_api.urls')),
]
