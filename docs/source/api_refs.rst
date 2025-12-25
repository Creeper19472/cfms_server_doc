API 接口参考
====================================

本章节详细列出了 CFMS 服务端支持的所有 API 接口。所有接口通过 WebSocket 连接以 JSON 格式进行通信。

.. contents:: 目录
   :local:
   :depth: 2

接口概览
--------

CFMS API 按功能分为以下几类，共计 49 个接口：

.. list-table:: API 分类
   :header-rows: 1
   :widths: 20 15 50

   * - 类别
     - 接口数量
     - 说明
   * - 服务器与认证
     - 4
     - 服务器信息、监听注册、用户登录、令牌刷新
   * - 两步验证
     - 5
     - TOTP 两步验证的设置、验证、禁用和状态查询
   * - 文档管理
     - 9
     - 文档的增删改查和权限管理
   * - 目录管理
     - 8
     - 目录的增删改查和权限管理
   * - 文件传输
     - 2
     - 文件上传和下载任务管理
   * - 用户管理
     - 11
     - 用户账户的创建、删除、修改、查询和头像管理
   * - 用户组管理
     - 6
     - 用户组的创建、删除和权限配置
   * - 访问控制
     - 2
     - 授予访问权限和查看访问记录
   * - 系统管理
     - 3
     - 锁定模式、审计日志和服务器关闭

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
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 用户名，长度至少 1
   * - password
     - String
     - 是
     - 密码，长度至少 1
   * - 2fa_token
     - String
     - 否
     - 两步验证令牌（TOTP 代码），启用 2FA 的用户必需

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
- ``401``: 用户名或密码错误，或两步验证令牌无效
- ``202``: 需要两步验证（用户已启用 2FA）
- ``403``: 密码已过期或不符合要求，需要修改

**两步验证响应示例**：

当用户启用了两步验证但未提供 2FA 令牌时：

.. code-block:: json

   {
       "code": 202,
       "message": "Two-factor authentication required",
       "data": {
           "method": "totp"
       }
   }

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
       "message": "registered as a listener",
       "data": {}
   }

.. note::

   监听连接不应主动发送其他请求，仅用于接收服务器推送的消息。

=======================
两步验证 API (2FA/TOTP)
=======================

CFMS 支持基于 TOTP (Time-based One-Time Password) 的两步验证，为用户账户提供额外的安全保护。

setup_2fa - 设置两步验证
-------------------------

为当前用户设置两步验证（TOTP）。生成 TOTP 密钥和备份码。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - method
     - String
     - 否
     - 两步验证方法，目前仅支持 ``"totp"``

**请求示例**：

.. code-block:: json

   {
       "action": "setup_2fa",
       "data": {
           "method": "totp"
       },
       "username": "user1",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication setup initiated. Please verify with your authenticator app.",
       "data": {
           "secret": "JBSWY3DPEHPK3PXP",
           "provisioning_uri": "otpauth://totp/CFMS:user1?secret=JBSWY3DPEHPK3PXP&issuer=CFMS",
           "backup_codes": [
               "12345678",
               "87654321",
               "11223344"
           ]
       }
   }

**字段说明**：

- ``secret``: TOTP 密钥，可用于手动输入到验证器应用
- ``provisioning_uri``: 供应 URI，可生成二维码供验证器应用扫描
- ``backup_codes``: 备份码列表，用于在无法使用验证器时恢复账户

**错误响应**：

- ``400``: 两步验证已启用
- ``404``: 用户不存在

.. warning::

   设置完成后必须调用 ``validate_2fa`` 进行验证才能启用两步验证。
   请妥善保存备份码，在丢失验证器设备时需要使用它们。

validate_2fa - 验证并启用两步验证
----------------------------------

验证 TOTP 配置并启用两步验证。用户必须提供验证器应用生成的 6 位数字代码。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - token
     - String
     - 是
     - 验证器应用生成的 6 位 TOTP 代码

**请求示例**：

.. code-block:: json

   {
       "action": "validate_2fa",
       "data": {
           "token": "123456"
       },
       "username": "user1",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication enabled successfully",
       "data": {
           "method": "totp"
       }
   }

**错误响应**：

- ``400``: 两步验证未设置或已启用
- ``401``: 验证码无效
- ``404``: 用户不存在

cancel_2fa_setup - 取消两步验证设置
-----------------------------------

取消尚未完成验证的两步验证设置。移除已生成但未验证的 TOTP 配置。

**认证要求**：是

**请求**：

.. code-block:: json

   {
       "action": "cancel_2fa_setup",
       "data": {},
       "username": "user1",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication setup cancelled",
       "data": {}
   }

**错误响应**：

- ``400``: 没有待验证的两步验证设置
- ``404``: 用户不存在

disable_2fa - 禁用两步验证
---------------------------

禁用并移除用户的两步验证配置。需要提供密码进行身份验证。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - password
     - String
     - 是
     - 用户当前密码

**请求示例**：

.. code-block:: json

   {
       "action": "disable_2fa",
       "data": {
           "password": "your_password"
       },
       "username": "user1",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication disabled successfully",
       "data": {}
   }

**错误响应**：

- ``400``: 两步验证未启用
- ``401``: 密码错误
- ``404``: 用户不存在

.. danger::

   禁用两步验证会降低账户的安全性。请确保在安全的环境中操作。

get_2fa_status - 获取两步验证状态
----------------------------------

查询指定用户的两步验证状态。

**认证要求**：是

**所需权限**：``manage_2fa``（查询他人状态时）

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - target
     - String
     - 否
     - 目标用户名。不提供时查询自己的状态

**请求示例**：

.. code-block:: json

   {
       "action": "get_2fa_status",
       "data": {
           "target": "user1"
       },
       "username": "admin",
       "token": "your_token"
   }

**成功响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Two-factor authentication status retrieved successfully",
       "data": {
           "enabled": true,
           "method": "totp"
       }
   }

**字段说明**：

- ``enabled``: 是否已启用两步验证
- ``method``: 两步验证方法（``"totp"`` 或 ``null``）

**错误响应**：

- ``403``: 权限不足（查询他人状态时）
- ``404``: 用户不存在

===================
文档管理 API
===================

list_directory - 列出目录内容
------------------------------

列出指定目录下的所有文档和子目录。

**认证要求**：是

**所需权限**：对目标目录的读取权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - folder_id
     - String
     - 目录 ID，使用 "root" 表示根目录

**请求示例**：

.. code-block:: json

   {
       "action": "list_directory",
       "data": {
           "folder_id": "root"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Directory listed successfully",
       "data": {
           "documents": [
               {
                   "id": "doc1",
                   "title": "Document 1",
                   "size": 1024,
                   "created_time": 1699999999.0,
                   "last_modified": 1699999999.0
               }
           ],
           "folders": [
               {
                   "id": "folder1",
                   "name": "Subfolder",
                   "created_time": 1699999999.0
               }
           ]
       }
   }

create_document - 创建文档
--------------------------

在指定目录下创建新文档。文档 ID 将自动生成。

**认证要求**：是

**所需权限**：``create_document`` 或 ``super_create_document``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - title
     - String
     - 是
     - 文档标题（至少 1 个字符）
   * - folder_id
     - String/null
     - 否
     - 所属目录 ID，null 或不提供表示根目录
   * - access_rules
     - Object
     - 否
     - 访问规则配置（可选）

**请求示例**：

.. code-block:: json

   {
       "action": "create_document",
       "data": {
           "title": "My Document",
           "folder_id": "folder123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document created successfully",
       "data": {
           "document_id": "auto_generated_id_123"
       }
   }

**字段说明**：

- ``document_id``: 服务器自动生成的文档 ID

**错误响应**：

- ``400``: 缺少必需字段或字段格式错误
- ``403``: 权限不足
- ``404``: 父目录不存在

get_document - 获取文档
------------------------

获取文档的完整信息（不包含文件内容）。

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
       "message": "Document retrieved successfully",
       "data": {
           "document_id": "my_doc",
           "title": "My Document",
           "folder_id": "root",
           "created_time": 1699999999.0,
           "revisions": [
               {
                   "revision_id": 1,
                   "file_id": "file123",
                   "created_time": 1699999999.0
               }
           ]
       }
   }

get_document_info - 获取文档信息
--------------------------------

获取文档的基本信息和访问规则。

**认证要求**：是

**所需权限**：对文档的读取权限

**请求数据**：同 ``get_document``

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document info retrieved successfully",
       "data": {
           "document_id": "my_doc",
           "parent_id": "root",
           "title": "My Document",
           "size": 2048,
           "created_time": 1699999999.0,
           "last_modified": 1700000000.0,
           "access_rules": [],
           "info_code": 0
       }
   }

**info_code 说明**：

- ``0``: 成功获取所有信息
- ``1``: 无权查看访问规则

delete_document - 删除文档
---------------------------

删除指定文档。

**认证要求**：是

**所需权限**：``delete_document``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 要删除的文档 ID

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document deleted successfully",
       "data": {}
   }

rename_document - 重命名文档
----------------------------

修改文档的标题。

**认证要求**：是

**所需权限**：``rename_document``

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

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document renamed successfully",
       "data": {}
   }

move_document - 移动文档
------------------------

将文档移动到另一个目录。

**认证要求**：是

**所需权限**：``move``

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
     - String
     - 目标目录 ID

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Document moved successfully",
       "data": {}
   }

upload_document - 上传文档内容
------------------------------

为文档创建新版本并上传文件内容。

**认证要求**：是

**所需权限**：对文档的写入权限

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID

**响应**：返回文件上传任务信息（详见文件传输部分）

===================
目录管理 API
===================

create_directory - 创建目录
----------------------------

创建新目录。目录 ID 将自动生成。

**认证要求**：是

**所需权限**：``create_directory`` 或 ``super_create_directory``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - name
     - String
     - 是
     - 目录名称（至少 1 个字符）
   * - parent_id
     - String/null
     - 否
     - 父目录 ID，null 或不提供表示根目录
   * - access_rules
     - Object
     - 否
     - 访问规则配置（可选）

**请求示例**：

.. code-block:: json

   {
       "action": "create_directory",
       "data": {
           "name": "My Folder",
           "parent_id": "parent_folder_id"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Directory created successfully",
       "data": {
           "folder_id": "auto_generated_folder_id_123"
       }
   }

**字段说明**：

- ``folder_id``: 服务器自动生成的目录 ID

**错误响应**：

- ``400``: 缺少必需字段或字段格式错误
- ``403``: 权限不足
- ``404``: 父目录不存在

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
       "message": "List of users",
       "data": {
           "users": [
               {
                   "username": "admin",
                   "nickname": "管理员",
                   "created_time": 1699999999.0,
                   "last_login": 1700000000.0,
                   "permissions": ["shutdown", "create_document", ...],
                   "groups": ["sysop", "user"]
               },
               {
                   "username": "user1",
                   "nickname": "User 1",
                   "created_time": 1700000000.0,
                   "last_login": null,
                   "permissions": ["set_passwd"],
                   "groups": ["user"]
               }
           ]
       }
   }

**字段说明**：

- ``username``: 用户名
- ``nickname``: 用户昵称
- ``created_time``: 账户创建时间（Unix 时间戳）
- ``last_login``: 最后登录时间（Unix 时间戳），null 表示从未登录
- ``permissions``: 用户拥有的所有权限列表
- ``groups``: 用户所属的用户组列表

**错误响应**：

- ``403``: 权限不足

create_user - 创建用户
-----------------------

创建新用户账户。

**认证要求**：是

**所需权限**：``create_user``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 用户名，至少 1 个字符，必须唯一
   * - password
     - String
     - 是
     - 初始密码
   * - nickname
     - String
     - 否
     - 用户昵称
   * - permissions
     - Array
     - 否
     - 用户权限配置数组
   * - groups
     - Array
     - 否
     - 用户组配置数组

**权限配置格式**：

.. code-block:: json

   {
       "permission": "create_document",
       "start_time": 0,
       "end_time": null
   }

- ``permission`` (必需): 权限名称
- ``start_time`` (必需): 生效时间（Unix 时间戳），0 表示立即生效
- ``end_time`` (可选): 过期时间（Unix 时间戳），null 或不提供表示永不过期

**用户组配置格式**：

.. code-block:: json

   {
       "group_name": "editors",
       "start_time": 0,
       "end_time": null
   }

- ``group_name`` (必需): 用户组名称
- ``start_time`` (必需): 生效时间（Unix 时间戳），0 表示立即生效
- ``end_time`` (可选): 过期时间（Unix 时间戳），null 或不提供表示永不过期

**请求示例（基本）**：

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

**请求示例（完整）**：

.. code-block:: json

   {
       "action": "create_user",
       "data": {
           "username": "newuser",
           "password": "secure_password",
           "nickname": "New User",
           "permissions": [
               {
                   "permission": "create_document",
                   "start_time": 0,
                   "end_time": null
               }
           ],
           "groups": [
               {
                   "group_name": "user",
                   "start_time": 0,
                   "end_time": null
               }
           ]
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User created successfully",
       "data": {}
   }

**错误响应**：

- ``400``: 缺少必需字段或字段格式错误
- ``403``: 权限不足
- ``409``: 用户名已存在

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

rename_user - 修改用户昵称
---------------------------

修改用户的显示昵称（nickname）。

**认证要求**：是

**所需权限**：``rename_user``（修改他人）或无需权限（修改自己）

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 要修改的用户名
   * - nickname
     - String/null
     - 是
     - 新昵称，null 表示清除昵称

**请求示例**：

.. code-block:: json

   {
       "action": "rename_user",
       "data": {
           "username": "user1",
           "nickname": "新昵称"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User renamed successfully",
       "data": {}
   }

**错误响应**：

- ``403``: 权限不足
- ``404``: 用户不存在

get_user_info - 获取用户信息
----------------------------

获取用户的详细信息。

**认证要求**：是

**所需权限**：``get_user_info``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 目标用户名

**请求示例**：

.. code-block:: json

   {
       "action": "get_user_info",
       "data": {
           "username": "user1"
       },
       "username": "admin",
       "token": "your_token"
   }

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

**错误响应**：

- ``403``: 权限不足
- ``404``: 用户不存在

change_user_groups - 修改用户组
-------------------------------

修改用户所属的用户组。

**认证要求**：是

**所需权限**：``change_user_groups``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 目标用户名
   * - groups
     - Array
     - 是
     - 用户组名称数组（字符串列表）

**请求示例**：

.. code-block:: json

   {
       "action": "change_user_groups",
       "data": {
           "username": "user1",
           "groups": ["user", "editors"]
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User groups changed successfully",
       "data": {}
   }

**错误响应**：

- ``403``: 权限不足
- ``404``: 用户或用户组不存在

set_passwd - 修改密码
----------------------

修改用户密码。

**认证要求**：是（修改他人时）或否（修改自己且无需认证）

**所需权限**：``set_passwd``（修改自己）或 ``super_set_passwd``（修改他人）

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 要修改密码的用户名
   * - old_passwd
     - String/null
     - 条件
     - 当前密码（修改自己时必需，修改他人时可选）
   * - new_passwd
     - String
     - 是
     - 新密码
   * - force_update_after_login
     - Boolean
     - 否
     - 是否要求用户下次登录时必须修改密码（默认 false）
   * - bypass_passwd_requirements
     - Boolean
     - 否
     - 是否跳过密码复杂度要求（需要 super_set_passwd 权限，默认 false）

**请求示例**：

.. code-block:: json

   {
       "action": "set_passwd",
       "data": {
           "username": "user1",
           "old_passwd": "old_password",
           "new_passwd": "new_secure_password"
       },
       "username": "user1",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Password changed successfully",
       "data": {}
   }

**错误响应**：

- ``400``: 新密码不符合安全要求
- ``401``: 旧密码错误或认证失败
- ``403``: 权限不足
- ``404``: 用户不存在

get_user_avatar - 获取用户头像
------------------------------

获取指定用户的头像文件 ID。

**认证要求**：是

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 目标用户名

**请求示例**：

.. code-block:: json

   {
       "action": "get_user_avatar",
       "data": {
           "username": "user1"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User avatar retrieved successfully",
       "data": {
           "avatar_id": "doc_avatar_123"
       }
   }

**字段说明**：

- ``avatar_id``: 头像文档 ID，可以是 null（未设置头像时）

**错误响应**：

- ``404``: 用户不存在

.. note::

   用户登录成功时，响应中已包含 avatar_id，通常无需单独调用此接口。

set_user_avatar - 设置用户头像
-------------------------------

为用户设置头像。头像必须是系统中已存在的文档。

**认证要求**：是

**所需权限**：``super_set_user_avatar``（设置他人头像）或无需权限（设置自己）

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 目标用户名
   * - document_id
     - String
     - 是
     - 头像文档 ID（必须是有效的文档 ID）

**请求示例**：

.. code-block:: json

   {
       "action": "set_user_avatar",
       "data": {
           "username": "user1",
           "document_id": "avatar_image_001"
       },
       "username": "user1",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User avatar set successfully",
       "data": {}
   }

**错误响应**：

- ``403``: 权限不足
- ``404``: 用户或文档不存在

.. warning::

   头像文档必须是图片文件，且用户必须有读取该文档的权限。

block_user - 封禁用户
----------------------

对用户施加访问封禁。可以封禁用户访问整个系统、特定目录或特定文档。

**认证要求**：是

**所需权限**：``block``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - username
     - String
     - 是
     - 要封禁的用户名
   * - target
     - Object
     - 是
     - 封禁目标配置
   * - block_types
     - Array
     - 是
     - 封禁类型列表（如 ["read", "write"]）
   * - reason
     - String
     - 否
     - 封禁原因
   * - end_time
     - Float/null
     - 否
     - 解封时间（Unix 时间戳），null 表示永久封禁

**封禁目标配置**：

.. code-block:: json

   {
       "type": "all",         // 或 "directory" 或 "document"
       "id": "target_id"      // type 为 "directory" 或 "document" 时必需
   }

**完整请求示例**：

.. code-block:: json

   {
       "action": "block_user",
       "data": {
           "username": "user1",
           "target": {
               "type": "all"
           },
           "block_types": ["read", "write"],
           "reason": "违反使用条款",
           "end_time": 1700000000.0
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User blocked successfully",
       "data": {
           "block_id": "block_abc123"
       }
   }

**字段说明**：

- ``block_id``: 封禁记录 ID，用于后续解封操作

**封禁类型**：

- ``read``: 禁止读取
- ``write``: 禁止写入
- ``delete``: 禁止删除
- ``manage``: 禁止管理（设置权限等）

**目标类型**：

- ``all``: 封禁对整个系统的访问
- ``directory``: 封禁对特定目录的访问
- ``document``: 封禁对特定文档的访问

**错误响应**：

- ``403``: 权限不足
- ``404``: 用户、目录或文档不存在

.. danger::

   封禁整个系统访问 (``type: "all"``) 会阻止用户执行除登录外的所有操作！

unblock_user - 解封用户
------------------------

解除用户的访问封禁。

**认证要求**：是

**所需权限**：``unblock``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - block_id
     - String
     - 是
     - 封禁记录 ID（由 block_user 返回）

**请求示例**：

.. code-block:: json

   {
       "action": "unblock_user",
       "data": {
           "block_id": "block_abc123"
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "User unblocked successfully",
       "data": {}
   }

**错误响应**：

- ``403``: 权限不足
- ``404``: 封禁记录不存在

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
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - status
     - Boolean
     - 是
     - true 启用锁定，false 禁用锁定

**请求示例**：

.. code-block:: json

   {
       "action": "lockdown",
       "data": {
           "status": true
       },
       "username": "admin",
       "token": "your_token"
   }

**响应**：

.. code-block:: json

   {
       "code": 200,
       "message": "Lockdown mode enabled",
       "data": {}
   }

**锁定模式白名单**：

锁定模式下，以下操作对所有用户可用：

- server_info
- register_listener
- login
- refresh_token
- validate_2fa
- upload_file
- download_file

拥有 ``bypass_lockdown`` 权限的用户不受锁定模式限制。

**错误响应**：

- ``401``: 认证失败
- ``403``: 权限不足

.. warning::

   启用锁定模式会限制大部分用户操作，仅应在紧急情况下使用。

view_audit_logs - 查看审计日志
-------------------------------

查看系统审计日志。支持分页和过滤功能。

**认证要求**：是

**所需权限**：``view_audit_logs``

**请求数据**：

.. list-table::
   :header-rows: 1
   :widths: 15 10 10 50

   * - 字段
     - 类型
     - 必需
     - 说明
   * - offset
     - Integer
     - 否
     - 偏移量，用于分页（默认 0，最小 0）
   * - count
     - Integer
     - 否
     - 返回记录数量（默认 50，最小 0，最大 100）
   * - filters
     - Array
     - 否
     - 操作类型过滤器（字符串数组），仅返回指定操作的日志

**请求示例**：

.. code-block:: json

   {
       "action": "view_audit_logs",
       "data": {
           "offset": 0,
           "count": 20,
           "filters": ["login", "logout", "create_user"]
       },
       "username": "admin",
       "token": "your_token"
   }

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
                   "logged_time": 1699999999.0
               },
               {
                   "id": 2,
                   "action": "create_user",
                   "username": "admin",
                   "result": 200,
                   "target": "newuser",
                   "remote_address": "127.0.0.1",
                   "logged_time": 1700000000.0
               }
           ],
           "total": 1000,
           "offset": 0,
           "count": 20
       }
   }

**字段说明**：

- ``logs``: 审计日志条目数组
- ``total``: 符合条件的日志总数
- ``offset``: 当前偏移量
- ``count``: 实际返回的记录数

**日志条目字段**：

- ``id``: 日志记录 ID
- ``action``: 执行的操作名称
- ``username``: 执行操作的用户名（可能为 null）
- ``result``: 操作结果代码（HTTP 状态码）
- ``target``: 操作目标（如用户名、文档 ID 等）
- ``remote_address``: 客户端 IP 地址
- ``logged_time``: 日志记录时间（Unix 时间戳）

**错误响应**：

- ``401``: 认证失败
- ``403``: 权限不足

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
