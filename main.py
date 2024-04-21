import json
import zipfile
import uuid
from download import *
from MicAuth import *
from java import *

print("欢迎使用 LoCyanFrp 联机大厅配套联机软件")
mcDir = input("请输入MC游戏文件夹(回车默认为官方启动器安装文件夹, 例如 E:\\MC\\.minecraft 结尾不带 \\): ")
versionList = []
notFoundFiles = {}
downloadFlag = False
maxMem = "2048m"

# 游戏目录
if mcDir == "":
    if platform.system().lower() == "Windows":
        mcDir = os.getcwd() + "%appdata%\\.minecraft"
    elif platform.system().lower() != "Linux":
        mcDir = os.getcwd() + "~/.minecraft"

# 游戏版本
for root, dirs, files in os.walk(mcDir + "/versions/"):
    versionList.append(dirs)
a = 1
for i in versionList[0]:
    print("( ", a, " ) ", i)
    a += 1
choose = int(input("请选择你要启动的游戏版本: "))
version = versionList[0][choose - 1]

javaList = find_java_executable()
if len(javaList) == 0:
    print("未在 C:/Program Files/Java 找到 Java 可执行文件, 请手动指定 Java.exe 路径")
elif len(javaList) == 1:
    javaPath = javaList[0]
else:
    a = 1
    for i in javaList:
        print("( ", a, " ) ", i)
        a += 1
    choose = int(input("请选择你要使用的 Java 版本: "))
    javaPath = javaList[choose - 1]

userType = input("请选择用户类型(1: 微软登录, 2: 离线登录): ")
if userType == "1":
    userInfo = get_code()
    username = userInfo["username"]
    userUuid = userInfo["uuid"]
else:
    username = input("请输入用户名: ")
    userUuid = uuid.uuid4()


def unpress(file_name, un_press_path, download_url):
    global downloadFlag
    zip = None
    try:
        zip = zipfile.ZipFile(file_name)
    except FileNotFoundError:
        downloadFlag = True
        notFoundFiles[file_name] = download_url
    if not downloadFlag:
        for z in zip.namelist():
            if not os.path.exists(un_press_path):
                os.mkdir(un_press_path)
            zip.extract(z, un_press_path)
        zip.close()


def get_os_type():
    system_type = platform.system()
    if system_type == "Windows":
        return "windows"
    elif system_type == "Darwin":
        return "osx"
    elif system_type == "Linux":
        return "linux"
    else:
        return None


def find_version(mcDir: str, version: str) -> bool:
    return os.path.exists(f"{mcDir}/versions/{version}/{version}.json")


def getPath(s: str) -> str:
    # org.ow2.asm:asm-analysis:9.6
    s = s.split(":")
    version = s[-1]
    fileName = s[1]
    path = (
            s[0].replace(".", "/")
            + "/"
            + fileName
            + "/"
            + version
            + "/"
            + fileName
            + "-"
            + version
            + ".jar"
    )
    return path


def run(javaPath: str, mcDir: str, version: str, username: str) -> None:
    if find_version(mcDir, version) != True:
        print(mcDir)
        print(version)

    dic = {}
    with open(f"{mcDir}/versions/{version}/{version}.json", "r") as f:
        dic = json.loads(f.read())

    if len(dic) == 0:
        print("解析 JSON 失败")
        exit()
    nativePath = f"{mcDir}/versions/{version}/{version}-natives"

    # 解压支持库至指定位置
    for i in dic["libraries"]:
        if i.get("downloads") == None:
            continue
        if "classifiers" in i["downloads"]:
            for native in i["downloads"]:
                if native == "artifact":
                    # 非本地库 （forge，optifine）
                    directPath = nativePath
                    path = i["downloads"][native]["path"]
                    filePath = f"{mcDir}/libraries/{path}"
                    print(filePath)
                    unpress(filePath, directPath, i["downloads"][native]["url"])
                elif native == "classifiers":
                    # 本地库
                    for m in i["downloads"][native].keys():
                        if m == "natives-" + get_os_type():
                            path = i["downloads"][native][m]["path"]
                            filePath = f"{mcDir}/libraries/{path}"
                            unpress(filePath, filePath.replace(".jar", ""), i["downloads"][native][m]["url"])
                            continue
                        if m == "javadoc":
                            path = i["downloads"][native][m]["path"]
                            filePath = f"{mcDir}/libraries/{path}"
                            unpress(filePath, filePath.replace(".jar", ""), i["downloads"][native][m]["url"])
                            continue
                        if m == "sources":
                            path = i["downloads"][native][m]["path"]
                            filePath = f"{mcDir}/libraries/{path}"
                            unpress(filePath, filePath.replace(".jar", ""), i["downloads"][native][m]["url"])
                            continue

    if downloadFlag:
        for i in notFoundFiles.keys():
            download_file(notFoundFiles[i], i)
        print("游戏资源下载完成，请尝试重启本软件")
        exit()

    jvmArgs = f'"{javaPath}" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump -Djava.library.path={nativePath} -Djna.tmpdir={nativePath} -Dorg.lwjgl.system.SharedLibraryExtractPath={nativePath} -Dio.netty.native.workdir={nativePath} -Dminecraft.launcher.brand=LoCyanLauncher -Dminecraft.launcher.version=1.0.0 -cp'
    classPath = ""
    classPath += '"'
    for i in dic["libraries"]:
        if i.get("downloads") == None or i.get("downloads") == {}:
            path = mcDir + "/libraries/" + getPath(i["name"])
            classPath += path + ";"
            continue
        if not "classifiers" in i["downloads"]:
            path = i["downloads"]["artifact"]["path"]
            normal = f"{mcDir}/libraries/{path}"
            classPath += normal + ";"
    classPath += f'{mcDir}/versions/{version}/{version}.jar"'
    # 参数拼接
    jvmArgs += " " + classPath + " -Xmx" + maxMem + " -Xmn256m"
    mc_args = ""
    mc_args += dic["mainClass"] + " "

    # 适配旧版本
    if dic.get("minecraftArguments") == "" or dic.get("minecraftArguments") == None:
        # 高版本
        for i in dic["arguments"]["game"]:
            if isinstance(i, str):
                mc_args += i + " "
            elif isinstance(i, dict):
                if isinstance(i["value"], list):
                    for a in i["value"]:
                        mc_args += a + " "
                else:
                    mc_args += i["value"] + " "
    else:
        # 低版本, 可以用 split 分割成和高版本一样的参数
        for i in dic["minecraftArguments"].split(" "):
            if isinstance(i, str):
                mc_args += i + " "
            elif isinstance(i, dict):
                if isinstance(i["value"], list):
                    for a in i["value"]:
                        mc_args += a + " "
                else:
                    mc_args += i["value"] + " "
    mc_args = mc_args.replace("${version_name}", version)
    mc_args = mc_args.replace(
        "${game_directory}", '"' + mcDir + "/versions/" + version + '"'
    )
    mc_args = mc_args.replace("${assets_root}", '"' + mcDir + "/assets" + '"')
    mc_args = mc_args.replace("${assets_index_name}", dic["assetIndex"]["id"])
    mc_args = mc_args.replace("${auth_player_name}", username)
    mc_args = mc_args.replace("${auth_uuid}", str(userUuid))
    mc_args = mc_args.replace("${user_properties}", "{}")
    if userType == "1":
        mc_args = mc_args.replace("${auth_access_token}", userInfo["access_token"])
        mc_args = mc_args.replace("${user_type}", "msa")
    else:
        mc_args = mc_args.replace("${auth_access_token}", "{}")
        mc_args = mc_args.replace("${user_type}", "Legacy")
    if "clientId" in mc_args:
        mc_args = mc_args.replace("${clientid}", "LoCyanClient")
        mc_args = mc_args.replace("${auth_xuid}", "{}")
        mc_args = mc_args.replace("${version_type}", dic["type"])
        mc_args = mc_args.replace("${resolution_height}", "960")
        mc_args = mc_args.replace("${resolution_width}", "1024")
        mc_args = mc_args.replace(
            "--quickPlayPath ${quickPlayPath} --quickPlaySingleplayer ${quickPlaySingleplayer} --quickPlayMultiplayer "
            "${quickPlayMultiplayer} --quickPlayRealms ${quickPlayRealms}",
            "",
        )
        # 去除 demo 版
        mc_args = mc_args.replace("--demo", "")
    commandLine = jvmArgs + " " + mc_args
    commandLine = commandLine.replace("/", "\\")
    with open("./run.bat", "w+") as f:
        f.write("@ECHO OFF\n")
        f.write(commandLine)
    os.system("run.bat")


if __name__ == "__main__":
    run(javaPath, mcDir, version, username)
