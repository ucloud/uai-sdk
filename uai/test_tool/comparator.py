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

import sys
import json

comparators = {}

def init_comparator(comparator, type):
    global comparators
    
    comparators[type] = comparator()

def get_comparator(type):
    global comparators
    return comparators[type]

"""
Default supported format includes:    
"""
TYPE_STR = "str"
TYPE_JSON = "json"

class BaseComparator(object):
    def __init__(self):
        pass

    def compare(self, src, resp):
        pass

class StrComparator(BaseComparator):
    def __init__(self):
        super(StrComparator, self).__init__()

    def compare(self, src, resp):
        target = resp.text
        if src == target:
            return True
        else:
            print("Compare error, expect {}; actual {}".format(src, target))
            return False

class JsonComparator(BaseComparator):
    def __init__(self):
        super(JsonComparator, self).__init__()

    def compare(self, src, resp):
        target = json.dumps(resp.json())

        #format str from unicode to no-unicode
        src = json.dumps(src)
        if src == target:
            return True
        else:
            print("Compare error, expect {}; actual {}".format(src, target))
            return False

init_comparator(StrComparator, TYPE_STR)
init_comparator(JsonComparator, TYPE_JSON)

