# LoCyanMinecraftLauncher
LoCyanTeam 为其配套联机大厅研发的 MC 启动器 | Powered by Python

## Warning
1. 本项目目前仍在开发中，产生任何 Bug 请及时反馈。

## Develop
1. 确保 Python 3.8+ 已安装
2. `git clone https://github.com/LoCyan-Team/LoCyanMinecraftLauncher.git`
3. `cd LoCyanMinecraftLauncher`
4. `pip install -r requerements.txt`

## Building
### Warning
目前 [Release](https://github.com/LoCyan-Team/LoCyanMinecraftLauncher/releases) 暂时还没有放包，目前只能以编译的方式使用 exe
### Pyinstaller(不推荐)
* `pip install pyinstaller`
* `pyinstaller -F main.py`
### nuitka
* `lndl_nuitka . -y`
