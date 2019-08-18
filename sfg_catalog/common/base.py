import json

from aiohttp.web import Response, View


class BaseView(View):

    id_fields = (
        '_id',
        'created_at',
        'updated_at'
    )

    def _clean_ids(self, content):
        if isinstance(content, list):
            [self._clean_ids(i) for i in content]
            return
        if not isinstance(content, dict):
            return
        for key in list(content.keys()):
            if key in self.id_fields:
                del content[key]
            else:
                self._clean_ids(content[key])

    def response(self, status_code, content=None):
        if isinstance(content, (dict, list)):
            self._clean_ids(content)
            content = json.dumps(content)

        content_type = 'application/json' if content else None

        return Response(
            status=status_code,
            text=content,
            content_type=content_type
        )
