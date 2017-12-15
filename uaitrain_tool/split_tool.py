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

import os
import sys
from uai.utils.super_large_file import split

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print('Use: split.py [file-dir file-to-split target-dir]')
    else:
        if len(sys.argv) != 4:
            print('Use: split.py [file-dir file-to-split target-dir]')
            os.exit(-1)
        else:
            fromdir = sys.argv[1]                  # args in cmdline
            fromfile = sys.argv[2]
            todir = sys.argv[3]

        print('Splitting {0}{1} to {2} by 128MB'.format(fromdir, fromfile, todir))

        try:
            parts = split(fromdir, fromfile, todir)
        except:
            print('Error during split')
        else:
            print('Split finished: {0}, parts are in {1}'.format(parts, todir))

