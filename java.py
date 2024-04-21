import os
import platform


def find_java_executable():
    global search_path
    java_list = []
    # 指定要搜索的路径
    if platform.system() == "Windows":
        search_path = "C:\\Program Files\\Java"
    elif platform.system() == "Linux":
        search_path = "/usr/bin/"
    # 遍历指定路径下的所有文件夹
    for root, dirs, files in os.walk(search_path):
        for file in files:
            # 如果找到 java.exe 文件，则返回完整路径
            if platform.system() == "Windows":
                if file == "java.exe":
                    java_list.append(os.path.join(root, file))
                else:
                    pass
            else:
                if file == "java":
                    java_list.append(os.path.join(root, file))
                else:
                    pass
    return java_list
