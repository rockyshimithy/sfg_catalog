import logging

from schema import And, Optional, Schema, Use

from sfg_catalog.common.models import BaseModel

log = logging.getLogger(__name__)


class ResourceModel(BaseModel):

    collection_name = 'resources'

    schema = Schema({
        Optional('_id'): Use(str),
        Optional('id'): str,
        'sku': str,
        'seller': str,
        'campaign_code': str,
        'product_name': str,
        'brand': str,
        'category': str,
        'subcategory': str,
        'size': str,
        'list_price': And(
            Use(float),
            lambda value: False if value <= 0 else True,
            error='List price should be greater than 0'
        ),
        'price': And(
            Use(float),
            lambda value: False if value <= 0 else True,
            error='Price should be greater than 0'
        )
    }, ignore_extra_keys=True)
