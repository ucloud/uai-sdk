# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

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
