import asyncio
import logging
from collections import namedtuple
from json import JSONDecodeError

import aiohttp_jinja2
from aiohttp.web import View
from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp.web_request import FileField
from schema import SchemaError

from sfg_catalog.common.base import BaseView

from .helpers import generate_resource_id
from .models import ResourceModel

log = logging.getLogger(__name__)


class ListResourcesView(BaseView):

    fields_available_for_search = (
        'sku', 'seller', 'campagin_code', 'product_name', 'brand', 'size',
        'category', 'subcategory'
    )

    async def get(self):
        page, limit = self._prepare_pagination()
        query = self._prepare_query()

        resources = await ResourceModel.list(
            query,
            limit=limit,
            skip=limit * (page - 1)
        )
        return self.response(200, resources)

    def _prepare_pagination(self):
        page = self.request.query.get('page', '1')
        limit = self.request.query.get('limit', '20')

        page = int(page) if page.isdigit() else 1
        limit = int(limit) if limit.isdigit() else 20
        return page, limit

    def _prepare_query(self):
        query = {}
        for field in self.fields_available_for_search:
            search_term = self.request.query.get(field)
            if search_term:
                query[field] = {'$regex': '{}'.format(search_term)}

        return query


class ListResourcesOnScreenView(View):

    @aiohttp_jinja2.template('index.html')
    async def get(self):
        resources = await ResourceModel.list()
        return {'resources': resources}


class ResourceView(BaseView):

    async def get(self):
        resource = await self._retrieve_resource()
        return self.response(200, resource)

    async def post(self):
        payload = await self._validate_payload()

        payload['id'] = generate_resource_id(
            payload['sku'],
            payload['seller'],
            payload['campaign_code']
        )

        result = await ResourceModel.get(id=payload['id'])
        if result:
            raise HTTPConflict(
                reason='It was not possible to create a resource {}'
                       ' that already exists'.format(payload['id'])
            )

        resource = ResourceModel(**payload)
        await resource.save()

        return self.response(201, resource)

    async def put(self):
        payload = await self._validate_payload()
        payload = self._clean_not_editable_fields(payload)

        resource = await self._retrieve_resource()

        resource.update(payload)
        await resource.save()

        return self.response(200, resource)

    async def patch(self):
        resource = await self._retrieve_resource()

        try:
            payload = await self.request.json()
            payload = self._clean_not_editable_fields(payload)
            resource.update(payload)
            ResourceModel.schema.validate(resource.to_dict())
        except SchemaError as error:
            raise HTTPBadRequest(reason=error.code)
        except JSONDecodeError:
            raise HTTPBadRequest(reason='Invalid payload')

        await resource.save()

        return self.response(200, resource)

    async def delete(self):
        resource = await self._retrieve_resource()

        await resource.delete()
        return self.response(204)

    async def _retrieve_resource(self):
        resource_id = self.request.match_info.get('id')
        resource = await ResourceModel.get(id=resource_id)
        if not resource:
            raise HTTPNotFound(
                reason='Resource {} not found'.format(resource_id)
            )
        return resource

    async def _validate_payload(self):
        try:
            payload = await self.request.json()
            ResourceModel.schema.validate(payload)
        except SchemaError as error:
            raise HTTPBadRequest(reason=error.code)
        except JSONDecodeError:
            raise HTTPBadRequest(reason='Invalid payload')
        return payload

    def _clean_not_editable_fields(self, payload):
        not_editable_fields = ('id', 'sku', 'seller', 'campaign_code')
        return {
            k: v
            for k, v in payload.items()
            if k not in not_editable_fields
        }


class UploadResourcesView(BaseView):

    resource = namedtuple(
        'Resource',
        (
            'sku', 'seller', 'campaign_code', 'product_name', 'brand',
            'category', 'subcategory', 'size', 'list_price', 'price'
        )
    )

    async def post(self):
        data = await self.request.post()

        if (
            not data.get('csv_file') or
            not isinstance(data['csv_file'], FileField)
        ):
            raise HTTPBadRequest(reason='Not a valid csv file')

        resources = await self._read_file(data['csv_file'].file.read())

        tasks = [
            self._create_or_update_resource(resource)
            for resource in resources
        ]

        resources_status = await asyncio.gather(*tasks)
        resources_failed = [r for r in resources_status if r is not None]

        if resources_failed:
            return self.response(207, {'resources_failed': resources_failed})
        return self.response(204)

    async def _read_file(self, csv_content):
        resources = []

        lines = csv_content.decode('utf-8').strip().split('\n')

        for line in lines:
            resources.append(self.resource(*line.split(',')))

        return resources

    async def _create_or_update_resource(self, data):
        try:
            resource_payload = ResourceModel.schema.validate(data._asdict())
        except SchemaError as error:
            return 'Fail to create or update {}, reason: {}'.format(
                data, error.code
            )

        resource_payload['id'] = generate_resource_id(
            data.sku, data.seller, data.campaign_code
        )

        # recalculates resource price
        resource_payload['price'] = float(format(
            (resource_payload['list_price'] - resource_payload['price']) * 1.1,
            '.2f'
        ))

        await ResourceModel._create_or_update(
            resource_payload['id'], resource_payload
        )
