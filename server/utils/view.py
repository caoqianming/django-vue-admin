from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from PIL import Image
from django.conf import settings

from datetime import datetime
import os
import uuid


class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        fileobj = request.FILES['file']
        file_name = fileobj.name.encode('utf-8').decode('utf-8')
        file_name_new = str(uuid.uuid1()) + '.' + file_name.split('.')[-1]
        subfolder = os.path.join('media', datetime.now().strftime("%Y%m%d"))
        if not os.path.exists(subfolder):
            os.mkdir(subfolder)
        file_path = os.path.join(subfolder, file_name_new)
        file_path = file_path.replace('\\', '/')
        with open(file_path, 'wb') as f:
            for chunk in fileobj.chunks():
                f.write(chunk)
        resdata = {"name": file_name, "path": '/' + file_path}
        return Response(resdata)
