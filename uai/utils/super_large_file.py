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

import sys, os
kilobytes = 1024
megabytes = kilobytes * 1024
chunksize = int(128 * megabytes)                   # default: roughly a floppy
readsize = 1024

#default chuck is 128MB
def split(fromdir, fromfile, todir, chunksize=chunksize): 
    if not os.path.exists(todir):                  # caller handles errors
        os.mkdir(todir)                            # make dir, read/write parts

    partnum = 0
    infile = os.path.join(fromdir, fromfile)
    input = open(infile, 'rb')                   # use binary mode on Windows
    while 1:                                       # eof=empty string from read
        chunk = input.read(chunksize)              # get next part <= chunksize
        if not chunk: break
        partnum  = partnum+1
        filename = os.path.join(todir, ('%s-part%04d' % (fromfile, partnum)))
        print(filename)
        fileobj  = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()                            # or simply open(  ).write(  )
    input.close()
    assert partnum <= 9999                         # join sort fails if 5 digits
    return partnum

def join(fromdir, fromfile, tofile):
    parts  = os.listdir(fromdir)
    output = open(tofile, 'wb')
    parts.sort()
    for filename in parts:
        if filename.startswith(fromfile) is False:
            continue
        filepath = os.path.join(fromdir, filename)
        fileobj  = open(filepath, 'rb')
        while 1:
            filebytes = fileobj.read(readsize)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close()
        os.remove(filepath)
    output.close()
