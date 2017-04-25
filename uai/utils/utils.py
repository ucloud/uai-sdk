import hashlib
import urlparse
import urllib
import json


def _verfy_ac(private_key, params):
    items = params.items()
    items.sort()

    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + str(value)
    params_data = params_data + private_key

    sign = hashlib.sha1()
    sign.update(params_data)
    signature = sign.hexdigest()

    return signature


def save_json(params, json_file):
    """ Save the params to the specified json_file
    """
    with open(json_file, 'w') as f:
        json.dump(params, f)
