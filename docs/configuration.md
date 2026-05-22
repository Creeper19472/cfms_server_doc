# 配置文件

基本配置文件（`config.toml`）指定了服务端启动时和运行中所需的一系列核心配置，本节为其各字段提供了进一步说明。

从 [TOML](https://toml.io/) (Tom's Obvious, Minimal Language) 的规范出发，每个设置项都在配置文件中以键值对的形式出现，而多个键值对又以表（Table）的形式组织。表由表头定义，后者独占一行，并由方括号（`[]`）包裹。

每个配置项的值需为 TOML 支持的数据类型。建议参阅 [TOML 规范](https://toml.io/en/v1.1.0) 以了解更多信息。

在本节和本文档的其余部分，出于习惯，我们也可能以“节”来称呼 TOML 中的表。

## 全局配置

以下的配置项不属于任一显式定义的表。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| debug | Boolean | false | 当值为 `true` 时，在控制台打印 SQLAlchemy 的调试日志，并启用服务端内调试目的的请求类型（如 `RequestThrowHandler`）。 |

## 服务器基础 `[server]`

本节的配置指定了与服务端监听相关的基础信息。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| name | String | "CFMS WebSocket Server" | 服务端实例的名称。这个名称将被包含在 `server_info` 的响应中，一些客户端实现会将此名称展示在登录界面上。 |
| host | String | "localhost" | 监听地址。 |
| port | Integer | 5104 | 监听端口。 |
| dualstack_ipv6 | Boolean | true | 启用 IPv6 和 IPv4 双栈支持。**注意：除非您知道自己在做什么，否则不要轻易调整此设置。** |
| secret_key | String | "" | 当用户特异的 `secret_key` 在数据库中未设置时（尽管一般情况下不会发生此事件），作为默认值用于为用户签发 JWT (JSON Web Token)。该键的值将在服务端初始化时自动生成。 |
| ssl_keyfile | Path | "./content/ssl/key.pem" | TLS 私钥文件路径。 |
| ssl_certfile | Path | "./content/ssl/cert.pem" | TLS 证书文件路径。 |
| file_chunk_size | Integer | 2097152 | 下载文件期间使用的数据块大小（单位为字节）。上传文件时的数据块大小是由服务端和客户端协商产生的。 |

## 文档与文件系统 `[document]`

管理文档管理系统的行为和文件系统约束。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| allow_name_duplicate | Boolean | false | 值若为 false，服务端将拒绝导致同一目录下发生重名的文档操作（包括但不限于上传、移动、重命名等）。然而，此项对已经发生的重名现象无效。 |

## 安全策略 `[security]`

定义密码策略和 mTLS（相互 TLS）要求。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| passwd_min_length | Integer | 8 | 用户密码的最少字符数。 |
| passwd_max_length | Integer | 32 | 用户密码的最大字符数。 |
| enable_passwd_force_expiration | Boolean | true | 如果启用，密码必须在 `passwd_expire_after_days` 定义的周期后更改。 |
| require_passwd_enforcement_changes | Boolean | true | 强制具有不符合要求的密码（例如，过短）的用户在登录时立即更改密码。 |
| passwd_expire_after_days | Integer | 365 | 密码被标记为过期前的天数。 |
| passwd_must_contain | Array | [] | _未实现的功能。_ |
| require_client_cert | Boolean | false | 启用 mTLS。如果为 `true`，服务器将根据 CA 验证客户端证书。 |
| client_cert_ca_path | String | "./content/ssl/client/" | 包含用于客户端验证的受信任 CA 证书的目录。 |

## 访问控制 `[access]`

控制访问控制列表 (ACL) 评估的复杂性和严格性。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| enable_access_recursive_check | Boolean | true | 为 true 时，系统会沿目录树向上递归检查，以确保用户具有路径遍历权限。禁用此项可能改善深目录结构的性能，但也需要采取额外的安全措施以确保访问受控。 |

## 数据库配置 `[database]`

配置与数据库连接相关的底层设置。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| type | String | "sqlite" | 数据库引擎类型。可选的值有 `sqlite` 和 `mysql`。 |
| file | String | "app.db" | （仅 SQLite）指定数据库文件的名称。 |
| host | String | "localhost" | （仅 MySQL）指定数据库服务器的主机名。 |
| port | Integer | 3306 | （仅 MySQL）指定数据库服务器的端口。 |
| username | String | "" | （仅 MySQL）指定登录到数据库所用的用户名。 |
| password | String | "" | （仅 MySQL）指定登录到数据库所用的密码。 |
| name | String | "app_db" | （仅 MySQL）指定数据库的名称。 |
| charset | String | "utf8mb4" | （仅 MySQL）指定连接字符集。 |
