import os

def find_java_executable():
    list = []
    # 指定要搜索的路径
    search_path = "C:\\Program Files\\Java"

    # 遍历指定路径下的所有文件夹
    for root, dirs, files in os.walk(search_path):
        for file in files:
            # 如果找到 java.exe 文件，则返回完整路径
            if file == "java.exe":
                list.append(os.path.join(root, file))
    return list