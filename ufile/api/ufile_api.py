import threading
import time
import os
import Queue
from ucloud.ufile import downloadufile
from ucloud.ufile import getufilelist
from ucloud.ufile import putufile
from ucloud.logger import logger, set_log_file

set_log_file()
retry_max_fail = 3

def DownloadUfileBatch(public_key, private_key, bucket, prefix, save_dir, is_private=True, parall_num=8):
    handler = getufilelist.GetFileList(public_key, private_key)
    ret, resp = handler.getfilelist(bucket=bucket, prefix=prefix)
    if resp.status_code != 200:
        print("fail to get ufile list. bucket: {0}, prefix: {1}. [Error info]: {2}" .format(bucket, prefix, resp))
        return False

    file_cnt = len(ret['DataSet'])
    if file_cnt == 0:
        print("file cnt is 0, exit.")
        return

    print("start download ufile. bucket: {0}, prefix: {1}" .format(bucket, prefix))
    print("file count: {0}" .format(file_cnt))

    cnt = 0
    file_batch = []
    files_size = 0
    finished = 0
    parall_num = min(parall_num, file_cnt)
    for i, item in enumerate(ret['DataSet']):
        cnt = cnt + 1
        file_batch.append(item['FileName'])
        size = item['Size'] if 'Size' in item else 0
        files_size = files_size + size

        if cnt < parall_num and i != file_cnt - 1:
            continue
        start = time.time()
        res = downloadUfileBatch(public_key, private_key, bucket, prefix, file_batch, save_dir, is_private)
        end = time.time()
        if res != True:
            print (res)
            return False
        speed = files_size/((end-start)*1000)
        finished = finished + cnt
        file_batch = []
        cnt = 0
        files_size = 0
        print("\rtotal: %d, finished: %d, remain: %d, speed: %.2f KB/s" % (file_cnt, finished, file_cnt-finished, speed))
    print("download ufile succ. save files into {0}" .format(save_dir))
    return True

def downloadUfileBatch(public_key, private_key, bucket, prefix, key_list, save_dir, is_private):
    thread_group = []
    res_queue = Queue.Queue()
    for key in key_list:
        file_name = key[len(prefix):]
        save_file = "{0}/{1}".format(save_dir, file_name)
        t = threading.Thread(target=dowloadUfileSingle, args=(public_key, private_key, bucket, key, save_file, is_private,res_queue,))
        thread_group.append(t)

    for t in thread_group:
        t.start()
    for t in thread_group:
        t.join()

    while not res_queue.empty():
        res = res_queue.get()
        if res != True:
            return res
    return True

def dowloadUfileSingle(public_key, private_key, bucket, key, save_file, is_private, res_queue):
    file_dir = save_file[:save_file.rfind('/')]
    try:
        isExists = os.path.exists(file_dir)
        if not isExists:
            os.makedirs(file_dir)
    except Exception as e:
        err_info = "fail to create dir. dir: {0}. err: {1}".format(file_dir, e)
        res_queue.put(err_info)
        return

    handler = downloadufile.DownloadUFile(public_key, private_key)
    for i in range(retry_max_fail):
        ret, resp = handler.download_file(bucket, key, save_file, isprivate=is_private)
        if resp.status_code == 200:
            break
    if resp.status_code != 200:
        err_info = "fail to download ufile. file name: {0}. [Err Info]: {1}" .format(key, resp)
        res_queue.put(err_info)
    else:
        res_queue.put(True)

def DowloadUfileSingle(public_key, private_key, bucket, key, save_file, is_private):
    file_dir = save_file[:save_file.rfind('/')]
    try:
        isExists = os.path.exists(file_dir)
        if not isExists:
            os.makedirs(file_dir)
    except Exception as e:
        print("fail to create dir. dir: {0}. err: {1}".format(file_dir, e))
        return False

    handler = downloadufile.DownloadUFile(public_key, private_key)
    for i in range(retry_max_fail):
        ret, resp = handler.download_file(bucket, key, save_file, isprivate=is_private)
        if resp.status_code == 200:
            break
    if resp.status_code != 200:
        print("fail to download ufile. file name: {0}. [Err Info]: {1}" .format(key, resp))
        return False

    print("download from ufile succ. save path: {0}, ufile: [bucket: {1}, key: {2}]".format(save_file, bucket, key))
    return True

def UploadUfileBatch(public_key, private_key, bucket, prefix, local_dir, parall_num=8):
    file_list = []
    getFileList(local_dir, file_list)
    file_cnt = len(file_list)
    print("start upload to ufile. local dir: {0}, bucket: {1}, prefix: {2}".format(local_dir, bucket, prefix))
    print("file count: {0}".format(file_cnt))
    print(file_list)
    cnt = 0
    file_batch = []
    files_size = 0
    finished = 0
    parall_num = min(parall_num, file_cnt)
    for i, f in enumerate(file_list):
        cnt = cnt + 1
        file_batch.append(f)
        files_size = files_size + os.path.getsize(f)

        if cnt < parall_num and i != file_cnt - 1:
            continue
        start = time.time()
        res = uploadUfileBatch(public_key, private_key, bucket, prefix, file_batch, local_dir)
        end = time.time()
        if res != True:
            print (res)
            return False
        speed = files_size / ((end - start) * 1000)
        finished = finished + cnt
        file_batch = []
        cnt = 0
        files_size = 0
        print("\rtotal: %d, finished: %d, remain: %d, speed: %.2f KB/s" % (file_cnt, finished, file_cnt - finished, speed))
    print("uplaod to ufile succ. save files into [bucket: {0}, prefix: {1}]".format(bucket, prefix))
    return True

def uploadUfileBatch(public_key, private_key, bucket, prefix, file_list, local_dir):
    thread_group = []
    res_queue = Queue.Queue()
    for f in file_list:
        path = f[len(local_dir)+1:]
        key = "{0}{1}" .format(prefix, path)

        print(key)

        t = threading.Thread(target=uploadUfileSingle, args=(public_key, private_key, bucket, key, f, res_queue,))
        thread_group.append(t)

    for t in thread_group:
        t.start()
    for t in thread_group:
        t.join()

    while not res_queue.empty():
        res = res_queue.get()
        if res != True:
            return res
    return True

def uploadUfileSingle(public_key, private_key, bucket, key, local_file, res_queue):
    try:
        isExists = os.path.exists(local_file)
        if not isExists:
            err_info = "file is not exist. path: {0}. ".format(local_file)
            res_queue.put(err_info)
            return
    except Exception as e:
        err_info = e
        res_queue.put(err_info)
        return

    handler = putufile.PutUFile(public_key, private_key)
    for i in range(retry_max_fail):
        ret, resp = handler.putfile(bucket, key, local_file)
        if resp.status_code == 200:
            break
    if resp.status_code != 200:
        err_info = "fail to download ufile. file name: {0}. [Err Info]: {1}" .format(key, resp)
        res_queue.put(err_info)
    else:
        res_queue.put(True)

def UploadUfileSingle(public_key, private_key, bucket, key, local_file):
    try:
        isExists = os.path.exists(local_file)
        if not isExists:
            print("file is not exist. path: {0}. ".format(local_file))
            return False
    except Exception as e:
        print(e)
        return False

    handler = putufile.PutUFile(public_key, private_key)
    for i in range(retry_max_fail):
        ret, resp = handler.putfile(bucket, key, local_file)
        if resp.status_code == 200:
            break
    if resp.status_code != 200:
        print("fail to upload file to ufile. file name: {0}. [Err Info]: {1}" .format(key, resp))
    print("upload to ufile succ. path: {0}, ufile: [bucket: {1}, key: {2}]".format(local_file, bucket, key))
    return True


def getFileList(dir, file_list):
    isExists = os.path.exists(dir)
    if not isExists:
        return False
    if not os.path.isdir(dir):
        return False

    files = os.listdir(dir)
    for f in files:
        file_path = "{0}/{1}".format(dir, f)
        if (f[0] == '.'):
            continue
        if (not os.path.isdir(file_path)):
            file_list.append(file_path)
        else:
            getFileList(file_path, file_list)
