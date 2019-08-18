import pytest

from sfg_catalog import app as _app
from sfg_catalog import loop as _loop
from sfg_catalog.resources.helpers import generate_resource_id
from sfg_catalog.resources.models import ResourceModel


@pytest.fixture(scope='session')
def loop():
    yield _loop
    _loop.close()


@pytest.fixture
def app(loop):
    return _app


@pytest.fixture(autouse=True)
def client(aiohttp_client, app):
    return app._loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def run_sync(loop):
    return loop.run_until_complete


@pytest.fixture
def mongo_db(app, loop, client):
    return app.mongo.db


@pytest.fixture(autouse=True)
async def clean_db(loop, mongo_db, run_sync):
    collections = await mongo_db.list_collection_names()

    for collection in collections:
        if collection.startswith('system'):
            continue
        await mongo_db.drop_collection(collection)

    return mongo_db


@pytest.fixture
def resource_dict():
    return {
        'id': 'ME888SHM70XSB-mega_boots-90',
        'sku': 'ME888SHM70XSB',
        'seller': 'mega_boots',
        'campaign_code': '90',
        'product_name': 'Bota Coturno em Couro Mega Boots 6017 Preto',
        'brand': 'Mega Boots',
        'category': 'calcados',
        'subcategory': 'calcados-masculinos',
        'size': '40',
        'list_price': 199.9,
        'price': 149.9
    }


@pytest.fixture
async def resource_saved(resource_dict):
    collection = ResourceModel(**resource_dict)
    await collection.save()

    return collection


@pytest.fixture
async def many_resources_saved(resource_dict):
    for i in range(20):
        for seller in ('dafiti', 'kanui', 'tricae'):
            resource_dict['sku'] = 'XPTO{}'.format(i)
            resource_dict['seller'] = seller
            resource_dict['id'] = generate_resource_id(
                'XPTO{}'.format(i), seller, resource_dict['campaign_code']
            )
            await ResourceModel(**resource_dict).save()
