#coding:utf8
import hashlib
import tarfile
import json

GATEWAY_DEFAULT='Default'

def _verfy_ac(private_key, params):
    items = params.items()
    items = sorted(items, reverse=False) # must use reverse=False to adapt python3

    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + val_to_str(value)
    params_data = params_data + private_key

    sign = hashlib.sha1()
    sign.update(params_data.encode('utf-8')) # must encode to adapt python3
    signature = sign.hexdigest()
    print("Signature",signature)
    return signature

def val_to_str(val):
    """ Transform value to string
    """
    if type(val) == bool:
        return 'true' if val == True else 'false'

    if type(val) != list:
        return str(val)

    # if value is type of list, then tansform into values split by ','
    val_arr = [val_to_str(item_val) for item_val in val]
    return ','.join(val_arr)

def save_json(params, json_file):
    """ Save the params to the specified json_file
    """
    with open(json_file, 'w') as f:
        json.dump(params, f)

def unpack_tar(tar_file):
    try:
        tar_file = tarfile.open(tarfile)
    except Exception as e:
        print(e)
        raise OSError
    tar_file.extractall()

def str_to_bool(str):
    return str.lower() in ("true", "t", "yes", "1")
