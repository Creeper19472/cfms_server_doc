API 接口参考
====================================

本章节详细列出了 CFMS 服务端支持的所有 API 接口。所有接口通过 WebSocket 连接以 JSON 格式进行通信。

.. contents:: 目录
   :local:
   :depth: 2

接口概览
--------

CFMS API 按功能分为以下几类，共计 45+ 个接口：

.. list-table:: API 分类
   :header-rows: 1
   :widths: 20 15 50

   * - 类别
     - 接口数量
     - 说明
   * - 服务器与认证
     - 4
     - 服务器信息、监听器注册、用户登录、令牌刷新
   * - 两步验证
     - 5
     - TOTP 两步验证的设置、验证、禁用和状态查询
   * - 文档管理
     - 9
     - 文档的增删改查、移动和权限管理
   * - 文件传输
     - 2
     - 文件的上传和下载
   * - 目录管理
     - 8
     - 目录的增删改查、移动和权限管理
   * - 用户管理
     - 10
     - 用户账户的创建、删除、修改、封禁和头像管理
   * - 用户组管理
     - 6
     - 用户组的创建、删除、重命名和权限配置
   * - 访问控制
     - 2
     - 授予访问权限和查看访问记录
   * - 系统管理
     - 3
     - 服务器关闭、锁定模式和审计日志

通用规范
--------

所有 API 请求遵循统一格式（详见 :doc:`api`）：

.. code-block:: json

   {
       "action": "api_name",
       "data": { },
       "username": "user",
       "token": "jwt_token"
   }

需要认证的接口（除特别说明外的所有接口）需要提供有效的 ``username`` 和 ``token``。

===================
服务器与认证 API
===================

server_info - 获取服务器信息
-----------------------------

获取服务器的基本信息和状态。

**认证要求**：无

**请求**：

.. code-block:: json

   {
       "action": "server_info",
       "data": {},
       "username": "",
       "token": ""
   }

**响应**：

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

**字段说明**：

- ``server_name``: 服务器名称
- ``version``: 服务器版本
- ``protocol_version``: 协议版本号
- ``lockdown``: 是否处于锁定模式

login - 用户登录
-----------------

使用用户名和密码登录系统。

**认证要求**：无

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 50

   * - 字段
     - 类型
     - 说明
   * - username
     - String
     - 用户名，长度至少 1
   * - password
     - String
     - 密码，长度至少 1

**请求示例**：

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

**成功响应**：

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

**字段说明**：

- ``token``: JWT 认证令牌，有效期 1 小时
- ``exp``: 令牌过期时间戳
- ``nickname``: 用户昵称
- ``permissions``: 用户拥有的所有权限列表
- ``groups``: 用户所属的用户组列表

**错误响应**：

- ``400``: 缺少用户名或密码
- ``401``: 用户名或密码错误
- ``403``: 密码已过期或不符合要求，需要修改

refresh_token - 刷新令牌
-------------------------

刷新用户的 JWT 令牌以延长会话时间。

**认证要求**：是

**请求**：

.. code-block:: json

   {
       "action": "refresh_token",
       "data": {},
       "username": "admin",
       "token": "current_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Token refreshed successfully",
       "data": {
           "token": "new_token_here",
           "exp": 1700003599.0
       }
   }

**错误响应**：

- ``401``: 当前令牌无效或已过期

register_listener - 注册监听连接
---------------------------------

将当前连接注册为监听器，用于接收服务器推送的通知。

**认证要求**：无

**请求**：

.. code-block:: json

   {
       "action": "register_listener",
       "data": {},
       "username": "",
       "token": ""
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Registered as a listener",
       "data": {},
       "protocol_version": 3
   }

.. note::

   监听连接不应主动发送其他请求，仅用于接收服务器推送的消息。服务器在触发事件时会向所有已注册的监听连接广播消息。

===================
两步验证 API
===================

setup_2fa - 设置两步验证
-------------------------

为当前用户设置 TOTP（基于时间的一次性密码）两步验证。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 50

   * - 字段
     - 类型
     - 说明
   * - method
     - String
     - 可选。验证方法，目前仅支持 "totp"

**请求示例**：

.. code-block:: json

   {
       "action": "setup_2fa",
       "data": {},
       "username": "admin",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication setup initiated. Please verify with your authenticator app.",
       "data": {
           "secret": "BASE32_SECRET_KEY",
           "provisioning_uri": "otpauth://totp/CFMS:admin?secret=...",
           "backup_codes": ["code1", "code2", ...]
       },
       "protocol_version": 3
   }

**字段说明**：

- ``secret``: TOTP 密钥（Base32 编码），用于手动输入
- ``provisioning_uri``: 配置 URI，可生成 QR 码供认证器应用扫描
- ``backup_codes``: 备份代码列表，用于在无法使用认证器时恢复访问

**错误响应**：

- ``400``: 两步验证已启用，需要先取消
- ``404``: 用户不存在

.. warning::

   请妥善保管备份代码！如果丢失认证器且没有备份代码，将无法登录账户。

validate_2fa - 验证两步验证
---------------------------

验证并启用两步验证。在设置两步验证后必须验证才能生效。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 50

   * - 字段
     - 类型
     - 说明
   * - token
     - String
     - 认证器生成的 6 位验证码

**请求示例**：

.. code-block:: json

   {
       "action": "validate_2fa",
       "data": {
           "token": "123456"
       },
       "username": "admin",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication enabled successfully",
       "data": {
           "method": "totp"
       },
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 两步验证未设置或已启用
- ``401``: 验证码无效
- ``404``: 用户不存在

disable_2fa - 禁用两步验证
--------------------------

禁用当前用户的两步验证。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 50

   * - 字段
     - 类型
     - 说明
   * - token
     - String
     - 认证器生成的 6 位验证码或备份代码

**请求示例**：

.. code-block:: json

   {
       "action": "disable_2fa",
       "data": {
           "token": "123456"
       },
       "username": "admin",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication disabled successfully",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 两步验证未启用
- ``401``: 验证码无效
- ``404``: 用户不存在

cancel_2fa_setup - 取消两步验证设置
-----------------------------------

取消正在进行中但尚未验证的两步验证设置。

**认证要求**：是

**请求**：

.. code-block:: json

   {
       "action": "cancel_2fa_setup",
       "data": {},
       "username": "admin",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication setup cancelled",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 没有待验证的两步验证设置或两步验证已启用
- ``404``: 用户不存在

get_2fa_status - 查询两步验证状态
---------------------------------

查询当前用户的两步验证状态。

**认证要求**：是

**请求**：

.. code-block:: json

   {
       "action": "get_2fa_status",
       "data": {},
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication status retrieved",
       "data": {
           "enabled": true,
           "method": "totp"
       },
       "protocol_version": 3
   }

**字段说明**：

- ``enabled``: 两步验证是否已启用
- ``method``: 验证方法（"totp" 或 null）

===================
文档管理 API
===================

list_directory - 列出目录内容
------------------------------

列出指定目录下的所有文档和子目录。

**认证要求**：是

**所需权限**：对目标目录的读取权限（或 ``super_list_directory``）

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String/null
     - 目录 ID。使用 null 表示根目录

**请求示例**：

.. code-block:: json

   {
       "action": "list_directory",
       "data": {
           "folder_id": null
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Directory listing successful",
       "data": {
           "parent_id": "/",
           "documents": [
               {
                   "id": "doc1",
                   "title": "Document 1",
                   "created_time": 1699999999.0,
                   "last_modified": 1699999999.0,
                   "size": 1024
               }
           ],
           "folders": [
               {
                   "id": "folder1",
                   "name": "Subfolder",
                   "created_time": 1699999999.0
               }
           ]
       },
       "protocol_version": 3
   }

**字段说明**：

- ``parent_id``: 父目录 ID，根目录的父目录为 "/"，null 表示没有父目录
- ``documents``: 文档列表，每个文档包含 id、title、created_time、last_modified 和 size
- ``folders``: 子目录列表，每个目录包含 id、name 和 created_time

**错误响应**：

- ``403``: 权限不足
- ``404``: 目录不存在

create_document - 创建文档
--------------------------

在指定目录下创建新文档并返回上传任务信息。

**认证要求**：是

**所需权限**：``create_document``（或 ``super_create_document`` 忽略目录写权限）

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - title
     - String
     - 文档标题，必填
   * - folder_id
     - String/null
     - 所属目录 ID，null 表示根目录（可选）
   * - access_rules
     - Object
     - 访问规则配置（可选）

**请求示例**：

.. code-block:: json

   {
       "action": "create_document",
       "data": {
           "title": "My Document",
           "folder_id": null,
           "access_rules": {}
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Task successfully created",
       "data": {
           "document_id": "abc123...",
           "task_data": {
               "task_id": "task123",
               "start_time": 1699999999.0,
               "end_time": 1700003599.0
           }
       },
       "protocol_version": 3
   }

**字段说明**：

- ``document_id``: 新创建的文档 ID
- ``task_data``: 文件上传任务信息
  - ``task_id``: 任务 ID，用于后续文件上传
  - ``start_time``: 任务开始时间
  - ``end_time``: 任务结束时间（通常为开始时间 + 1小时）

**错误响应**：

- ``400``: 缺少标题或设置访问规则失败
- ``403``: 权限不足或无权设置访问规则
- ``404``: 父目录不存在
- ``409``: 文档名称冲突（当配置不允许重名时）

get_document - 获取文档
------------------------

获取文档的基本信息并创建下载任务。

**认证要求**：是

**所需权限**：对文档的读取权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**请求示例**：

.. code-block:: json

   {
       "action": "get_document",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document successfully fetched",
       "data": {
           "document_id": "doc123",
           "title": "My Document",
           "task_data": {
               "task_id": "task456",
               "start_time": 1699999999.0,
               "end_time": 1700003599.0
           }
       },
       "protocol_version": 3
   }

**字段说明**：

- ``task_data``: 文件下载任务信息，使用 ``download_file`` 接口下载文件内容

**错误响应**：

- ``403``: 权限不足
- ``404``: 文档不存在或文档没有活动版本

get_document_info - 获取文档信息
--------------------------------

获取文档的详细信息，包括大小、时间和访问规则。

**认证要求**：是

**所需权限**：对文档的读取权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**请求示例**：

.. code-block:: json

   {
       "action": "get_document_info",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document info retrieved successfully",
       "data": {
           "document_id": "doc123",
           "parent_id": null,
           "title": "My Document",
           "size": 2048,
           "created_time": 1699999999.0,
           "last_modified": 1700000000.0,
           "access_rules": [
               {
                   "rule_id": 1,
                   "access_type": "read",
                   "rule_data": {...}
               }
           ],
           "info_code": 0
       },
       "protocol_version": 3
   }

**info_code 说明**：

- ``0``: 成功获取所有信息
- ``1``: 无权查看访问规则（access_rules 为空）

**错误响应**：

- ``403``: 权限不足
- ``404``: 文档不存在或文档没有活动版本

get_document_access_rules - 获取文档访问规则
---------------------------------------------

获取文档的访问规则配置，按访问类型分组。

**认证要求**：是

**所需权限**：对文档的读取权限且拥有 ``view_access_rules`` 权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**请求示例**：

.. code-block:: json

   {
       "action": "get_document_access_rules",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document access rules retrieved successfully",
       "data": {
           "read": [
               {
                   "match": "any",
                   "match_groups": [...]
               }
           ],
           "write": [...],
           "move": [...],
           "manage": [...]
       },
       "protocol_version": 3
   }

**字段说明**：

响应数据是一个字典，键为访问类型（read、write、move、manage），值为该类型的规则数据数组。

**错误响应**：

- ``403``: 权限不足或无权查看访问规则
- ``404``: 文档不存在

delete_document - 删除文档
---------------------------

删除指定文档及其所有版本。

**认证要求**：是

**所需权限**：``delete_document`` 且对文档有写权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 要删除的文档 ID

**请求示例**：

.. code-block:: json

   {
       "action": "delete_document",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document successfully deleted",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``403``: 权限不足
- ``404``: 文档不存在
- ``500``: 删除失败（可能有正在进行的下载任务）

rename_document - 重命名文档
----------------------------

修改文档的标题。

**认证要求**：是

**所需权限**：``rename_document`` 且对文档有写权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID
   * - new_title
     - String
     - 新标题

**请求示例**：

.. code-block:: json

   {
       "action": "rename_document",
       "data": {
           "document_id": "doc123",
           "new_title": "Updated Title"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document renamed successfully",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 新标题与当前标题相同或名称冲突
- ``403``: 权限不足
- ``404``: 文档不存在

move_document - 移动文档
------------------------

将文档移动到另一个目录。

**认证要求**：是

**所需权限**：``move`` 且对文档有移动权限，对目标目录有写权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID
   * - target_folder_id
     - String/null
     - 目标目录 ID，null 表示根目录（可选，默认不移动）

**请求示例**：

.. code-block:: json

   {
       "action": "move_document",
       "data": {
           "document_id": "doc123",
           "target_folder_id": "folder456"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Success",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 目标目录中存在同名文档或文件夹
- ``403``: 权限不足
- ``404``: 文档或目标目录不存在

upload_document - 上传文档版本
------------------------------

为已存在的文档创建新版本并返回上传任务。

**认证要求**：是

**所需权限**：对文档的写权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**请求示例**：

.. code-block:: json

   {
       "action": "upload_document",
       "data": {
           "document_id": "doc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Task successfully created",
       "data": {
           "task_data": {
               "task_id": "task789",
               "start_time": 1699999999.0,
               "end_time": 1700003599.0
           }
       },
       "protocol_version": 3
   }

**字段说明**：

- ``task_data``: 上传任务信息，使用 ``upload_file`` 接口上传文件内容

**错误响应**：

- ``403``: 权限不足
- ``404``: 文档不存在

set_document_rules - 设置文档访问规则
-------------------------------------

为文档设置访问控制规则。

**认证要求**：是

**所需权限**：``set_access_rules`` 且对文档有管理权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID
   * - access_rules
     - Object
     - 访问规则配置，键为访问类型，值为规则数组

**请求示例**：

.. code-block:: json

   {
       "action": "set_document_rules",
       "data": {
           "document_id": "doc123",
           "access_rules": {
               "read": [
                   {
                       "match": "any",
                       "match_groups": ["user"]
                   }
               ],
               "write": []
           }
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Set access rules successfully",
       "data": {},
       "protocol_version": 3
   }

**错误响应**：

- ``400``: 规则格式错误
- ``403``: 权限不足
- ``404``: 文档不存在

.. note::

   访问规则的详细格式请参考 :doc:`access_control`。

===================
文件传输 API
===================

download_file - 下载文件
--------------------------

通过任务 ID 下载文件。此接口需要先通过 ``get_document`` 获取任务 ID。

**认证要求**：否（任务 ID 本身提供认证）

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - task_id
     - String
     - 下载任务 ID

**请求示例**：

.. code-block:: json

   {
       "action": "download_file",
       "data": {
           "task_id": "task123"
       },
       "username": "",
       "token": ""
   }

**响应**：

服务器会直接通过 WebSocket 发送文件的二进制数据，不返回 JSON 响应。

**错误响应**：

- ``400``: 任务状态无效或任务时间无效
- ``404``: 任务不存在

.. note::

   此接口是锁定模式白名单操作，即使在锁定模式下也可使用。
   任务有效期为 1 小时，超时后需要重新创建任务。

upload_file - 上传文件
-----------------------

通过任务 ID 上传文件。此接口需要先通过 ``create_document`` 或 ``upload_document`` 获取任务 ID。

**认证要求**：否（任务 ID 本身提供认证）

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - task_id
     - String
     - 上传任务 ID

**请求示例**：

.. code-block:: json

   {
       "action": "upload_file",
       "data": {
           "task_id": "task456"
       },
       "username": "",
       "token": ""
   }

**响应**：

服务器准备好接收文件数据后会发送确认响应，客户端应通过 WebSocket 发送文件的二进制数据。

**错误响应**：

- ``400``: 任务状态无效或任务时间无效
- ``404``: 任务不存在

.. note::

   此接口是锁定模式白名单操作。
   文件上传采用分块传输，默认块大小为 2MB。
   任务有效期为 1 小时。

create_directory - 创建目录
----------------------------

创建新目录。

**认证要求**：是

**所需权限**：``create_directory`` 或 ``super_create_directory``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 新目录的 ID
   * - name
     - String
     - 目录名称
   * - parent_id
     - String
     - 父目录 ID，"root" 表示根目录

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Directory created successfully",
       "data": {
           "folder_id": "new_folder"
       }
   }

get_directory_info - 获取目录信息
---------------------------------

获取目录的详细信息。

**认证要求**：是

**所需权限**：对目录的读取权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 目录 ID

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Directory info retrieved successfully",
       "data": {
           "folder_id": "folder1",
           "name": "My Folder",
           "parent_id": "root",
           "created_time": 1699999999.0,
           "access_rules": []
       }
   }

delete_directory - 删除目录
---------------------------

删除目录及其所有内容。

**认证要求**：是

**所需权限**：``delete_directory``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 要删除的目录 ID

.. warning::

   删除目录会同时删除其中的所有文档和子目录！

rename_directory - 重命名目录
------------------------------

修改目录名称。

**认证要求**：是

**所需权限**：``rename_directory``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 目录 ID
   * - new_name
     - String
     - 新名称

move_directory - 移动目录
--------------------------

将目录移动到另一个父目录。

**认证要求**：是

**所需权限**：``move``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 目录 ID
   * - target_parent_id
     - String
     - 目标父目录 ID

===================
用户管理 API
===================

list_users - 列出所有用户
--------------------------

列出系统中的所有用户。

**认证要求**：是

**所需权限**：``list_users``

**请求**：

.. code-block:: json

   {
       "action": "list_users",
       "data": {},
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Users listed successfully",
       "data": {
           "users": [
               {
                   "username": "admin",
                   "nickname": "管理员",
                   "created_time": 1699999999.0,
                   "last_login": 1700000000.0
               },
               {
                   "username": "user1",
                   "nickname": "User 1",
                   "created_time": 1700000000.0,
                   "last_login": null
               }
           ]
       }
   }

create_user - 创建用户
-----------------------

创建新用户账户。

**认证要求**：是

**所需权限**：``create_user``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - username
     - String
     - 用户名，唯一
   * - password
     - String
     - 初始密码
   * - nickname
     - String
     - 用户昵称（可选）

**请求示例**：

.. code-block:: json

   {
       "action": "create_user",
       "data": {
           "username": "newuser",
           "password": "secure_password",
           "nickname": "New User"
       },
       "username": "admin",
       "token": "your_token"
   }

delete_user - 删除用户
-----------------------

删除用户账户。

**认证要求**：是

**所需权限**：``delete_user``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 要删除的用户名

rename_user - 重命名用户
-------------------------

修改用户的用户名。

**认证要求**：是

**所需权限**：``rename_user``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - old_username
     - String
     - 当前用户名
   * - new_username
     - String
     - 新用户名

get_user_info - 获取用户信息
----------------------------

获取用户的详细信息。

**认证要求**：是

**所需权限**：``get_user_info``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 目标用户名

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User info retrieved successfully",
       "data": {
           "username": "user1",
           "nickname": "User 1",
           "created_time": 1699999999.0,
           "last_login": 1700000000.0,
           "groups": ["user"],
           "permissions": ["set_passwd"]
       }
   }

change_user_groups - 修改用户组
-------------------------------

修改用户所属的用户组。

**认证要求**：是

**所需权限**：``change_user_groups``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 目标用户名
   * - groups
     - Array
     - 用户组配置数组

**组配置格式**：

.. code-block:: json

   {
       "group_name": "sysop",
       "start_time": 0,
       "end_time": null
   }

- ``start_time``: 生效时间（Unix 时间戳），0 或 null 表示立即生效
- ``end_time``: 过期时间（Unix 时间戳），null 表示永不过期

set_passwd - 修改密码
----------------------

修改用户密码。

**认证要求**：是

**所需权限**：``set_passwd``（修改自己）或 ``super_set_passwd``（修改他人）

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 要修改密码的用户名
   * - old_password
     - String
     - 当前密码（修改自己时必需）
   * - new_password
     - String
     - 新密码

block_user - 封禁用户
----------------------

封禁用户账户。

**认证要求**：是

**所需权限**：``block``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 要封禁的用户名
   * - reason
     - String
     - 封禁原因（可选）
   * - end_time
     - Float
     - 解封时间（Unix 时间戳），null 表示永久封禁

unblock_user - 解封用户
------------------------

解除用户封禁。

**认证要求**：是

**所需权限**：``unblock``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_username
     - String
     - 要解封的用户名

===================
用户组管理 API
===================

list_groups - 列出用户组
-------------------------

列出系统中的所有用户组。

**认证要求**：是

**所需权限**：``list_groups``

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Groups listed successfully",
       "data": {
           "groups": [
               {
                   "group_name": "user",
                   "created_time": 1699999999.0
               },
               {
                   "group_name": "sysop",
                   "created_time": 1699999999.0
               }
           ]
       }
   }

create_group - 创建用户组
--------------------------

创建新用户组。

**认证要求**：是

**所需权限**：``create_group``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - group_name
     - String
     - 用户组名称（唯一）

delete_group - 删除用户组
--------------------------

删除用户组。

**认证要求**：是

**所需权限**：``delete_group``

.. warning::

   删除用户组会影响所有属于该组的用户！

rename_group - 重命名用户组
----------------------------

修改用户组名称。

**认证要求**：是

**所需权限**：``rename_group``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - old_name
     - String
     - 当前组名
   * - new_name
     - String
     - 新组名

get_group_info - 获取用户组信息
-------------------------------

获取用户组的详细信息。

**认证要求**：是

**所需权限**：``get_group_info``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - group_name
     - String
     - 用户组名称

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Group info retrieved successfully",
       "data": {
           "group_name": "sysop",
           "created_time": 1699999999.0,
           "permissions": [
               {
                   "permission": "shutdown",
                   "start_time": 0,
                   "end_time": null
               },
               {
                   "permission": "create_document",
                   "start_time": 0,
                   "end_time": null
               }
           ]
       }
   }

change_group_permissions - 修改用户组权限
-----------------------------------------

修改用户组的权限配置。

**认证要求**：是

**所需权限**：``set_group_permissions``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - group_name
     - String
     - 用户组名称
   * - permissions
     - Array
     - 权限配置数组

**权限配置格式**：

.. code-block:: json

   {
       "permission": "create_document",
       "start_time": 0,
       "end_time": null
   }

===================
访问控制 API
===================

grant_access - 授予访问权限
----------------------------

为用户或用户组授予对特定资源的访问权限。

**认证要求**：是

**所需权限**：``manage_access``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_type
     - String
     - 目标类型："document" 或 "folder"
   * - target_id
     - String
     - 目标 ID
   * - subject_type
     - String
     - 授权对象类型："user" 或 "group"
   * - subject_name
     - String
     - 用户名或组名
   * - access_type
     - String
     - 访问类型："read", "write", "move", "manage"

**请求示例**：

.. code-block:: json

   {
       "action": "grant_access",
       "data": {
           "target_type": "document",
           "target_id": "doc123",
           "subject_type": "user",
           "subject_name": "user1",
           "access_type": "read"
       },
       "username": "admin",
       "token": "your_token"
   }

view_access_entries - 查看访问记录
----------------------------------

查看资源的访问控制记录。

**认证要求**：是

**所需权限**：``view_access_entries``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - target_type
     - String
     - 目标类型："document" 或 "folder"
   * - target_id
     - String
     - 目标 ID

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Access entries retrieved successfully",
       "data": {
           "entries": [
               {
                   "subject_type": "user",
                   "subject_name": "user1",
                   "access_type": "read",
                   "granted_time": 1699999999.0
               }
           ]
       }
   }

===================
系统管理 API
===================

lockdown - 锁定系统
--------------------

启用或禁用系统锁定模式。锁定模式下，只有白名单内的操作和拥有 ``bypass_lockdown`` 权限的用户可以操作。

**认证要求**：是

**所需权限**：``apply_lockdown``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - enable
     - Boolean
     - true 启用锁定，false 禁用锁定

**请求示例**：

.. code-block:: json

   {
       "action": "lockdown",
       "data": {
           "enable": true
       },
       "username": "admin",
       "token": "your_token"
   }

**锁定模式白名单**：

- server_info
- register_listener
- login
- refresh_token
- upload_file
- download_file

view_audit_logs - 查看审计日志
-------------------------------

查看系统审计日志。

**认证要求**：是

**所需权限**：``view_audit_logs``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - limit
     - Integer
     - 返回记录数量限制（可选，默认 100）
   * - offset
     - Integer
     - 偏移量，用于分页（可选，默认 0）

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Audit logs retrieved successfully",
       "data": {
           "logs": [
               {
                   "id": 1,
                   "action": "login",
                   "username": "admin",
                   "result": 200,
                   "target": "admin",
                   "remote_address": "127.0.0.1",
                   "timestamp": 1699999999.0
               }
           ],
           "total": 1000
       }
   }

===================
文件传输 API
===================

download_file - 下载文件
--------------------------

创建文件下载任务。

**认证要求**：是

**所需权限**：对文档的读取权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**响应**：

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

**后续步骤**：

1. 使用返回的 ``task_id`` 通过二进制消息下载文件内容
2. 任务有效期为 1 小时（``end_time`` - ``start_time``）

upload_file - 上传文件
-----------------------

创建文件上传任务。

**认证要求**：部分（可使用 task_id 而无需认证）

**所需权限**：对文档的写入权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - task_id
     - String
     - 上传任务 ID（由 upload_document 创建）

**响应**：确认上传任务已准备就绪

**后续步骤**：

1. 通过二进制消息上传文件内容
2. 文件内容分块传输（默认 2MB 块）

===================
访问规则 API
===================

set_document_rules - 设置文档访问规则
-------------------------------------

为文档设置访问控制规则。

**认证要求**：是

**所需权限**：``set_access_rules``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID
   * - rules
     - Array
     - 访问规则数组

**规则格式**：详见 :doc:`access_control`

set_directory_rules - 设置目录访问规则
---------------------------------------

为目录设置访问控制规则。

**认证要求**：是

**所需权限**：``set_access_rules``

**请求数据**：同 ``set_document_rules``，但使用 ``folder_id``

get_document_access_rules - 获取文档访问规则
---------------------------------------------

获取文档的访问规则配置。

**认证要求**：是

**所需权限**：``view_access_rules``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Access rules retrieved successfully",
       "data": {
           "rules": [
               {
                   "rule_id": 1,
                   "access_type": "read",
                   "rule_data": {
                       "match": "any",
                       "match_groups": [...]
                   }
               }
           ]
       }
   }

get_directory_access_rules - 获取目录访问规则
---------------------------------------------

获取目录的访问规则配置。

**认证要求**：是

**所需权限**：``view_access_rules``

**请求数据**：同 ``get_document_access_rules``，但使用 ``folder_id``

shutdown - 关闭服务器
----------------------

关闭 CFMS 服务器。

**认证要求**：是

**所需权限**：``shutdown``

**请求**：

.. code-block:: json

   {
       "action": "shutdown",
       "data": {},
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Server is shutting down",
       "data": {}
   }

.. danger::

   此操作会立即关闭服务器，所有活动连接将被断开！

常见错误代码
------------

所有 API 可能返回的通用错误：

.. list-table::
   :header-rows: 1
   :widths: 10 30 40

   * - 代码
     - 含义
     - 可能原因
   * - 400
     - Bad Request
     - JSON 格式错误、缺少必需字段、字段类型错误
   * - 401
     - Unauthorized
     - 未提供认证信息、令牌无效或过期
   * - 403
     - Forbidden
     - 权限不足、密码需更改
   * - 404
     - Not Found
     - 请求的资源（文档、目录、用户等）不存在
   * - 409
     - Conflict
     - 资源冲突（如ID重复、名称重复）
   * - 500
     - Internal Server Error
     - 服务器内部错误，查看日志获取详细信息
   * - 999
     - Lockdown
     - 服务器处于锁定模式

相关文档
--------

- :doc:`api` - WebSocket 通信协议详解
- :doc:`groups_and_rights` - 权限系统说明
- :doc:`access_control` - 访问控制规则详解
- :doc:`file_management` - 文件传输详解
