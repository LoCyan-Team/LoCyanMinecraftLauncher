import os
import requests
from tqdm import tqdm

def download_file(url, file_path):
    # 创建目录
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 发送 GET 请求获取文件大小
    response = requests.head(url)
    file_size = int(response.headers.get('Content-Length', 0))

    # 使用 stream=True 来确保下载时以流的形式进行，这样可以避免将整个文件加载到内存中
    response = requests.get(url, stream=True)
    
    # 使用 tqdm 显示下载进度
    with open(file_path, 'wb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_path.split('/')[-1]) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: # 过滤掉空的 chunk
                    f.write(chunk)
                    pbar.update(len(chunk))
