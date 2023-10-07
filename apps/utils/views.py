
import os
import cv2
from django.http import HttpResponse
from apps.utils.errors import SIGN_MAKE_FAIL
from server.settings import BASE_DIR
import numpy as np
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from apps.utils.viewsets import CustomGenericViewSet
from apps.utils.mixins import CustomCreateModelMixin
from apps.utils.serializers import GenSignatureSerializer
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from django.core.cache import cache
import json
import requests


class SignatureViewSet(CustomCreateModelMixin, CustomGenericViewSet):
    authentication_classes = ()
    permission_classes = ()
    create_serializer_class = GenSignatureSerializer

    def create(self, request, *args, **kwargs):
        """
        照片生成透明签名图片

        照片生成透明签名图片
        """
        path = (BASE_DIR + request.data['path']).replace('\\', '/')
        try:
            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            size = image.shape
            width = size[0]  # 宽度
            height = size[1]  # 高度
            if size[2] != 4:  # 判断
                background = np.zeros((size[0], size[1], 4))
                for yh in range(height):
                    for xw in range(width):
                        background[xw, yh, :3] = image[xw, yh]
                        background[xw, yh, 3] = 255
                image = background
            size = image.shape
            for i in range(size[0]):
                for j in range(size[1]):
                    if image[i][j][0] > 100 and image[i][j][1] > 100 and image[i][j][2] > 100:
                        image[i][j][3] = 0
                    else:
                        image[i][j][0], image[i][j][1], image[i][j][2] = 0, 0, 0
            ext = os.path.splitext(path)
            new_path = ext[0] + '.png'
            cv2.imwrite(new_path, image)
            return Response({'path': new_path.replace(BASE_DIR, '')})
        except Exception:
            raise ParseError(**SIGN_MAKE_FAIL)