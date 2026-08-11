# 快速开始

## 前置条件

至本文档修订之时止，服务端需 Python 3.14 及以上版本方可正常运行。请提前配置好 Python 环境和用于管理依赖的包管理器。作为参考，我们推荐使用 `uv` 来管理依赖和虚拟环境，它是一款用 Rust 编写的 Python 包管理器和环境管理器，具有相比 `pip` 等工具而言极高的性能，且能带来其他多种好处。

由于服务端采用 `threading` 方案实现，使用 Python 的自由线程（freethreaded）版本或可使本服务端在多核利用上取得更好的表现。不过，我们尚未就此开展全面的测试，因此不能断定这么做是否能在性能上带来实际提升。

若要通过代码仓库直接部署服务端，并希望在之后继续从代码仓库拉取更新，您还需要在环境中准备好 [Git](https://git-scm.com)。以下的内容均假定您已满足本节前述的所有要求。在之后的教程中，我们将一直使用 `uv` 来管理依赖，不过使用 `pip` 等其他工具理论上也是可行的。

!!! warning
    截至 Python 3.14.5 发布之时，Python 的官方分发版所捆绑的 OpenSSL 版本均较低（版本 3.5 以下），因此缺少对[后量子加密算法](https://csrc.nist.gov/projects/post-quantum-cryptography)（Post-Quantum Cryptography, PQC）的支持，而这可能导致服务器与客户端的通信受“先窃取，后解密”的威胁。现在，当运行在任何捆绑了过低版本的 OpenSSL 的 Python 分发版上时，服务端每次启动时都将在日志中输出一条警告信息，以提醒系统管理员使用更高的 OpenSSL 版本。

    Python 的一些第三方分发版已捆绑了更高版本的 OpenSSL ，使用 `uv` 即可方便地安装它们。

## 拉取代码仓库

如果您计划直接拉取代码仓库来将服务端文件下载到本地，可运行如下的命令：

```bash
git clone https://github.com/cfms-dev/cfms_on_websocket.git --depth=1 --recurse-submodules --shallow-submodules
```

这将把代码仓库克隆到您工作目录下的 `cfms_on_websocket` 文件夹，并仅拉取默认分支最近的一次提交及其子模块。在该文件夹下，`src/` 是存放服务端代码的实际目录，今后运行服务端和维护命令时也应当将它设置为工作目录。

!!! warning
    请确保您在启动服务端前设置了正确的工作目录，因为服务端的文件读写是基于相对路径而非绝对路径进行的。错误的工作目录将导致不可预知的后果。

若克隆时未使用 `--recurse-submodules`，可运行下面的命令补充初始化子模块。它们包括一套简单的证书工具和预置的证书库，后者允许服务端识别持有由开发者签发的证书的客户端：

```bash
cd cfms_on_websocket
git submodule init
git submodule update --depth=1
```

## 安装依赖

进入代码仓库根目录，运行以下命令来安装必要的依赖：

```bash
cd cfms_on_websocket
uv sync --upgrade
```

这将安装服务端以最小状态运行时所需要的最低限度的依赖。然而，一些可选功能需要额外的依赖才能正常工作，可以运行下面的命令来为 S3 对象存储、Redis 和 MySQL 支持等可选功能安装依赖：

```bash
uv sync --extra cluster --extra mysql --extra ext_oidc_sso
```

其中，`cluster` 为 Redis 和 S3 提供者安装依赖，`mysql` 安装 MySQL 驱动，而 `ext_oidc_sso` 安装 OpenID Connect 单点登录扩展所需的依赖。仅需启用其中部分功能时，可以省略无关的 `--extra` 参数。

## 调整配置文件

代码仓库中不含可由服务端直接读取的配置文件，而仅含有一份范本（`config.toml.sample`）。由于服务端不会在缺失配置文件时自动生成它，因此在初次启动服务端前我们需要手动完成配置。

为了创建配置文件，我们需要在 `src` 目录下将 `config.toml.sample` 复制一份，并命名为 `config.toml`：

=== "Linux"

    ```bash
    cd src
    cp config.toml.sample config.toml
    ```

=== "Windows"

    ```ps1
    Set-Location src
    Copy-Item config.toml.sample config.toml
    ```

之后，我们需要编辑 `config.toml`。此配置文件中有相当数目的可配置项，不过为了快速开始，我们暂时只需关注其中的小部分设置。

在 `server` 一节下，`host` 指定了服务端监听的地址，`port` 指定了监听的端口。服务端支持 SQLite 和 MySQL 两种类型的数据库引擎，如果您没有一个 MySQL 服务器，无需调整任何配置，服务端便可默认基于 SQLite 数据库运行。若希望以 MySQL 作为数据库引擎，可以通过 `database` 节下的 `type` 指定要使用的数据库引擎，并在该节的其他配置项中填写目标服务器地址和登录凭据。如有疑问，随配置文件附上的注释和[配置文件](configuration.md)一节可提供更多信息。

`server.secret_key` 和 `security.pepper` 在此时可以暂时保持为空。服务端将在首次初始化时分别生成随机值并写回配置文件；生成后务必将它们作为机密信息妥善保管。

## 启动服务端

保持 `src` 为工作目录并运行：

```bash
uv run python main.py
```

请勿通过 `python -O` 或设置 `PYTHONOPTIMIZE` 来启动服务端。

也可以先激活虚拟环境（以下的示例假定当前位于代码仓库根目录）：

=== "Linux"

    ```bash
    source .venv/bin/activate
    cd src
    python main.py
    ```

=== "Windows"

    ```ps1
    .\.venv\Scripts\Activate.ps1
    Set-Location src
    python main.py
    ```

若服务端正常启动，您将看到与以下内容类似的输出：

```log
[2026-08-11 19:22:01,359 INFO    ] Database not initialized, initializing now...
[2026-08-11 19:22:02,105 INFO    ] Initializating CFMS WebSocket server...
[2026-08-11 19:22:02,106 INFO    ] CFMS Core Version: 0.4.1.260811_alpha
[2026-08-11 19:22:02,212 INFO    ] Loaded 0 banned subnet(s) from database.
[2026-08-11 19:22:02,220 INFO    ] CFMS WebSocket server started at wss://[::1]:5104
```

首次启动期间，服务端还会创建数据库、内置用户组、示例文档以及初始管理员账户，并在 `src/admin_password.txt` 中写入管理员密码。使用该密码完成首次登录后，应尽快修改密码并安全删除这个明文文件。若配置的 TLS 私钥和证书均不存在，服务端还会生成一套自签名证书；正式部署时应替换为受客户端信任、且与实际服务地址相匹配的证书。

服务端将在 `src/init` 中记录已经完成初始化。不要在数据库和其他运行数据仍需保留时单独删除该文件，否则服务端会将当前目录视为尚未初始化。

对于 Linux 而言，为了使服务端进程长期驻留在内存中，相较于使用 `screen` 命令，我们更推荐为服务端创建一个服务，以实现意外退出时的自动重启等功能。
