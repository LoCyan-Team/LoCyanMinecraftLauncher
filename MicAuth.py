from requests import get
from requests import post
from json import dumps, loads
import webbrowser


def get_code():
    webbrowser.open(
        "https://login.live.com/oauth20_authorize.srf?client_id=00000000402b5328&response_type=code&scope=service%3A"
        "%3Auser.auth.xboxlive.com%3A%3AMBI_SSL&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
    )
    print(
        """请访问打开的页面获取登录令牌, 并在该页面内复制重定向后的URL,格式类似于 https://login.live.com/oauth20_desktop.srf?code=codegoeshere&lc=1033
"""
    )

    code_url = input("输入URL: ")
    begin = code_url.find("code") + 5
    end = code_url.find("&lc")
    code = code_url[begin:end]
    data = {
        "client_id": "00000000402b5328",
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "service::user.auth.xboxlive.com::MBI_SSL",
    }
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    # 得到 accessToken 进行 XBL 验证
    rs = post(
        "https://login.live.com/oauth20_token.srf", data=data, headers=header
    ).json()
    access_token = rs["access_token"]
    refresh_token = rs["refresh_token"]
    with open("./token.session", "w+") as f:
        f.write(refresh_token)

    data = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"{access_token}",
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }

    header = {"Content-Type": "application/json", "Accept": "application/json"}

    # XBL 身份验证
    rs = post(
        "https://user.auth.xboxlive.com/user/authenticate",
        data=dumps(data),
        headers=header,
    ).json()
    token = rs["Token"]
    for i in rs["DisplayClaims"]["xui"]:
        uhs = i["uhs"]

    data = {
        "Properties": {"SandboxId": "RETAIL", "UserTokens": [token]},
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
    }
    # 用 XBL 身份验证得到的 Token 获取 XSTS 令牌
    rs = post(
        "https://xsts.auth.xboxlive.com/xsts/authorize",
        data=dumps(data),
        headers=header,
    ).json()
    xsts = rs["Token"]

    data = {"identityToken": "XBL3.0 x=" + uhs + ";" + xsts}

    # 得到 Minecraft 档案
    rs = post(
        "https://api.minecraftservices.com/authentication/login_with_xbox",
        data=dumps(data),
    ).json()
    mc_access_token = rs["access_token"]

    # 检测该用户是否拥有 Java 版游戏
    header = {"Authorization": f"Bearer {mc_access_token}"}
    rs = get("https://api.minecraftservices.com/entitlements/mcstore", headers=header)
    if rs.text == "":
        print("你还没购买 Minecraft!")
        exit()

    rs = get(
        "https://api.minecraftservices.com/minecraft/profile", headers=header
    ).json()
    uuid = rs["id"]
    name = rs["name"]
    rs_val = {"uuid": uuid, "username": name, "access_token": mc_access_token}
    return rs_val
