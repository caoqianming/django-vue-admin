from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from PIL import Image
from django.conf import settings
from rest_framework import status
from datetime import datetime
import os
import uuid
import cv2
from server.settings import BASE_DIR

# class UploadFileView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser,)

#     def post(self, request, *args, **kwargs):
#         fileobj = request.FILES['file']
#         file_name = fileobj.name.encode('utf-8').decode('utf-8')
#         file_name_new = str(uuid.uuid1()) + '.' + file_name.split('.')[-1]
#         subfolder = os.path.join('media', datetime.now().strftime("%Y%m%d"))
#         if not os.path.exists(subfolder):
#             os.mkdir(subfolder)
#         file_path = os.path.join(subfolder, file_name_new)
#         file_path = file_path.replace('\\', '/')
#         with open(file_path, 'wb') as f:
#             for chunk in fileobj.chunks():
#                 f.write(chunk)
#         resdata = {"name": file_name, "path": '/' + file_path}
#         return Response(resdata)

class GenSignature(APIView):
    """
    生成签名图片
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        path = (BASE_DIR + request.data['path']).replace('\\', '/')
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        size = image.shape
        for i in range(size[0]):
            for j in range(size[1]):
                if image[i][j][0]>100 and image[i][j][1]>100 and image[i][j][2]>100:
                    image[i][j][3] = 0
                else:
                    image[i][j][0],image[i][j][1],image[i][j][2] = 0,0,0
        cv2.imwrite(path,image)
        return Response(request.data, status=status.HTTP_200_OK)
