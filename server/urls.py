"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.views.generic import TemplateView

schema_view = get_schema_view(
    openapi.Info(
        title=settings.SYS_NAME,
        default_version=settings.SYS_VERSION,
        contact=openapi.Contact(email="caoqianming@foxmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[],
    url=settings.BASE_URL
)

urlpatterns = [
    # django后台
    path('django/admin/doc/', include('django.contrib.admindocs.urls')),
    path('django/admin/', admin.site.urls),
    path('django/api-auth/', include('rest_framework.urls')),

    # api
    path('', include('apps.auth1.urls')),
    path('', include('apps.system.urls')),
    path('', include('apps.wf.urls')),
    path('', include('apps.utils.urls')),
    path('', include('apps.ops.urls')),



    # api文档
    path('api/docs/', include_docs_urls(title="接口文档",
         authentication_classes=[], permission_classes=[])),
    path('api/swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    # 前端页面入口
    path('', TemplateView.as_view(template_name="index.html")),
] + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
