.. _installation:

安装与配置
============

系统要求
--------

CFMS 服务端需要以下环境：

- **Python 3.11 或更高版本**（必需，使用了 Python 3.11+ 的新语法特性）
- **操作系统**：Linux、macOS 或 Windows
- **数据库**：SQLite（默认）或 MySQL
- **网络**：支持 WebSocket 的网络环境

快速开始
--------

1. 克隆代码仓库
^^^^^^^^^^^^^^^

从 GitHub 克隆 CFMS 服务端仓库：

.. code-block:: console

   $ git clone https://github.com/creeper19472/cfms_on_websocket.git
   $ cd cfms_on_websocket

2. 安装依赖
^^^^^^^^^^^

使用 pip 安装所需的 Python 包：

.. code-block:: console

   $ pip install -r requirements.txt

主要依赖包括：

- ``websockets`` - WebSocket 服务器实现
- ``sqlalchemy`` - 数据库 ORM
- ``PyJWT`` - JWT 令牌生成和验证
- ``cryptography`` - 加密和 SSL 证书生成
- ``jsonschema`` - JSON 数据验证
- ``tomli`` (Python < 3.11) 或内置 ``tomllib`` - TOML 配置文件解析

3. 配置服务器
^^^^^^^^^^^^^

在首次启动前，需要创建配置文件 ``config.toml``。可以从示例配置开始：

.. code-block:: console

   $ cp config.sample.toml config.toml
   $ nano config.toml  # 或使用您喜欢的编辑器

关键配置项：

.. code-block:: toml

   [server]
   name = "CFMS WebSocket Server"
   host = "127.0.0.1"  # 监听地址
   port = 5104         # 监听端口
   secret_key = ""     # JWT 密钥（首次启动时自动生成）

   [database]
   type = "sqlite"     # 或 "mysql"
   file = "app.db"     # SQLite 数据库文件名

详细的配置说明请参见 :doc:`config` 章节。

4. 初始化数据库
^^^^^^^^^^^^^^^

首次运行时，服务器会自动初始化数据库并创建必要的表结构：

.. code-block:: console

   $ python main.py

初始化过程会：

- 创建所有数据库表
- 生成自签名 SSL 证书（用于 WSS 连接）
- 创建默认用户组（``user`` 和 ``sysop``）
- 创建管理员账户（用户名：``admin``）
- 生成随机密码并保存到 ``admin_password.txt``

.. warning::

   请妥善保管 ``admin_password.txt`` 中的管理员密码，并在首次登录后立即修改！

5. 启动服务器
^^^^^^^^^^^^^

配置完成后，启动 CFMS 服务器：

.. code-block:: console

   $ python main.py

服务器启动后，您应该看到类似以下的输出：

.. code-block:: text

   [INFO] Server starting on 127.0.0.1:5104
   [INFO] SSL certificate loaded
   [INFO] Database initialized
   [INFO] Server ready to accept connections

6. 验证安装
^^^^^^^^^^^

可以使用简单的 Python 脚本测试连接：

.. code-block:: python

   import asyncio
   import websockets
   import ssl
   import json

   async def test_connection():
       ssl_context = ssl.create_default_context()
       ssl_context.check_hostname = False
       ssl_context.verify_mode = ssl.CERT_NONE
       
       async with websockets.connect('wss://localhost:5104', ssl=ssl_context) as ws:
           # 请求服务器信息
           await ws.send(json.dumps({
               "action": "server_info",
               "data": {},
               "username": "",
               "token": ""
           }))
           response = await ws.recv()
           print(json.loads(response))

   asyncio.run(test_connection())

目录结构
--------

安装后的目录结构如下：

.. code-block:: text

   cfms_on_websocket/
   ├── main.py                    # 服务器主入口
   ├── config.toml                # 配置文件（需创建）
   ├── config.sample.toml         # 配置文件示例
   ├── requirements.txt           # Python 依赖
   ├── test.py                    # 测试脚本
   ├── include/                   # 核心代码
   │   ├── classes/               # 类定义
   │   ├── database/              # 数据库模型
   │   ├── handlers/              # 请求处理器
   │   ├── system/                # 系统工具
   │   └── util/                  # 工具函数
   ├── content/                   # 运行时数据
   │   ├── logs/                  # 日志文件
   │   └── ssl/                   # SSL 证书
   └── certtools/                 # 证书工具

数据库初始化详情
----------------

服务器初始化时会创建以下数据结构：

默认用户组
^^^^^^^^^^

1. **user** 组：基础用户组，拥有基本权限
   
   - ``set_passwd`` - 修改自己的密码

2. **sysop** 组：系统管理员组，拥有完整权限
   
   - 所有文档和目录操作权限
   - 用户和组管理权限
   - 系统管理权限
   - 访问控制管理权限
   - 审计日志查看权限

默认管理员账户
^^^^^^^^^^^^^^

- **用户名**：``admin``
- **昵称**：管理员
- **密码**：随机生成（保存在 ``admin_password.txt``）
- **所属组**：``sysop`` 和 ``user``

安全最佳实践
------------

1. **更改管理员密码**

   首次登录后立即修改管理员密码：

   .. code-block:: json

      {
        "action": "set_passwd",
        "data": {
          "username": "admin",
          "old_password": "<从文件读取的密码>",
          "new_password": "<您的新密码>"
        },
        "username": "admin",
        "token": "<您的令牌>"
      }

2. **配置防火墙**

   限制对服务器端口的访问，仅允许受信任的 IP 地址连接。

3. **使用有效的 SSL 证书**

   在生产环境中，应替换自签名证书为受信任的 CA 颁发的证书：

   .. code-block:: toml

      [server]
      ssl_keyfile = "/path/to/your/key.pem"
      ssl_certfile = "/path/to/your/cert.pem"

4. **设置强密码策略**

   在配置文件中启用密码要求：

   .. code-block:: toml

      [security]
      passwd_min_length = 12
      passwd_must_contain = ["uppercase", "lowercase", "digit", "special"]

5. **定期备份数据库**

   定期备份 ``app.db`` 文件（SQLite）或 MySQL 数据库。

故障排除
--------

端口已被占用
^^^^^^^^^^^^

如果看到 "Address already in use" 错误，检查端口是否被占用：

.. code-block:: console

   $ lsof -i :5104  # Linux/macOS
   $ netstat -ano | findstr :5104  # Windows

可以在 ``config.toml`` 中修改端口号。

SSL 证书错误
^^^^^^^^^^^^

如果遇到 SSL 相关错误，确保：

- ``content/ssl/`` 目录存在且有写入权限
- 首次启动时自动生成的证书文件完整

数据库连接失败
^^^^^^^^^^^^^^

对于 MySQL：

- 确认 MySQL 服务正在运行
- 检查配置文件中的数据库连接信息
- 确保数据库用户有足够的权限

权限被拒绝
^^^^^^^^^^

确保运行服务器的用户有权限：

- 读写数据库文件
- 创建和写入日志目录
- 读取 SSL 证书文件

下一步
------

成功安装并启动服务器后，您可以：

- 阅读 :doc:`api` 了解如何与服务器通信
- 查看 :doc:`api_refs` 了解所有可用的 API 接口
- 学习 :doc:`groups_and_rights` 了解权限系统
- 探索 :doc:`access_control` 了解访问控制机制
