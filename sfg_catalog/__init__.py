import asyncio

import yaml

from .main import build_app

yaml.warnings({'YAMLLoadWarning': False})

loop = asyncio.get_event_loop()
app = build_app(loop=loop)
