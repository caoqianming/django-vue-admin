
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from apps.auth1.errors import USERNAME_OR_PASSWORD_WRONG
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from apps.auth1.services import check_phone_code
from apps.utils.sms import send_sms
from apps.utils.tools import rannum
from apps.utils.wxmp import wxmpClient
from apps.utils.wx import wxClient
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from apps.auth1.services import validate_password
import base64
from apps.utils.tools import tran64
from apps.auth1.serializers import FaceLoginSerializer


from apps.auth1.serializers import (CodeLoginSerializer, LoginSerializer,
                                    PwResetSerializer, SecretLoginSerializer, SendCodeSerializer, WxCodeSerializer)
from apps.system.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.


def get_tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class TokenLoginView(CreateAPIView):
    """
    账户名/密码获取token

    账户名/密码获取token
    """
    authentication_classes = []  
    permission_classes = []
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data
        password_check = vdata.get('password_check', True)
        # 校验密码复杂度
        is_ok = validate_password(vdata.get('password'))
        if is_ok is False and password_check:
            raise ParseError('密码校验失败, 请更换登录方式并修改密码')
        user = authenticate(username=vdata.get('username'),
                            password=vdata.get('password'))
        if user is not None:
            token_dict = get_tokens_for_user(user)
            token_dict['password_ok'] = is_ok
            return Response(token_dict)
        raise ParseError(**USERNAME_OR_PASSWORD_WRONG)
    
class TokenBlackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Token拉黑


        Token拉黑
        """
        return Response(status=status.HTTP_200_OK)


class LoginView(CreateAPIView):
    """
    Session登录


    账户密码Session登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data
        user = authenticate(username=vdata.get('username'),
                            password=vdata.get('password'))
        if user is not None:
            login(request, user)
            return Response(status=201)
        raise ParseError(**USERNAME_OR_PASSWORD_WRONG)


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """
        退出登录


        退出登录
        """
        logout(request)
        return Response()


class WxmpLogin(CreateAPIView):
    """微信小程序自动登录

    微信小程序自动登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = WxCodeSerializer

    def post(self, request):
        code = request.data['code']
        info = wxmpClient.get_basic_info(code=code)
        openid = info['openid']
        session_key = info['session_key']
        try:
            user = User.objects.get(wxmp_openid=openid)
            ret = get_tokens_for_user(user)
            ret['wxmp_session_key'] = session_key
            ret['wxmp_openid'] = openid
            cache.set(code, ret, 60*5)
            return Response(ret)
        except Exception:
            return Response({'wxmp_openid': openid, 'wxmp_session_key': session_key}, status=400)


class WxLogin(CreateAPIView):
    """微信公众号授权登录

    微信公众号授权登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = WxCodeSerializer

    def post(self, request):
        code = request.data['code']
        info = wxClient.get_basic_info(code=code)
        openid = info['openid']
        access = info['access_token']
        try:
            user = User.objects.get(wx_openid=openid)
            ret = get_tokens_for_user(user)
            ret['wx_token'] = access
            ret['wx_openid'] = openid
            cache.set(code, ret, 60*5)
            return Response(ret)
        except Exception:
            return Response({'wx_openid': openid, 'wx_token': access}, status=400)


class SendCode(CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SendCodeSerializer

    def post(self, request):
        """短信验证码发送

        短信验证码发送
        """
        phone = request.data['phone']
        code = rannum(6)
        is_ok, _ = send_sms(phone, 505, {'code': code})
        cache.set(phone, code, 60*5)
        if is_ok:
            return Response()
        raise ParseError('短信发送失败,请确认手机号')


class CodeLogin(CreateAPIView):
    """手机验证码登录

    手机验证码登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = CodeLoginSerializer

    def post(self, request):
        phone = request.data['phone']
        code = request.data['code']
        check_phone_code(phone, code)
        user = User.objects.filter(phone=phone).first()
        if user:
            ret = get_tokens_for_user(user)
            return Response(ret)
        raise ParseError('账户不存在或已禁用')


class SecretLogin(CreateAPIView):
    """App端密钥登录

    App端密钥登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = SecretLoginSerializer

    def post(self, request):
        sr = SecretLoginSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        username = vdata['username']
        secret = vdata['secret']
        user = User.objects.filter(Q(username=username) | Q(phone=username) | Q(
            employee__id_number=username)).filter(secret=secret).first()
        if user:
            ret = get_tokens_for_user(user)
            return Response(ret)
        raise ParseError('登录失败')


class PwResetView(CreateAPIView):
    """重置密码

    重置密码
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = PwResetSerializer

    def post(self, request):
        sr = PwResetSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        check_phone_code(vdata['phone'], vdata['code'])
        user = User.objects.filter(phone=vdata['phone']).first()
        if user:
            user.password = make_password(vdata['password'])
            user.save()
            return Response()
        raise ParseError('账户不存在或已禁用')
    

class FaceLoginView(CreateAPIView):
    """人脸识别登录

    人脸识别登录
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = FaceLoginSerializer


    def create(self, request, *args, **kwargs):
        """
        人脸识别登录
        """
        from apps.hrm.services import HrmService
        base64_data = base64.urlsafe_b64decode(tran64(request.data.get('base64').replace(' ', '+')))
        ep, msg = HrmService.face_compare_from_base64(base64_data)
        if ep:
            if ep.user and ep.user.is_active and ep.user.is_deleted is False:
                user = ep.user
                refresh = RefreshToken.for_user(ep.user)
            # # 可设为在岗
            # now = timezone.now()
            # now_local = timezone.localtime()
            # if 8<=now_local.hour<=17:
            #     ins, created = ClockRecord.objects.get_or_create(
            #             create_by = user, create_time__hour__range = [8,18], 
            #             create_time__year=now_local.year, create_time__month=now_local.month, 
            #             create_time__day=now_local.day,
            #             defaults={
            #                 'type':ClockRecord.ClOCK_WORK1,
            #                 'create_by':user,
            #                 'create_time':now
            #             })
            #     # 设为在岗
            #     if created:
            #         Employee.objects.filter(user=user).update(is_atwork=True, last_check_time=now)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username':user.username,
                    'name':user.name
                })
            else:
                raise ParseError('账户不存在或不可用') 
        raise ParseError(msg)
