import logging

import jinja2
from aiohttp import web
from aiohttp_swagger import setup_swagger

from .settings import LOGGING, TEMPLATES_DIR


def build_app(loop=None):
    app = web.Application(loop=loop, middlewares=get_middlewares())
    app.on_startup.append(load_plugins)
    app.on_cleanup.append(cleanup_plugins)
    register_routes(app)

    setup_swagger(
        app,
        swagger_url='/docs',
        swagger_from_file="docs/swagger.yaml"
    )

    setup_logging()

    return app


def setup_logging():
    logging.config.dictConfig(LOGGING)


def register_routes(app):
    pass


def get_middlewares():
    return []


async def load_plugins(app):
    pass


async def cleanup_plugins(app):
    pass
