# 快速开始

## 前置条件

至本文档修订之时止，版本 0.11.0 及以上的服务端需 Python 3.15 及以上版本、OpenSSL 3.5 及以上版本方可正常运行。

请提前配置好 Python 环境和用于管理依赖的包管理器。作为参考，我们推荐使用 `uv` 来管理依赖和虚拟环境，它是一款用 Rust 编写的 Python 包管理器和环境管理器，具有相比 `pip` 等工具而言极高的性能，且能带来其他多种好处。

!!! warning
    较老旧的 Linux 分发版可能仍携带低版本的 OpenSSL，经系统包管理器安装的 Python 或许会基于它们构建。由 `uv` 安装和管理的 Python 分发版则通常会自行携带 OpenSSL 库，可以解决此问题。

尽管使用 Python 的自由线程（freethreaded）版本或可使本服务端取得更好的表现，但受制于部分依赖的支持问题，服务端**尚无法在自由线程分发版下正常运作**。

若要通过代码仓库直接部署服务端，并希望在之后继续从代码仓库拉取更新，您还需要在环境中准备好 [Git](https://git-scm.com)。以下的内容均假定您已满足本节前述的所有要求。在之后的教程中，我们将一直使用 `uv` 来管理依赖，不过使用 `pip` 等其他工具理论上也是可行的。

## 拉取代码仓库

如果您计划直接拉取代码仓库来将服务端文件下载到本地，可运行如下的命令：

```bash
git clone https://github.com/cfms-dev/cfms_on_websocket.git --depth=1 --recurse-submodules --shallow-submodules
```

这将把代码仓库克隆到您工作目录下的 `cfms_on_websocket` 文件夹，并仅拉取默认分支最近的一次提交及其子模块。在该文件夹下，`src/` 是存放服务端代码的实际目录；启动 `main.py` 时必须将它设为工作目录。`maintain` 则可从项目根、`src/` 或其子目录调用，并会自动定位最近的运行根。

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
uv sync
```

这将安装服务端以最小状态运行时所需的依赖。然而，一些可选功能需要额外的依赖才能正常工作，可以利用形如下方的命令安装依赖：

```bash
uv sync --extra cluster --extra mysql
# PostgreSQL 部署改用：
uv sync --extra cluster --extra postgresql

# 按需添加扩展运行时：
uv sync --extra ext-oidc-sso --extra ext-http-api --extra ext-scheduling-cluster
```

其中，`cluster` 为 Redis 和 S3 Provider 安装依赖，`mysql` 与 `postgresql` 分别安装数据库驱动，`ext-oidc-sso` 安装 OpenID Connect 单点登录运行时，`ext-http-api` 安装可选 HTTPS/FastAPI 框架，`ext-scheduling-cluster` 安装 Redis 集群调度所需的 Dramatiq。

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

在 `server` 一节下，`host` 指定服务端监听地址，`port` 指定端口。服务端支持 SQLite、MySQL 和 PostgreSQL；单机快速开始无需调整即可使用 SQLite。共享数据库部署应通过 `database.type` 选择引擎并填写连接信息，同时安装相应驱动。如有疑问，随配置范本附上的注释和[配置文件](configuration.md)一节可提供更多信息。

`server.secret_key` 和 `security.pepper` 在此时应保持为空。当 `src/init` 尚不存在时，服务端会在首次初始化时为两者生成随机值并写回配置文件；即使事先填写了值，首次初始化流程也会覆盖它们。在生成后，请记得将它们作为机密信息妥善保管。

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
[2026-09-09 19:22:02,106 INFO    ] CFMS Core Version: 0.8.0
[2026-08-11 19:22:02,212 INFO    ] Loaded 0 banned subnet(s) from database.
[2026-08-11 19:22:02,220 INFO    ] CFMS WebSocket server started at wss://[::1]:5104
```

首次启动期间，服务端还会创建数据库、内置用户组、示例文档以及初始管理员账户，并在 `src/admin_password.txt` 中写入管理员密码。使用该密码完成首次登录后，应尽快修改密码并安全删除这个明文文件。若配置的 TLS 私钥和证书均不存在，服务端还会生成一套自签名证书；正式部署时应替换为受客户端信任、且与实际服务地址相匹配的证书。

服务端将在 `src/init` 中记录已经完成初始化。不要在数据库和其他运行数据仍需保留时单独删除该文件，否则服务端会将当前目录视为尚未初始化。

对于 Linux 而言，为了使服务端进程长期驻留在内存中，相较于使用 `screen` 命令，我们更推荐为服务端创建一个服务，以实现意外退出时的自动重启等功能。
