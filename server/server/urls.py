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
from apps.system.views import FileViewSet, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

router = routers.DefaultRouter()
router.register('file', FileViewSet, basename="file")

schema_view = get_schema_view(
   openapi.Info(
      title="Django-Vue-Admin API",
      default_version='v1',
      contact=openapi.Contact(email="caoqianming@foxmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/black/', LogoutView.as_view(), name='token_black'),
    path('system/', include('apps.system.urls')),
    path('docs/', include_docs_urls(title="接口文档", authentication_classes=[], permission_classes=[])),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
] + \
static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

