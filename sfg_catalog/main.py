import logging

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_swagger import setup_swagger

from .common.mongo import Mongo
from .middlewares import error_middleware
from .resources.routes import resources_routes
from .settings import LOGGING, TEMPLATES_DIR


def build_app(loop=None):
    app = web.Application(loop=loop, middlewares=get_middlewares())
    app.on_startup.append(load_plugins)
    app.on_cleanup.append(cleanup_plugins)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
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
    resources_routes(app)


def get_middlewares():
    return [error_middleware]


async def load_plugins(app):
    app.mongo = Mongo()
    app.mongo.initialize(app._loop)


async def cleanup_plugins(app):
    if app.mongo:
        app.mongo.close()
