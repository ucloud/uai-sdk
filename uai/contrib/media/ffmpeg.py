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
import subprocess

from PIL import Image

class UaiVideoProcessor:

    def __init__(self, video_stream):
        filename = '/mnt/video.mp4'
        with open(filename, 'w+') as f:
            f.write(video_stream)
        self._video_path = filename

    def get_video_len(self):
        video_path = self._video_path
        cmd = "ffprobe -v error -show_entries format=duration   -of default=noprint_wrappers=1:nokey=1 " + video_path
        video_len = os.popen(cmd).readline()

        print(video_len)
        return float(video_len[:-1])

    def get_frame_rage(self):
        video_path = self._video_path
        cmd = "ffprobe -v 0 -of csv=p=0 -select_streams 0 -show_entries stream=r_frame_rate " + video_path
        rate = os.popen(cmd).readline()
        print(rate)
        
        rate = rate[:-1].split('/')
        return float(rate[0])/float(rate[1])

    def slice_video2image_basic(self, time_gap=10):
        video_len = self.get_video_len()
        video_rate = self.get_frame_rage()

        processes = []
        images = []
        start = 0
        video_path = self._video_path
        while start < video_len:
            hour = start / 3600
            minute = (start % 3600) / 60
            second = (start % 60)
            time = str(hour) + ":" + str(minute) + ":" + str(second)
            image_name = str(start) + "-image.jpeg"
            image_name = os.path.join('/tmp/', image_name)
            str_video = "ffmpeg -ss " + time + " -i " + video_path + " -r " + str(video_rate) + "  -frames:v 1 -f image2 " + image_name

            p = subprocess.Popen(str_video, shell=True)
            images.append(image_name)
            processes.append(p)

            start = start + time_gap

        exit_codes = [p.wait() for p in processes]
        return images

    def slice_video2image(self, time_gap=10):
        images = self.slice_video2image_basic(time_gap)
        img_list = []
        for imagefile in images:
            img = Image.open(imagefile)
            img_list.append(img)
            os.remove(imagefile)

        return img_list

    def cleanup(self):
        os.remove(self._video_path)

if __name__ == "__main__":
    video_p = UaiVideoFileProcessor("/data/data/zs12.mp4")
    images = video_p.slice_video2image_basic(30)
    print(images)