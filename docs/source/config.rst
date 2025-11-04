.. _config:

配置文件
============================

CFMS 服务端使用 TOML 格式的配置文件 ``config.toml`` 来管理服务器的运行参数。
配置文件应位于服务器的工作根目录下。

.. note:: 
   配置文件在服务器启动时加载一次，修改后需要重启服务器才能生效。
   这些设置仅控制基本的启动参数。有关运行时行为的高级控制，请参考权限和访问控制系统。

配置文件格式
------------------------------

CFMS 使用 Python 3.11+ 内置的 ``tomllib`` 库（或 Python 3.11 以下使用 ``tomli``）
读取 TOML v1.0 格式的配置文件。

TOML 支持以下数据类型：

1. 字符串（String）
2. 整数（Integer）
3. 浮点数（Float）  
4. 布尔值（Boolean）
5. 日期时间（Datetime）
6. 数组（Array）
7. 表（Table）
8. 内联表（Inline Table）

更多信息请访问 TOML 官方网站：https://toml.io/

完整配置示例
------------------------------

以下是一个完整的配置文件示例：

.. code-block:: toml

   debug = false

   [server]
   name = "CFMS WebSocket Server"
   host = "127.0.0.1"
   port = 5104
   dualstack_ipv6 = true
   secret_key = ""
   ssl_keyfile = "./content/ssl/key.pem"
   ssl_certfile = "./content/ssl/cert.pem"
   file_chunk_size = 2097152  # 2MB

   [document]
   allow_name_duplicate = false

   [security]
   passwd_min_length = 8
   passwd_max_length = 32
   enable_passwd_force_expiration = true
   require_passwd_enforcement_changes = true
   passwd_expire_after_days = 365
   passwd_must_contain = []

   [database]
   type = "sqlite"
   file = "app.db"
   # MySQL 配置（如果使用 MySQL）
   host = "localhost"
   port = 3306
   username = ""
   password = ""
   db_name = "app_db"
   charset = "utf8mb4"

配置项详解
------------------------------

全局配置
^^^^^^^^^^^^^^^^^^^^^^

``debug``
   **类型**：布尔值（Boolean）
   
   **默认值**：``false``
   
   **说明**：是否启用调试模式。启用后会输出更详细的日志信息，但可能影响性能。
   生产环境中应设置为 ``false``。

服务器配置 [server]
^^^^^^^^^^^^^^^^^^^^^^

``name``
   **类型**：字符串（String）
   
   **默认值**：``"CFMS WebSocket Server"``
   
   **说明**：服务器名称，用于标识和日志记录。

``host``
   **类型**：字符串（String）
   
   **默认值**：``"127.0.0.1"``
   
   **说明**：服务器监听的 IP 地址。
   
   - ``"127.0.0.1"`` - 仅监听本地回环接口
   - ``"0.0.0.0"`` - 监听所有 IPv4 接口
   - ``"::"`` - 监听所有 IPv6 接口（需要 dualstack_ipv6）
   
   **安全提示**：仅在必要时监听外部接口，并配置防火墙规则。

``port``
   **类型**：整数（Integer）
   
   **默认值**：``5104``
   
   **说明**：WebSocket 服务器监听的端口号。确保该端口未被其他程序占用。

``dualstack_ipv6``
   **类型**：布尔值（Boolean）
   
   **默认值**：``true``
   
   **说明**：是否启用 IPv4/IPv6 双栈支持。启用后服务器可以同时处理 IPv4 和 IPv6 连接。

``secret_key``
   **类型**：字符串（String）
   
   **默认值**：``""``（空字符串，首次启动时自动生成）
   
   **说明**：用于签名 JWT 令牌的密钥。服务器会在首次启动时自动生成一个随机密钥。
   
   **安全提示**：
   
   - 保持该密钥的机密性
   - 不要在版本控制系统中提交包含实际密钥的配置文件
   - 更改密钥会使所有现有的用户令牌失效

``ssl_keyfile``
   **类型**：字符串（String）
   
   **默认值**：``"./content/ssl/key.pem"``
   
   **说明**：SSL/TLS 私钥文件的路径。用于建立安全的 WSS 连接。

``ssl_certfile``
   **类型**：字符串（String）
   
   **默认值**：``"./content/ssl/cert.pem"``
   
   **说明**：SSL/TLS 证书文件的路径。服务器启动时会检查证书是否存在，
   如果不存在则自动生成自签名证书。
   
   **生产环境建议**：使用受信任的证书颁发机构（CA）签发的证书。

``file_chunk_size``
   **类型**：整数（Integer）
   
   **默认值**：``2097152``（2MB）
   
   **说明**：文件传输时的分块大小（字节）。较大的分块可以提高传输效率，
   但可能因客户端配置导致传输失败。
   
   **推荐值**：1MB - 4MB 之间

文档配置 [document]
^^^^^^^^^^^^^^^^^^^^^^

``allow_name_duplicate``
   **类型**：布尔值（Boolean）
   
   **默认值**：``false``
   
   **说明**：是否允许同一目录下存在重名的文档。
   
   - ``false`` - 禁止重名（推荐）
   - ``true`` - 允许重名
   
   .. note::
      如果先启用后禁用，已存在的重名文档会被保留，但新上传的重名文档会被拒绝。

安全配置 [security]
^^^^^^^^^^^^^^^^^^^^^^

``passwd_min_length``
   **类型**：整数（Integer）
   
   **默认值**：``8``
   
   **说明**：密码的最小长度要求。

``passwd_max_length``
   **类型**：整数（Integer）
   
   **默认值**：``32``
   
   **说明**：密码的最大长度限制。

``enable_passwd_force_expiration``
   **类型**：布尔值（Boolean）
   
   **默认值**：``true``
   
   **说明**：是否启用密码强制过期策略。启用后，用户密码在指定天数后会过期，
   需要强制更改。

``require_passwd_enforcement_changes``
   **类型**：布尔值（Boolean）
   
   **默认值**：``true``
   
   **说明**：是否强制要求不符合密码规则的用户在登录时修改密码。
   
   .. note::
      即使密码是在规则实施前创建的，也会要求修改。

``passwd_expire_after_days``
   **类型**：整数（Integer）
   
   **默认值**：``365``
   
   **说明**：密码过期天数。仅在 ``enable_passwd_force_expiration`` 为 ``true`` 时生效。

``passwd_must_contain``
   **类型**：数组（Array）
   
   **默认值**：``[]``（空数组，无特殊要求）
   
   **说明**：密码必须包含的字符类型。可选值：
   
   - ``"uppercase"`` - 大写字母
   - ``"lowercase"`` - 小写字母
   - ``"digit"`` - 数字
   - ``"special"`` - 特殊字符
   
   **示例**：
   
   .. code-block:: toml
   
      passwd_must_contain = ["uppercase", "lowercase", "digit"]

数据库配置 [database]
^^^^^^^^^^^^^^^^^^^^^^

``type``
   **类型**：字符串（String）
   
   **默认值**：``"sqlite"``
   
   **说明**：数据库类型。支持的值：
   
   - ``"sqlite"`` - SQLite 数据库（推荐用于开发和小规模部署）
   - ``"mysql"`` - MySQL 数据库（推荐用于生产环境）

SQLite 特定配置
""""""""""""""""

``file``
   **类型**：字符串（String）
   
   **默认值**：``"app.db"``
   
   **说明**：SQLite 数据库文件名（相对于工作目录）。

MySQL 特定配置
""""""""""""""""

``host``
   **类型**：字符串（String）
   
   **默认值**：``"localhost"``
   
   **说明**：MySQL 服务器地址。

``port``
   **类型**：整数（Integer）
   
   **默认值**：``3306``
   
   **说明**：MySQL 服务器端口。

``username``
   **类型**：字符串（String）
   
   **说明**：MySQL 数据库用户名。

``password``
   **类型**：字符串（String）
   
   **说明**：MySQL 数据库密码。
   
   **安全提示**：考虑使用环境变量或密钥管理工具存储密码。

``db_name``
   **类型**：字符串（String）
   
   **默认值**：``"app_db"``
   
   **说明**：要使用的 MySQL 数据库名称。

``charset``
   **类型**：字符串（String）
   
   **默认值**：``"utf8mb4"``
   
   **说明**：MySQL 连接字符集。推荐使用 ``utf8mb4`` 以支持完整的 Unicode 字符集。

``options``
   **类型**：字符串（String）
   
   **说明**：MySQL 连接的额外选项。
   
   .. note::
      此功能尚未完全实现。

配置最佳实践
------------------------------

开发环境
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: toml

   debug = true

   [server]
   host = "127.0.0.1"
   port = 5104

   [database]
   type = "sqlite"
   file = "dev.db"

   [security]
   passwd_min_length = 6  # 开发时可以放宽
   enable_passwd_force_expiration = false

生产环境
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: toml

   debug = false

   [server]
   host = "0.0.0.0"  # 根据实际需求
   port = 5104
   secret_key = "use-a-strong-random-key-here"
   ssl_keyfile = "/etc/cfms/ssl/key.pem"
   ssl_certfile = "/etc/cfms/ssl/cert.pem"

   [database]
   type = "mysql"
   host = "db.example.com"
   username = "cfms_user"
   password = "strong-database-password"
   db_name = "cfms_production"

   [security]
   passwd_min_length = 12
   passwd_must_contain = ["uppercase", "lowercase", "digit", "special"]
   enable_passwd_force_expiration = true
   passwd_expire_after_days = 90

配置文件安全
------------------------------

1. **权限控制**

   限制配置文件的读取权限：

   .. code-block:: console

      $ chmod 600 config.toml
      $ chown cfms-user:cfms-group config.toml

2. **版本控制**

   不要在 Git 中提交包含敏感信息的配置文件：

   .. code-block:: text

      # .gitignore
      config.toml
      *.db
      content/

3. **密钥管理**

   考虑使用环境变量或密钥管理服务：

   .. code-block:: python

      import os
      secret_key = os.environ.get('CFMS_SECRET_KEY')

故障排除
------------------------------

配置文件语法错误
^^^^^^^^^^^^^^^^

如果看到 TOML 解析错误，检查：

- 引号是否正确闭合
- 数组和表的语法是否正确
- 布尔值是否使用 ``true``/``false``（小写）
- 数字是否包含非法字符

配置不生效
^^^^^^^^^^

确保：

- 配置文件位于正确的目录
- 文件名为 ``config.toml``（区分大小写）
- 重启了服务器（配置不会热加载）
- 检查日志中是否有配置加载错误

相关文档
--------

- :doc:`setup` - 安装和初始配置
- :doc:`security` - 安全配置详解
- :doc:`database` - 数据库配置详解
