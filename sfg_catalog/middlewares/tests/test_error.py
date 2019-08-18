import asyncio
import json

import pytest
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPError,
    HTTPMethodNotAllowed,
    HTTPNotFound
)

from sfg_catalog.middlewares import error_middleware


@asyncio.coroutine
def handler_raise_bad_request_code_400(request):
    raise HTTPBadRequest(reason='Invalid Payload')


@asyncio.coroutine
def handler_raise_not_found_code_404(request):
    raise HTTPNotFound(reason='Resource Not Found')


@asyncio.coroutine
def handler_raise_http_error_code_405(request):
    raise HTTPMethodNotAllowed(
        allowed_methods=('GET', 'PUT'),
        method='OPTIONS',
        reason='Method not allowed for this route'
    )


@asyncio.coroutine
def handler_raise_http_error_code_409(request):
    raise HTTPConflict(reason='Conflict resource')


@asyncio.coroutine
def handler_raise_http_error_code_500(request):
    raise HTTPError(reason='Internal error')


class TestErrorMiddleware:

    async def _build_middleware(self, request, handler):
        return (await error_middleware(request=request, handler=handler))

    async def test_middleware_returns_bad_request_code_400(self):
        response = await self._build_middleware(
            None, handler_raise_bad_request_code_400
        )

        assert response.status == 400
        assert response.text == json.dumps({
            'error_message': 'Invalid Payload',
            'error_reason': 'Bad Request'
        })

    async def test_middleware_returns_not_found_code_404(self):
        response = await self._build_middleware(
            None, handler_raise_not_found_code_404
        )

        assert response.status == 404
        assert response.text == json.dumps({
            'error_message': 'Resource Not Found',
            'error_reason': 'Not Found'
        })

    async def test_middleware_returns_error_code_405(self):
        response = await self._build_middleware(
            None, handler_raise_http_error_code_405
        )

        assert response.status == 405
        assert response.text == json.dumps({
            'error_message': 'Method not allowed for this route',
            'error_reason': 'Method Not Allowed'
        })

    async def test_middleware_returns_error_code_409(self):
        response = await self._build_middleware(
            None, handler_raise_http_error_code_409
        )

        assert response.status == 409
        assert response.text == json.dumps({
            'error_message': 'Conflict resource',
            'error_reason': 'Conflict'
        })

    async def test_middleware_returns_error_code_500(self):
        with pytest.raises(HTTPError) as e:
            await self._build_middleware(
                None, handler_raise_http_error_code_500
            )

        assert e.value.reason == 'Internal error'
