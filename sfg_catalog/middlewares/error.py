import json
import logging

from aiohttp.web import Response, middleware
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPMethodNotAllowed,
    HTTPNotFound
)

log = logging.getLogger(__name__)


@middleware
async def error_middleware(request, handler):
    try:
        return (await handler(request))
    except HTTPBadRequest as e:
        error_message = _get_message(e)
        error_reason = 'Bad Request'
        status = 400
        log.warning(error_message)
    except HTTPNotFound as e:
        error_message = _get_message(e)
        error_reason = 'Not Found'
        status = 404
    except HTTPMethodNotAllowed as e:
        error_message = _get_message(e)
        error_reason = 'Method Not Allowed'
        status = 405
    except HTTPConflict as e:
        error_message = _get_message(e)
        error_reason = 'Conflict'
        status = 409
    except Exception as e:
        log.exception('Generic error:{}'.format(e))
        raise

    error = {
        'error_message': error_message,
        'error_reason': error_reason
    }

    return Response(
        text=json.dumps(error),
        status=status,
        content_type='application/json'
    )


def _get_message(exception):
    return (
        exception.message
        if hasattr(exception, 'message')
        else str(exception)
    )
