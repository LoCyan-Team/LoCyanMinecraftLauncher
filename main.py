import os
import json
import zipfile
import uuid
from download import *

# 自动识别 Optifine, Forge, Fabric 进行启动
version = "1.20.4"
mcDir = "E:/MC/.minecraft"
maxMem = "2048m"
javaPath = "C:/Program Files/Java/jdk-21/bin/java.exe"
username = "Daiyangcheng"
notFoundFiles = {}
downloadFlag = False

def unpress(fileName, unPressPath,downloadUrl):
    global downloadFlag
    zip = None
    try:
        zip = zipfile.ZipFile(fileName)
    except FileNotFoundError:
        downloadFlag = True
        notFoundFiles[fileName] = downloadUrl
    if downloadFlag == False:
        for z in zip.namelist():
            if os.path.exists(unPressPath) == False:
                os.mkdir(unPressPath)
            zip.extract(z, unPressPath)
        zip.close()
        

def findVersion(mcDir: str, version: str) -> bool:
    return os.path.exists(f"{mcDir}/versions/{version}/{version}.json")

def getPath(s: str) -> str:
    # org.ow2.asm:asm-analysis:9.6
    s = s.split(":")
    version = s[-1]
    fileName = s[1]
    path = s[0].replace(".", "/") + "/" + fileName + "/" + version + "/" + fileName + "-" + version + ".jar"
    return path

def run(javaPath: str, mcDir: str, version: str, username: str) -> None:
    if findVersion(mcDir, version) != True:
        exit()
    
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
                    unpress(filePath, directPath, i["downloads"][native]["url"])
                elif native == "classifiers":
                    # 本地库
                    for m in i["downloads"][native].keys():
                        if m == "natives-windows":
                            path = i["downloads"][native][m]["path"]
                            filePath = f"{mcDir}/libraries/{path}"
                            unpress(filePath, filePath.replace(".jar", ""), i["downloads"][native][m]["url"])
    
    if downloadFlag:
        for i in notFoundFiles.keys():
            download_file(notFoundFiles[i], i)
        print("游戏资源下载完成，请尝试重启本软件")
        exit()
    
    jvmArgs = f"\"{javaPath}\" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump -Djava.library.path={nativePath} -Djna.tmpdir={nativePath} -Dorg.lwjgl.system.SharedLibraryExtractPath={nativePath} -Dio.netty.native.workdir={nativePath} -Dminecraft.launcher.brand=LoCyanLauncher -Dminecraft.launcher.version=1.0.0 -cp"
    classPath = ""
    classPath += "\""
    for i in dic["libraries"]:
        if i.get("downloads") == None or i.get("downloads") == {}:
            path = mcDir + "/libraries/" + getPath(i["name"])
            print(path)
            classPath += path + ";"
            continue
        if not "classifiers" in i["downloads"]:
            path = i["downloads"]["artifact"]["path"]
            normal = f"{mcDir}/libraries/{path}"
            classPath += normal + ";"
    classPath += f"{mcDir}/versions/{version}/{version}.jar\""
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
    mc_args = mc_args.replace("${auth_player_name}", username)
    mc_args = mc_args.replace("${version_name}", version)
    mc_args = mc_args.replace("${game_directory}", "\"" + mcDir + "/versions/" + version + "\"")
    mc_args = mc_args.replace("${assets_root}", "\"" + mcDir + "/assets" + "\"")
    mc_args = mc_args.replace("${assets_index_name}", dic["assetIndex"]["id"])
    mc_args = mc_args.replace("${auth_uuid}", str(uuid.uuid4()).replace("-",""))
    mc_args = mc_args.replace("${auth_access_token}", "{}")
    mc_args = mc_args.replace("${user_properties}", "{}")
    mc_args = mc_args.replace("${user_type}", "Legacy")
    if "clientId" in mc_args:
        mc_args = mc_args.replace("${clientid}", "LoCyanClient")
        mc_args = mc_args.replace("${auth_xuid}", "{}")
        mc_args = mc_args.replace("${version_type}", dic["type"])
        mc_args = mc_args.replace("${resolution_height}", "960")
        mc_args = mc_args.replace("${resolution_width}", "1024")
        mc_args = mc_args.replace("--quickPlayPath ${quickPlayPath} --quickPlaySingleplayer ${quickPlaySingleplayer} --quickPlayMultiplayer ${quickPlayMultiplayer} --quickPlayRealms ${quickPlayRealms}", "")
        # 去除 demo 版
        mc_args = mc_args.replace("--demo", "")
    commandLine = jvmArgs + " " + mc_args
    commandLine = commandLine.replace("/", "\\")
    with open("./run.bat", "w+") as f:
        f.write(commandLine)
        f.write("\npause")
    os.system("run.bat")


if __name__ == "__main__":
    run(javaPath, mcDir, version, username)