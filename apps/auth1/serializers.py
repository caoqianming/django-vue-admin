from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    password = serializers.CharField(label="密码")
    password_check = serializers.BooleanField(required=False, default=True)


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号")


class CodeLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号")
    code = serializers.CharField(label="验证码")


class WxCodeSerializer(serializers.Serializer):
    code = serializers.CharField(label="code")


class PwResetSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号")
    code = serializers.CharField(label="验证码")
    password = serializers.CharField(label="新密码")


class SecretLoginSerializer(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    secret = serializers.CharField(label="密钥")


class FaceLoginSerializer(serializers.Serializer):
    base64 = serializers.CharField()