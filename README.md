# VoceChat_文生图机器人演示

## 开始之前

确保您的计算机上已经安装了 Python。如果没有，请访问 [Python 官网](https://www.python.org/) 下载并安装。
## 2. 安装 virtualenv（可选）

在 Python 3.3 及以后的版本中，您可以使用 venv 模块创建虚拟环境。如果您使用的是较早版本的 Python，您可以通过以下命令安装 virtualenv：

```bash
pip install virtualenv
```
###创建虚拟环境
打开命令行终端，并导航到您希望创建虚拟环境的目录。然后运行以下命令，其中 myenv 是您希望为虚拟环境命名的名称：

对于 Python 3.3 及更高版本（使用 venv）：

```bash
python -m venv myenv
```
对于使用 virtualenv：

```bash
virtualenv myenv
```
###激活虚拟环境
激活虚拟环境将更改您当前的命令行环境，以便在其中安装和运行项目特定的依赖项。在命令行中运行以下命令：

对于 Windows：

```bash
myenv\Scripts\activate
```
对于 macOS 和 Linux：

```bash
source myenv/bin/activate
```
### 安装依赖

在开始之前，请确保您已经安装了所有必要的库。您可以使用以下命令一键安装所有依赖：

```bash
pip install flask pymysql requests
```
###修改kexw_imgbot里面的默认参数

```bash
# 需要修改的配置
 # 机器人的 UID
BOT_UID = 4
 #ai图片网站 
kexw_url = "https://rightbrain.art"
 #ai图片网站cookies
cookies_list = [
    "satoken=xxxxx; token=xxxxx",
    "satoken=xxxxx; token=xxxxx " ]
 #VoceChat地址
kexw_boturl = "http://127.0.0.1:3009"
 #VoceChat Bot的key
kexw_key = " Bot的key"
 #VoceChat 管理员的Token 
kexw_sudokey = "管理员的Token"
#mysql
kexw_host = "127.0.0.1"
kexw_user = "账号"
kexw_password = "数据库账号密码"
kexw_port = 3306  #数据库端口默认3306
kexw_database = "数据库账号"
# 需要修改的配置
```
### 运行脚本
```bash
python kexw_imgbot.py
```
如果您希望在终端会话中继续与脚本交互，您可以在启动 nohup 命令时添加 & 符号来使脚本在后台运行，然后使用 disown 命令来将进程与终端分离，从而不会被终端关闭影响：
```bash
nohup python kexw_imgbot.py &
```
这样，脚本将继续在后台运行，即使您关闭了终端。
请记住，后台运行的进程将继续在后台执行，直到您手动终止它，或者重启计算机。要停止进程，您可以使用 kill 命令，将之前输出的 PID 替换为相应的进程 ID。

以上地址都是本地运行的地址，在voce的BOT设置页面填入对应的地址，
```bash
http://127.0.0.1:5321/webhook
```
应该能够进行通信了，如果网站和webhook的服务器不是同一台，手机反代即可

## 功能
### 修改默认参数请发送 
1. 修改模型方向
2. 修改采集器选项
3. 修改图片比例

### 生成图片格式 
#### `图片的关键词`|`负面关键词`|`输入文本强度。默认可以7上限15`|`输入步数默认可以20（生成图片的步数） `|`输入照片模式0.普通，1.高清`|`输入生成的张数，默认。如果照片模式是高清，这里只能输入2,如果是普通无上限`

### 花里长着小猫的花朵，动物|正常的花朵|7|20|高清|2
