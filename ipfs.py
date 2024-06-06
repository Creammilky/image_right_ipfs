import ipfs_api
import os
import shutil
from pathlib import Path
import time
# 上传文件到链
def upload_file(file_path: str):
    file_cid = ipfs_api.publish(file_path)
    return file_cid


# 下载文件到本地
def download_file(file_name: str, file_cid: str, path='.'):
    # 下载文件到指定路径，假设ipfs_api.download函数会将文件下载到指定目录并返回下载文件的路径
    ipfs_api.download(file_cid, path)
    file_path = Path(os.path.join(path, file_cid))  # 替换为你的文件路径
    timeout = 30  # 设置超时时间（秒）

    start_time = time.time()
    while not file_path.exists() and (time.time() - start_time < timeout):
        time.sleep(0.5)  # 每0.5秒检查一次文件是否存在

    if file_path.exists():
        print(f"File {file_name}, {file_cid} succeed download")
    else:
        print(f"File {file_name}, {file_cid} timeout in {timeout}s")
    # 获取下载文件的原始后缀
    original_extension = os.path.splitext(path)[1]
    # 如果用户未提供后缀，则使用原始文件的后缀
    if not os.path.splitext(file_name)[1]:
        file_name += original_extension
    # 构建新的文件路径
    new_filepath = os.path.join(path, file_name)
    # 重命名下载的文件
    shutil.move(os.path.join(path, file_cid), new_filepath)


# 直接预览ipfs文件内容（仅限文本）
def show_text(file_cid: str):
    text = ipfs_api.read(file_cid)
    return text


# 任何数据在网络中的节点上都可能会被删除或丢失。
# 为了确保特定内容（例如文件或数据块）始终保存在特定节点上，
# 固定内容后，该内容及其相关的数据块将不会被垃圾收集机制删除，
# 从而保证数据的可用性和持久性。
def pin_file(file_cid: str):
    ipfs_api.pin(file_cid)


# 取消固定
def unpin_file(file_cid: str):
    ipfs_api.unpin(file_cid)


# 从此IPFS节点的存储中删除具有给定CID的内容（未固定）
def remove_file(file_cid: str):
    pinned_cids = ipfs_api.pins(True, None)
    print()
    if file_cid in pinned_cids:
        print(f"文件 {file_cid} 被固定，无法删除。")
        return 1
    else:
        ipfs_api.remove(file_cid)
        return 2


# 创建ipns，并关联文件,随后上传
def create_ipns(name: str, path):
    ipfs_api.create_ipns_record(name)
    ipfs_api.update_ipns_record(name, path)
    return ipfs_api.predict_cid(path)


# 已有ipns的情况下更新绑定文件（通过路径更新）
def update_ipns_path(name: str, path):
    ipfs_api.update_ipns_record(name, path)


# 已有ipns的情况下更新绑定文件（通过cid更新）
def update_ipns_cid(name: str, file_cid):
    ipfs_api.update_ipns_record_from_cid(name, file_cid)


# IPFS PubSub
def pubsub(name: str, file_cid):
    ipfs_api.pubsub_subscribe("test", print)  # print is the eventhandler
    ipfs_api.pubsub_publish("test", "Hello there!")

if __name__ == '__main__':
    #file_cid = upload_file('/home/user/ipfs_script/upload/test.txt')
    #print(file_cid)
    id = remove_file('QmeomffUNfmQy76CQGy9NdmqEnnHU9soCexBnGU3ezPHVH')
    print(id)
