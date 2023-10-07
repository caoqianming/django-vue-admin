"""
ASGI config for server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.utils.middlewares import TokenAuthMiddleware
import apps.ws.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            apps.ws.routing.websocket_urlpatterns
        )
    )
})