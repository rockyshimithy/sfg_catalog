

def generate_resource_id(sku, seller, campaign_code):
    return '{}-{}-{}'.format(sku, seller, campaign_code)
