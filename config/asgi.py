"""
ASGI config for Ksatria Muslim project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
import os
import sys
from pathlib import Path

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path


# This allows easy placement of apps within the interior
# ksatria_muslim directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "ksatria_muslim"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()
# Apply ASGI middleware here.
# from helloworld.asgi import HelloWorldApplication
# application = HelloWorldApplication(application)
from ksatria_muslim.vimflowly.consumers import VimFlowlyConsumer


application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": URLRouter([
            path("ws/vim-flowly/socket", VimFlowlyConsumer.as_asgi(), name="vim-flowly-asgi"),
        ])
    }
)
