# Copyright 2017 The UAI-SDK Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import re

DataBackendUFile = 'UFile'
DataBackendUfs = 'UFS'

DataPathPatternUFile = '^((http:\\/\\/)|(https:\\/\\/))[\\w-]+((\\.ufile\\.ucloud\\.com\\.cn)|(\\.[\\w-]+\\.ufileos\\.com))\\/(/?[A-Za-z0-9\\-_\\.])+\\/'
DataPathPatternUfs = '^(((\\d{1,2})|(1\\d{2})|(2[0-4]\\d)|(25[0-5]))\\.){3}((\\d{1,2})|(1\\d{2})|(2[0-4]\\d)|(25[0-5])):\\/ufs-([0-9a-zA-Z]+\\/)'
DataPathPatternNfs = r'([\\w-\\.@]+\\/+)+'

UfsMountPointFormat = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\/ufs-\w+'
UfsPathFormat = r'(\w+\/)+'


def get_data_backend_name(data_path):
    ufile_pattern = re.compile(DataPathPatternUFile)
    ufs_pattern = re.compile(DataPathPatternUfs)
    if re.match(ufile_pattern, data_path) is not None:
        return DataBackendUFile
    elif re.match(ufs_pattern, data_path) is not None:
        return DataBackendUfs
    else:
        raise ValueError('Current data_path invalid, match none of available databackend patterns')


def concat_ufs_path(path, mount_point):
    mount_point_pattern = re.compile(UfsMountPointFormat)
    ufs_path_pattern = re.compile(UfsPathFormat)
    if mount_point_pattern.match(mount_point) is None:
        raise RuntimeError('UFS mount point should be in format x.x.x.x:/ufs-xxx')
    if ufs_path_pattern.match(path) is None:
        raise RuntimeError('UFS path should match xxx/xxx/')
    return mount_point + '/' + path