API 接口参考
====================================

本章节详细列出了 CFMS 服务端支持的所有 API 接口。所有接口通过 WebSocket 连接以 JSON 格式进行通信。

.. contents:: 目录
   :local:
   :depth: 2

接口概览
--------

CFMS API 按功能分为以下几类，共计约 40 个接口：

.. list-table:: API 分类
   :header-rows: 1
   :widths: 20 15 50

   * - 类别
     - 接口数量
     - 说明
   * - 服务器与认证
     - 3
     - 服务器信息、用户登录、令牌刷新
   * - 文档管理
     - 8
     - 文档的增删改查和权限管理
   * - 目录管理
     - 8
     - 目录的增删改查和权限管理
   * - 用户管理
     - 9
     - 用户账户的创建、删除、修改和查询
   * - 用户组管理
     - 6
     - 用户组的创建、删除和权限配置
   * - 访问控制
     - 2
     - 授予访问权限和查看访问记录
   * - 系统管理
     - 2
     - 锁定模式和审计日志

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
       "message": "registered as a listener",
       "data": {}
   }

.. note::

   监听连接不应主动发送其他请求，仅用于接收服务器推送的消息。

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

在指定目录下创建新文档。

**认证要求**：是

**所需权限**：``create_document`` 或 ``super_create_document``

**请求数据**：

.. list-table::
   :header-rows: 1

   * - 字段
     - 类型
     - 说明
   * - document_id
     - String
     - 文档 ID（唯一标识符）
   * - title
     - String
     - 文档标题
   * - folder_id
     - String
     - 所属目录 ID，"root" 表示根目录

**请求示例**：

.. code-block:: json

   {
       "action": "create_document",
       "data": {
           "document_id": "my_doc",
           "title": "My Document",
           "folder_id": "root"
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
           "document_id": "my_doc"
       }
   }

**错误响应**：

- ``400``: 缺少必需字段或字段格式错误
- ``403``: 权限不足
- ``409``: 文档 ID 已存在

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
