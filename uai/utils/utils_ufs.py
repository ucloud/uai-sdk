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

import re

UFS_MOUNT_POINT_FORMAT = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\/ufs-\w+'
UFS_PATH_FORMAT = r'(\w+\/)+'

def concat_ufs_path(path, mount_point):
    mount_point_pattern = re.compile(UFS_MOUNT_POINT_FORMAT)
    path_pattern = re.compile(UFS_PATH_FORMAT)

    if mount_point_pattern.match(mount_point) is None:
        raise RuntimeError("UFS mount point should be in format x.x.x.x:/ufs-xxx")

    if path_pattern.match(path) is None:
        raise RuntimeError("UFS path should match xxx/xxx/")

    return mount_point + '/' + path
