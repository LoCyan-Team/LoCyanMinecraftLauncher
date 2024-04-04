import os
import json
import zipfile

version = "1.20.2"
mcDir = "E:/MC/.minecraft"
maxMem = "2048m"
javaPath = "C:/Program Files/Java/jre-1.8/bin/javaw.exe"
username = "Daiyangcheng"

def unpress(fileName, unPressPath):
    zip = zipfile.ZipFile(fileName)
    for z in zip.namelist():
        if os.path.exists(unPressPath) == False:
            os.mkdir(unPressPath)
        zip.extract(z, unPressPath)
    zip.close()
        

def findVersion(mcDir: str, version: str) -> bool:
    return os.path.exists(f"{mcDir}/versions/{version}/{version}.json")

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
        if "classifiers" in i["downloads"]:
            for native in i["downloads"]:
                if native == "artifact":
                    # 非本地库 （forge，optifine）
                    directPath = nativePath
                    path = i["downloads"][native]["path"]
                    filePath = f"{mcDir}/libraries/{path}"
                    unpress(filePath, directPath)
                elif native == "classifiers":
                    # 本地库
                    for m in i["downloads"][native].keys():
                        if m == "natives-windows":
                            path = i["downloads"][native][m]["path"]
                            filePath = f"{mcDir}/libraries/{path}"
                            unpress(filePath, filePath.replace(".jar", ""))
    jvmArgs = f"\"{javaPath}\" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True -Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true -XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump -Djava.library.path={nativePath} -Djna.tmpdir={nativePath} -Dorg.lwjgl.system.SharedLibraryExtractPath={nativePath} -Dio.netty.native.workdir={nativePath} -Dminecraft.launcher.brand=LoCyanLauncher -Dminecraft.launcher.version=1.0.0 -cp"
    classPath = ""
    classPath += "\""
    for i in dic["libraries"]:
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
    if dic.get("minecraftArguments") == "":
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
    mc_args = mc_args.replace("${auth_uuid}", "{}")
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

        
    commandLine = jvmArgs + " " + mc_args
    commandLine = commandLine.replace("/", "\\")
    with open("./run.bat", "w+") as f:
        f.write(commandLine)
    os.system("./run.bat")


if __name__ == "__main__":
    run(javaPath, mcDir, version, username)