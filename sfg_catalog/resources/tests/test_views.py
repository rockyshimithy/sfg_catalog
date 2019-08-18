import io

import pytest

from sfg_catalog.resources.models import ResourceModel


class TestListResourcesView:

    async def test_get_resources(self, client, resource_dict, resource_saved):
        response = await client.get('/resources/')

        payload = await response.json()

        assert payload == [resource_dict]
        assert response.status == 200

    async def test_get_resources_is_empty(self, client):
        response = await client.get('/resources/')

        payload = await response.json()

        assert payload == []
        assert response.status == 200

    async def test_get_resources_first_page(
        self,
        client,
        many_resources_saved
    ):
        response = await client.get('/resources/?page=1')

        payload = await response.json()

        assert len(payload) == 20
        assert response.status == 200

    async def test_get_resources_second_page(
        self,
        client,
        many_resources_saved
    ):
        response = await client.get('/resources/?page=2')

        payload = await response.json()

        assert len(payload) == 20
        assert response.status == 200

    async def test_get_resources_sixth_page_with_limit_5(
        self,
        client,
        many_resources_saved
    ):
        response = await client.get('/resources/?page=6&limit=5')

        payload = await response.json()
        resources = await ResourceModel.list(limit=5, skip=25)

        assert len(payload) == 5
        assert [p['id'] for p in payload] == [r.to_dict()['id'] for r in resources]  # noqa
        assert response.status == 200

    @pytest.mark.parametrize('seller', ['tricae', 'kanui', 'dafiti'])
    async def test_get_resources_filtering_by_seller(
        self,
        client,
        seller,
        many_resources_saved
    ):
        response = await client.get('/resources/?seller={}'.format(seller))

        payload = await response.json()
        resources = await ResourceModel.list(
            {'seller': {'$regex': '{}'.format(seller)}}
        )

        assert len(payload) == 20
        assert [p['seller'] for p in payload] == [r.to_dict()['seller'] for r in resources]  # noqa
        assert response.status == 200

    @pytest.mark.parametrize('seller', ['ric', 'anu', 'fit'])
    async def test_get_resources_filtering_partially_by_seller_and_partially_by_sku(  # noqa
        self,
        client,
        seller,
        many_resources_saved
    ):
        response = await client.get(
            '/resources/?seller={}&sku=0'.format(seller)
        )

        payload = await response.json()
        resources = await ResourceModel.list({
            'seller': {'$regex': '{}'.format(seller)},
            'sku': {'$regex': '0'}
        })

        assert len(payload) == 2
        assert [p['seller'] for p in payload] == [r.to_dict()['seller'] for r in resources]  # noqa
        assert response.status == 200


class TestListResourcesOnScreenView:

    async def test_get_resources_on_screen(
        self,
        client,
        resource_dict,
        resource_saved
    ):
        response = await client.get('/resources/list/')

        content_response = await response.text()

        assert resource_dict['sku'] in content_response
        assert response.status == 200

    async def test_get_resources_is_empty(
        self,
        client
    ):
        response = await client.get('/resources/list/')

        content_response = await response.text()

        assert 'There are no resources to display' in content_response
        assert response.status == 200


class TestResourceView:

    @pytest.fixture
    def expected_response_not_found(self):
        return {
            'error_message': 'Resource ME888SHM70XSB-mega_boots-90 not found',
            'error_reason': 'Not Found'
        }

    async def test_get_a_resource(self, client, resource_dict, resource_saved):
        response = await client.get(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        payload = await response.json()

        assert payload == resource_dict
        assert response.status == 200

    async def test_get_a_resource_not_found(
        self,
        client,
        resource_dict,
        expected_response_not_found
    ):
        response = await client.get(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        payload = await response.json()

        assert payload == expected_response_not_found
        assert response.status == 404

    async def test_create_a_resource(self, client, resource_dict):
        response = await client.post('/resources/', json=resource_dict)

        resource_on_db = await ResourceModel.get(id=resource_dict['id'])
        resource = resource_on_db.to_dict()
        del resource['_id']

        assert resource_dict == resource
        assert response.status == 201

    @pytest.mark.parametrize(
        'field,value',
        [
            ('product_name', 55), ('brand', {}), ('category', 22.4),
            ('subcategory', 11), ('size', ()),
            ('list_price', []), ('price', None)
        ]
    )
    async def test_create_a_resource_bad_request_with_invalid_data_types(
        self,
        field,
        value,
        client,
        resource_dict
    ):
        resource_dict[field] = value

        response = await client.post('/resources/', json=resource_dict)

        payload = await response.json()

        assert 'should be' in payload['error_message']
        assert response.status == 400

    @pytest.mark.parametrize(
        'field',
        [
            'sku', 'seller', 'campaign_code', 'product_name', 'brand',
            'category', 'subcategory', 'size', 'list_price', 'price'
        ]
    )
    async def test_create_a_resource_bad_request_without_fields(
        self,
        field,
        client,
        resource_dict
    ):
        expected_response_bad_request = {
            'error_message': "Missing key: '{}'".format(field),
            'error_reason': 'Bad Request'
        }
        del resource_dict[field]

        response = await client.post('/resources/', json=resource_dict)

        payload = await response.json()

        assert payload == expected_response_bad_request
        assert response.status == 400

    async def test_create_a_resource_bad_request_without_request_body(
        self,
        client
    ):
        expected_response_bad_request = {
            'error_message': 'Invalid payload',
            'error_reason': 'Bad Request'
        }

        response = await client.post('/resources/')

        payload = await response.json()

        assert payload == expected_response_bad_request
        assert response.status == 400

    async def test_create_a_resource_conflict(
        self,
        client,
        resource_dict,
        resource_saved
    ):
        expected_response_conflict = {
            'error_message': 'It was not possible to create a resource ME888SHM70XSB-mega_boots-90 that already exists',   # noqa
            'error_reason': 'Conflict'
        }

        response = await client.post('/resources/', json=resource_dict)

        payload = await response.json()

        assert payload == expected_response_conflict
        assert response.status == 409

    @pytest.mark.parametrize(
        'field,value',
        [
            ('product_name', 'Camisa estampa XPTO'), ('brand', 'Fulano'),
            ('category', 'roupa'), ('subcategory', 'camisa'), ('size', 'M'),
            ('list_price', 49.9), ('price', 25.5)
        ]
    )
    async def test_update_a_resource(
        self,
        field,
        value,
        client,
        resource_dict,
        resource_saved
    ):
        resource_dict[field] = value

        response = await client.put(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=resource_dict
        )

        resource_on_db = await ResourceModel.get(id=resource_dict['id'])
        resource = resource_on_db.to_dict()
        del resource['_id']

        assert resource_dict == resource
        assert response.status == 200

    @pytest.mark.parametrize(
        'field,value',
        [
            ('product_name', 55), ('brand', {}), ('category', 22.4),
            ('subcategory', 11), ('size', ()),
            ('list_price', []), ('price', None)
        ]
    )
    async def test_update_a_resource_bad_request_with_invalid_data_types(
        self,
        field,
        value,
        client,
        resource_dict,
        resource_saved
    ):
        resource_dict[field] = value

        response = await client.put(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=resource_dict
        )

        payload = await response.json()

        assert 'should be' in payload['error_message']
        assert response.status == 400

    @pytest.mark.parametrize(
        'field',
        [
            'sku', 'seller', 'campaign_code', 'product_name', 'brand',
            'category', 'subcategory', 'size', 'list_price', 'price'
        ]
    )
    async def test_update_a_resource_bad_request_without_fields(
        self,
        field,
        client,
        resource_dict,
        resource_saved
    ):
        expected_response_bad_request = {
            'error_message': "Missing key: '{}'".format(field),
            'error_reason': 'Bad Request'
        }
        del resource_dict[field]

        response = await client.put(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=resource_dict
        )

        payload = await response.json()

        assert payload == expected_response_bad_request
        assert response.status == 400

    async def test_update_a_resource_bad_request_without_request_body(
        self,
        client,
        resource_dict,
        resource_saved
    ):
        expected_response_bad_request = {
            'error_message': 'Invalid payload',
            'error_reason': 'Bad Request'
        }

        response = await client.put(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        payload = await response.json()

        assert payload == expected_response_bad_request
        assert response.status == 400

    async def test_update_a_resource_not_found(
        self,
        client,
        resource_dict,
        expected_response_not_found
    ):
        response = await client.put(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=resource_dict
        )

        payload = await response.json()

        assert payload == expected_response_not_found
        assert response.status == 404

    @pytest.mark.parametrize(
        'field,value',
        [
            ('product_name', 'Camisa estampa XPTO'), ('brand', 'Fulano'),
            ('category', 'roupa'), ('subcategory', 'camisa'), ('size', 'M'),
            ('list_price', 49.9), ('price', 25.5)
        ]
    )
    async def test_partially_update_a_resource(
         self,
         field,
         value,
         client,
         resource_dict,
         resource_saved
    ):
        request_payload = {field: value}

        response = await client.patch(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=request_payload
        )

        resource_on_db = await ResourceModel.get(id=resource_dict['id'])

        assert request_payload[field] == resource_on_db[field]
        assert response.status == 200

    @pytest.mark.parametrize(
        'field,value',
        [
            ('product_name', 55), ('brand', {}), ('category', 22.4),
            ('subcategory', 11), ('size', ()),
            ('list_price', []), ('price', None)
        ]
    )
    async def test_partially_update_a_resource_bad_request_with_invalid_data_types(  # noqa
        self,
        field,
        value,
        client,
        resource_dict,
        resource_saved
    ):
        request_payload = {field: value}

        response = await client.patch(
            '/resources/{id}/'.format(id=resource_dict['id']),
            json=request_payload
        )

        payload = await response.json()

        assert 'should be' in payload['error_message']
        assert response.status == 400

    async def test_partially_update_a_resource_bad_request_without_request_body(  # noqa
        self,
        client,
        resource_dict,
        resource_saved
    ):
        expected_response_bad_request = {
            'error_message': 'Invalid payload',
            'error_reason': 'Bad Request'
        }

        response = await client.patch(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        payload = await response.json()

        assert payload == expected_response_bad_request
        assert response.status == 400

    async def test_delete_resource(
        self,
        client,
        resource_dict,
        resource_saved
    ):
        response = await client.delete(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        assert await ResourceModel.count() == 0
        assert response.status == 204

    async def test_delete_resource_not_found(
        self,
        client,
        resource_dict
    ):
        response = await client.delete(
            '/resources/{id}/'.format(id=resource_dict['id'])
        )

        assert await ResourceModel.count() == 0
        assert response.status == 404


class TestUploadResourcesView:

    @pytest.fixture
    def csv_file(self):
        return io.BytesIO(
            b'1111,dafiti,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n1111,tricae,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n1111,kanui,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n2222,dafiti,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n2222,tricae,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n2222,kanui,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n3333,dafiti,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n3333,tricae,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n3333,kanui,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n4444,dafiti,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n4444,tricae,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n4444,kanui,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,dafiti,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,tricae,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,kanui,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n6666,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n6666,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n6666,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n7777,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n7777,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n7777,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n8888,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n8888,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n8888,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n'  # noqa
        )

    @pytest.fixture
    def csv_file_with_invalid_data(self):
        return io.BytesIO(
            b'sku,seller,campaign_code,product_name,brand,category,subcategory,size,list_price,price\n1111,dafiti,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n1111,tricae,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n1111,kanui,buscape,Cinto couro com fivela de metal,bananas de pijama,acessorios,cinto,\xc3\xbanico,99.9,20.00\n2222,dafiti,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n2222,tricae,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n2222,kanui,home_site,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,P,65.50,15.50\n3333,dafiti,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n3333,tricae,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n3333,kanui,email_marketing,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,M,65.50,15.50\n4444,dafiti,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n4444,tricae,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n4444,kanui,zoom,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,dafiti,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,tricae,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n5555,kanui,buscape,Cueca de bolinhas,Xuxa s\xc3\xb3 para encapetadinhos,roupas,cueca,G,65.50,15.50\n6666,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n6666,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n6666,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,P,299.99,55.99\n7777,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n7777,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n7777,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,M,299.99,55.99\n8888,dafiti,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n8888,tricae,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n8888,kanui,google_shopping,Jaqueta couro que n\xc3\xa3o \xc3\xa9 couro,Nice,roupas,jaqueta,G,299.99,55.99\n'  # noqa
        )

    async def test_upload_file_with_success(
        self,
        client,
        csv_file
    ):
        data = {'csv_file': csv_file}

        response = await client.post('/resources/csv_import/', data=data)

        assert response.status == 204

    async def test_upload_file_with_some_resource_failed(
        self,
        client,
        csv_file_with_invalid_data
    ):
        expected_response = {'resources_failed': [
            "Fail to create or update Resource(sku='sku', seller='seller', "
            "campaign_code='campaign_code', product_name='product_name', "
            "brand='brand', category='category', subcategory='subcategory', "
            "size='size', list_price='list_price', price='price'), "
            "reason: List price should be greater than 0"
        ]}
        data = {'csv_file': csv_file_with_invalid_data}

        response = await client.post('/resources/csv_import/', data=data)

        payload = await response.json()

        assert payload == expected_response
        assert response.status == 207

    async def test_upload_file_bad_request_without_file(
        self,
        client
    ):

        data = {'csv_file': None}

        response = await client.post('/resources/csv_import/', data=data)

        assert response.status == 400

    async def test_upload_file_bad_request_without_key_form(
        self,
        client
    ):

        response = await client.post('/resources/csv_import/', data={})

        assert response.status == 400
