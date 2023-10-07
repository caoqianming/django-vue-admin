
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.auth1.views import (CodeLogin, LoginView, LogoutView, PwResetView,
                              SecretLogin, SendCode, TokenBlackView, WxLogin, WxmpLogin, TokenLoginView, FaceLoginView)

API_BASE_URL = 'api/auth/'
urlpatterns = [
    path(API_BASE_URL + 'token/', TokenLoginView.as_view(), name='token_obtain_pair'),
    path(API_BASE_URL + 'token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(API_BASE_URL + 'token/black/', TokenBlackView.as_view(), name='token_black'),
    path(API_BASE_URL + 'login/', LoginView.as_view(), name='session_login'),
    path(API_BASE_URL + 'login_secret/', SecretLogin.as_view(), name='secret_login'),
    path(API_BASE_URL + 'login_wxmp/', WxmpLogin.as_view(), name='login_wxmp'),
    path(API_BASE_URL + 'login_wx/', WxLogin.as_view(), name='login_wx'),
    path(API_BASE_URL + 'login_sms_code/', CodeLogin.as_view(), name='login_sms_code'),
    path(API_BASE_URL + 'sms_code/', SendCode.as_view(), name='sms_code_send'),
    path(API_BASE_URL + 'logout/', LogoutView.as_view(), name='session_logout'),
    path(API_BASE_URL + 'reset_password/', PwResetView.as_view(), name='reset_password'),
    path(API_BASE_URL + 'login_face/', FaceLoginView.as_view(), name='face_login')
]
