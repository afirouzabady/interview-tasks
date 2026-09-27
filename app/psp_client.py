import os

import requests

ACME_BASE_URL = os.getenv("ACME_BASE_URL", "http://127.0.0.1:9099")


def fetch_order(order_ref):
    """Look up an order in Acme Pay. Used when a webhook omits the seller."""
    response = requests.get(ACME_BASE_URL + "/v1/orders/" + order_ref)
    return response.json()
