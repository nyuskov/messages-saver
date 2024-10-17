"""
ASGI config for messages_saver project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from mails.consumers import MessageConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messages_saver.settings')

asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi_application,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('mails', MessageConsumer.as_asgi()),
        ])
    )
})
