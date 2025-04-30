
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
import chat_app.views as views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google-login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('user-creation/', views.UserCreation.as_view(), name='user_create'),
    path('get-message/', views.GetMessage.as_view(), name='get_messages'),
    path('home/',views.Dashboard.as_view(), name='message'),
    path('notifications/',views.NotificationApiView.as_view(), name='notification'),
    path('mark-as-read/',views.NotificationReadApiView.as_view(), name='mark_as_read'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)