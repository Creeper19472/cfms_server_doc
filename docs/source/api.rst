WebSocket 通信协议
==================

本章节介绍 CFMS 的 WebSocket 通信协议，包括连接建立、消息格式和通用规范。

协议概述
--------

CFMS 使用 **WebSocket** 协议进行客户端与服务器之间的实时双向通信。协议版本为 **v3**。

核心特性
^^^^^^^^

- **传输协议**：WebSocket over TLS (WSS)
- **数据格式**：JSON
- **认证方式**：JWT (JSON Web Token)
- **编码**：UTF-8
- **协议版本**：3

连接服务器
----------

默认配置
^^^^^^^^

服务器默认监听地址：``wss://localhost:5104``

Python 连接示例
^^^^^^^^^^^^^^^^

使用 ``websockets`` 库连接：

.. code-block:: python

   from websockets.sync.client import connect
   import ssl
   import json

   # 创建 SSL 上下文（自签名证书）
   ssl_context = ssl.create_default_context()
   ssl_context.check_hostname = False
   ssl_context.verify_mode = ssl.CERT_NONE

   # 连接到服务器
   with connect("wss://localhost:5104", ssl=ssl_context) as websocket:
       # 发送请求
       request = {
           "action": "server_info",
           "data": {},
           "username": "",
           "token": ""
       }
       websocket.send(json.dumps(request))
       
       # 接收响应
       response = websocket.recv()
       print(json.loads(response))

.. warning::

   上述示例跳过了 SSL 证书验证，仅适用于开发环境。
   生产环境中应使用受信任的证书并启用完整的证书验证。

JavaScript 连接示例
^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

   const ws = new WebSocket('wss://localhost:5104');

   ws.onopen = function() {
       // 发送请求
       const request = {
           action: "server_info",
           data: {},
           username: "",
           token: ""
       };
       ws.send(JSON.stringify(request));
   };

   ws.onmessage = function(event) {
       const response = JSON.parse(event.data);
       console.log(response);
   };

   ws.onerror = function(error) {
       console.error('WebSocket Error:', error);
   };

消息格式规范
------------

请求格式
^^^^^^^^

所有客户端请求必须遵循以下 JSON 格式：

.. code-block:: json

   {
       "action": "string",
       "data": {},
       "username": "string",
       "token": "string"
   }

请求字段说明：

.. list-table::
   :header-rows: 1
   :widths: 15 10 50

   * - 字段名
     - 类型
     - 说明
   * - action
     - String
     - 必需。要执行的操作名称，如 ``"login"``, ``"get_document"`` 等。
       详见 :doc:`api_refs` 获取完整列表。
   * - data
     - Object
     - 必需。操作所需的数据。具体内容因 action 而异。空对象 ``{}`` 表示无需额外数据。
   * - username
     - String
     - 用户名。某些操作（如登录）可以为空字符串，大多数操作需要有效用户名。
   * - token
     - String
     - JWT 认证令牌。登录后获得，用于后续请求的身份验证。
       登录和部分无需认证的操作可以为空字符串。

响应格式
^^^^^^^^

服务器响应遵循以下 JSON 格式：

.. code-block:: json

   {
       "code": 200,
       "message": "string",
       "data": {},
       "protocol_version": 3
   }

响应字段说明：

.. list-table::
   :header-rows: 1
   :widths: 20 10 50

   * - 字段名
     - 类型
     - 说明
   * - code
     - Integer
     - HTTP 风格的状态码。200 表示成功，4xx 表示客户端错误，5xx 表示服务器错误。
   * - message
     - String
     - 响应消息的文本描述。成功时为操作描述，失败时为错误说明。
   * - data
     - Object
     - 响应数据。具体内容因请求类型而异。错误时可能为空对象。
   * - protocol_version
     - Integer
     - 协议版本号，当前为 3。

状态码规范
----------

CFMS 使用 HTTP 风格的状态码：

成功状态码 (2xx)
^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - 代码
     - 含义
     - 说明
   * - 200
     - OK
     - 请求成功
   * - 202
     - Accepted
     - 请求被接受但需要额外操作（如两步验证）

客户端错误 (4xx)
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - 代码
     - 含义
     - 说明
   * - 400
     - Bad Request
     - 请求格式错误或缺少必需字段
   * - 401
     - Unauthorized
     - 未认证或认证失败
   * - 403
     - Forbidden
     - 已认证但无权限执行操作，或密码需要更改
   * - 404
     - Not Found
     - 请求的资源不存在
   * - 409
     - Conflict
     - 资源冲突（如重名）

服务器错误 (5xx)
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - 代码
     - 含义
     - 说明
   * - 500
     - Internal Server Error
     - 服务器内部错误

特殊状态码
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - 代码
     - 含义
     - 说明
   * - 999
     - Lockdown
     - 服务器处于锁定模式，仅允许特定操作

认证流程
--------

1. 获取服务器信息（可选）
^^^^^^^^^^^^^^^^^^^^^^^^^^

首次连接时，可以先查询服务器信息：

.. code-block:: json

   {
       "action": "server_info",
       "data": {},
       "username": "",
       "token": ""
   }

响应示例：

.. code-block:: json

   {
       "code": 200,
       "message": "Server information retrieved successfully",
       "data": {
           "server_name": "CFMS WebSocket Server",
           "version": "0.1.0.250919_alpha",
           "protocol_version": 3,
           "lockdown": false
       }
   }

2. 用户登录
^^^^^^^^^^^

使用用户名和密码登录：

.. code-block:: json

   {
       "action": "login",
       "data": {
           "username": "admin",
           "password": "your_password"
       },
       "username": "",
       "token": ""
   }

成功响应：

.. code-block:: json

   {
       "code": 200,
       "message": "Login successful",
       "data": {
           "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
           "exp": 1699999999.0,
           "nickname": "管理员",
           "permissions": ["shutdown", "create_document", ...],
           "groups": ["sysop", "user"]
       }
   }

失败响应：

.. code-block:: json

   {
       "code": 401,
       "message": "Invalid credentials",
       "data": {}
   }

3. 使用令牌进行后续请求
^^^^^^^^^^^^^^^^^^^^^^^

登录成功后，使用返回的 token 进行后续操作：

.. code-block:: json

   {
       "action": "list_directory",
       "data": {
           "folder_id": "root"
       },
       "username": "admin",
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }

4. 刷新令牌
^^^^^^^^^^^

令牌默认有效期为 1 小时（3600 秒）。过期前可以刷新：

.. code-block:: json

   {
       "action": "refresh_token",
       "data": {},
       "username": "admin",
       "token": "your_current_token"
   }

响应：

.. code-block:: json

   {
       "code": 200,
       "message": "Token refreshed successfully",
       "data": {
           "token": "new_token_here",
           "exp": 1700003599.0
       }
   }

无需认证的操作
--------------

以下操作无需用户认证即可执行：

1. **server_info** - 获取服务器信息
2. **login** - 用户登录
3. **register_listener** - 注册为监听连接

文件传输
--------

CFMS 通过特殊的任务机制处理文件上传和下载。

文件下载流程
^^^^^^^^^^^^

1. 创建下载任务：

.. code-block:: json

   {
       "action": "download_file",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

2. 服务器创建任务并返回：

.. code-block:: json

   {
       "code": 200,
       "message": "Download task created",
       "data": {
           "task_id": "task_abc123",
           "file_id": "file_xyz789",
           "start_time": 1699999999.0,
           "end_time": 1700003599.0
       }
   }

3. 使用 task_id 下载文件数据（通过二进制消息）

文件上传流程
^^^^^^^^^^^^

1. 创建上传任务
2. 服务器返回 task_id
3. 使用 task_id 上传文件数据（通过二进制消息）

.. note::

   文件传输的详细实现请参考客户端示例代码。

锁定模式 (Lockdown)
-------------------

服务器可以进入"锁定模式"，此时仅允许特定操作：

- server_info
- register_listener
- login
- refresh_token
- validate_2fa
- upload_file
- download_file

拥有 ``bypass_lockdown`` 权限的用户不受锁定模式影响。

锁定模式状态可通过 ``server_info`` 查询：

.. code-block:: json

   {
       "data": {
           "lockdown": true
       }
   }

错误处理
--------

常见错误场景
^^^^^^^^^^^^

1. **JSON 格式错误**

响应：

.. code-block:: json

   {
       "code": 400,
       "message": "Invalid JSON format",
       "data": {}
   }

2. **缺少必需字段**

响应：

.. code-block:: json

   {
       "code": 400,
       "message": "Missing required field: document_id",
       "data": {
           "validator": "required",
           "validator_value": ["document_id"]
       }
   }

3. **令牌过期**

响应：

.. code-block:: json

   {
       "code": 401,
       "message": "Token expired",
       "data": {}
   }

4. **权限不足**

响应：

.. code-block:: json

   {
       "code": 403,
       "message": "Permission denied",
       "data": {}
   }

5. **资源不存在**

响应：

.. code-block:: json

   {
       "code": 404,
       "message": "Document not found",
       "data": {}
   }

最佳实践
--------

连接管理
^^^^^^^^

1. **使用连接池**：避免频繁建立和关闭连接
2. **实现重连机制**：处理网络中断
3. **心跳检测**：定期发送 ``server_info`` 保持连接活跃

令牌管理
^^^^^^^^

1. **安全存储**：不要在客户端明文存储令牌
2. **主动刷新**：在令牌过期前主动刷新
3. **失效处理**：令牌失效时重新登录

错误处理
^^^^^^^^

1. **解析状态码**：根据状态码实现不同的处理逻辑
2. **显示错误消息**：向用户展示 ``message`` 字段
3. **日志记录**：记录所有错误响应用于调试

安全建议
^^^^^^^^

1. **使用 WSS**：始终使用加密的 WebSocket 连接
2. **验证证书**：生产环境中验证 SSL 证书
3. **保护令牌**：防止令牌泄露
4. **实现超时**：为所有请求设置合理的超时时间

下一步
------

- 查看 :doc:`api_refs` 了解所有可用的 API 接口
- 学习 :doc:`groups_and_rights` 了解权限系统
- 探索 :doc:`file_management` 了解文件传输的详细实现
