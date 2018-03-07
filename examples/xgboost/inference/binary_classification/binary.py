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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
from uai.arch.xgboost_model import XGBoostUcloudModel

import xgboost as xgb
import scipy.sparse

class BinaryClassModel(XGBoostUcloudModel):
    """ Binary Classification example model
    """
    def __init__(self, conf):
        super(BinaryClassModel, self).__init__(conf)

    def load_model(self):
        model_file = self.model_name
        bst = xgb.Booster({'nthread':1})
        bst.load_model(model_file)

        self.bst = bst

    def execute(self, data, batch_size):
        """
        Input
            data: an array of http requests, you can get the body by data[i].body
            batch_size: the array size of http data

        Output:
            an array of output (which can be read by django, such as string or json object),
              which is compatable with the 'Input' data array
        """
        row = []
        col = []
        dat = []

        for i in range(batch_size):
            line = data[i].body
            print(line)

            arr = line.split()
            for it in arr[1:]:
                k,v = it.split(':')
                row.append(i)
                col.append(int(k))
                dat.append(float(v))
        csr = scipy.sparse.csr_matrix((dat, (row, col)))
        dtest = xgb.DMatrix(csr)
        ypred = self.bst.predict(dtest)

        return ypred