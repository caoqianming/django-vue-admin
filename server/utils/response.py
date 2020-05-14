from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
import rest_framework.status as status


class BaseResponse(object):
    """
    封装的返回信息类
    """

    def __init__(self):
        self.code = 200
        self.data = None
        self.msg = None

    @property
    def dict(self):
        return self.__dict__


class FitJSONRenderer(JSONRenderer):
    """
    自行封装的渲染器
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        如果使用这个render，
        普通的response将会被包装成：
            {"code":200,"data":"X","msg":"X"}
        这样的结果
        使用方法：
            - 全局
                REST_FRAMEWORK = {
                'DEFAULT_RENDERER_CLASSES': ('utils.response.FitJSONRenderer', ),
                }
            - 局部
                class UserCountView(APIView):
                    renderer_classes = [FitJSONRenderer]

        :param data: {"msg":"X"}
        :param accepted_media_type:
        :param renderer_context:
        :return: {"code":200,"data":"X","msg":"X"}
        """
        response_body = BaseResponse()
        response = renderer_context.get("response")
        response_body.code = response.status_code
        if response_body.code >= 400:  # 响应异常
            response_body.msg = data['detail'] if 'detail' in data else data
        else:
            response_body.data = data
        renderer_context.get("response").status_code = 200  # 统一成200响应,用code区分
        return super(FitJSONRenderer, self).render(response_body.dict, accepted_media_type, renderer_context)
