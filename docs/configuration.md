# 配置文件

基本配置文件（`config.toml`）指定了服务端启动时和运行中所需的一系列核心配置，本节为其各字段提供进一步说明。

从 [TOML](https://toml.io/) (Tom's Obvious, Minimal Language) 的规范出发，每个设置项都在配置文件中以键值对的形式出现，而多个键值对又以表（Table）的形式组织。表由表头定义，后者独占一行，并由方括号（`[]`）包裹。

每个配置项的值需为 TOML 支持的数据类型。建议参阅 [TOML 规范](https://toml.io/en/v1.1.0) 以了解更多信息。在本节和本文档的其余部分，出于习惯，我们也可能以“节”来称呼 TOML 中的表。

服务端会监视 `config.toml` 的变动，并尝试自动重新加载配置。若新配置无法通过校验，服务端将在日志中记录错误并继续沿用上一次有效的配置。监听地址、TLS、数据库和提供者等在启动时初始化的配置，以及启用的扩展发生变化后，仍需重新启动服务端方可生效。

!!! warning
    `server.secret_key` 和 `security.pepper` 都属于敏感信息。服务端在首次初始化时会为值为空的这两个配置项生成随机值并写回 `config.toml`。之后请勿随意替换它们，也不要将配置文件及其备份提交到代码仓库。

## 全局配置

以下的配置项不属于任一显式定义的表。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| debug | Boolean | false | 当值为 `true` 时，在控制台打印 SQLAlchemy 的调试日志，并启用服务端内调试目的的请求类型（如 `throw_exception`）。 |

## 扩展 `[extensions]`

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| enabled | Array | [] | 按加载顺序列出要启用的扩展标识符。内置扩展 `builtin` 总是最先加载，不应出现在本数组中。修改后需重新启动服务端。 |

扩展标识符应由小写字母、数字和下划线组成，必须以小写字母开头。服务端将在启动时校验已安装扩展的清单、兼容性和标识符；配置了不存在或不兼容的扩展时，启动将失败，而不会静默忽略该扩展。扩展的安装与开发约定请参阅[扩展](extensions.md)。

### 自动暴力破解锁定 `[extensions.brute_force_lockdown]`

本节仅在 `extensions.enabled` 中含有 `brute_force_lockdown` 时生效。该扩展会在一个滚动窗口内汇总针对已有账户的本地密码和 TOTP 验证失败，并在失败总数和目标分散程度同时达到阈值时令服务端进入锁定模式。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| window_seconds | Integer | 600 | 统计验证失败的滚动窗口长度，单位为秒。 |
| failure_threshold | Integer | 50 | 触发锁定所需的失败总数。 |
| distinct_account_threshold | Integer | 10 | 与失败总数共同构成触发条件的不同账户数量。 |
| distinct_ip_threshold | Integer | 10 | 与失败总数共同构成触发条件的不同 IP 地址数量。账户或 IP 数量达到任一阈值即可满足分散程度条件。 |
| reason | String | "Automatic security lockdown: suspected credential-guessing attack detected." | 自动进入锁定模式时公开的理由。 |

自动触发的锁定不会自行解除，且不会覆盖已经存在的手动锁定理由。

## 服务器基础 `[server]`

本节的配置指定了与服务端监听相关的基础信息。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| name | String | "CFMS WebSocket Server" | 服务端实例的名称。这个名称将被包含在 `server_info` 的响应中，一些客户端实现会将此名称展示在登录界面上。 |
| host | String | "localhost" | 监听地址。 |
| port | Integer | 5104 | 监听端口。 |
| dualstack_ipv6 | Boolean | true | 启用 IPv6 和 IPv4 双栈支持。**注意：除非您知道自己在做什么，否则不要轻易调整此设置。** |
| secret_key | String | "" | 用于签发部分用户令牌、加密分页游标及派生速率限制器内部标识的服务端密钥。首次初始化时自动生成。 |
| ssl_keyfile | Path | "./content/ssl/key.pem" | TLS 私钥文件路径。 |
| ssl_certfile | Path | "./content/ssl/cert.pem" | TLS 证书文件路径。 |
| trusted_proxy_networks | Array | ["127.0.0.1/32", "::1/128"] | 允许通过 `X-Forwarded-For` 或 `X-Real-IP` 提供客户端地址的反向代理网段，以 CIDR 表示。 |
| file_chunk_size | Integer | 2097152 | 服务端允许协商的文件分块大小上限，单位为字节。实际分块大小还受客户端声明值和传输方向硬限制的约束。 |

!!! warning "谨慎配置信任的反向代理"
    服务端会以解析得到的客户端 IP 地址执行连接准入、速率控制和安全封禁。请仅将会清理并重新填写转发标头的反向代理加入 `trusted_proxy_networks`，否则客户端可能伪造来源地址。

### 准入控制 `[server.admission_control]`

本节所规定的限制均在单个服务端进程内强制执行，即使请求速率控制处于观察或禁用模式也不例外。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| max_connections | Integer | 64 | 同一进程允许同时存在的 WebSocket 连接总数。 |
| max_connections_per_ip | Integer | 16 | 同一来源 IP 地址允许同时存在的连接数。不得大于 `max_connections`。 |
| max_inflight_requests | Integer | 64 | 同一进程允许同时处理的逻辑请求总数。 |
| max_inflight_requests_per_connection | Integer | 8 | 单条连接允许同时处理的逻辑请求数。不得大于 `max_inflight_requests`。 |
| max_pending_streams_per_connection | Integer | 16 | 单条连接允许等待处理的逻辑流数量。 |
| busy_retry_after_seconds | Integer | 1 | 因服务端容量不足而拒绝请求时，建议客户端等待的秒数。 |

## 安全策略 `[security]`

定义密码策略和 mTLS（相互 TLS）要求。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| pepper | String | "" | 在 Argon2id 处理前附加到密码及二步验证备用代码的服务端机密值。首次初始化时自动生成。 |
| passwd_min_length | Integer | 8 | 用户密码的最少字符数。 |
| passwd_max_length | Integer | 32 | 用户密码的最大字符数。 |
| enable_passwd_force_expiration | Boolean | true | 如果启用，密码必须在 `passwd_expire_after_days` 定义的周期后更改。 |
| require_passwd_enforcement_changes | Boolean | true | 强制具有不符合要求的密码（例如，过短）的用户在登录时立即更改密码。 |
| passwd_expire_after_days | Integer | 365 | 密码被标记为过期前的天数。 |
| passwd_rules | Array | [`'[A-Z]'`, `'[a-z]'`, `'[0-9]'`, `'[!@#$%^&*()]'`] | 密码需符合的规则，以正则表达式表示，视数组中的每个字符串为一条。 |
| passwd_min_passed_count | Integer | 2 | 密码需满足的规则的最小条数，应为非负整数。 |
| require_client_cert | Boolean | false | 启用 mTLS。如果为 `true`，服务端将根据指定的 CA 目录验证客户端证书。 |
| client_cert_ca_path | Path | "./content/ssl/client/" | 用于客户端证书验证的受信任 CA 目录。目录中的证书需遵循 OpenSSL 的哈希命名约定。 |

!!! note "注意 `passwd_min_passed_count` 具有的隐式行为"
    在内部实现中，`passwd_min_passed_count` 的值实际被隐式地设置为 $\min(\text{passwd_min_passed_count}, \text{len}(\text{passwd_rules}))$，以确保规则检查总能在密码满足所有规则要求时通过。

### 身份验证节流 `[security.auth_throttle]`

本节用于减缓针对密码和 TOTP 的反复猜测。账户、账户与 IP 的组合以及 IP 地址分别维护失败状态；命中任一有效锁定都将阻止相应的验证尝试。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| enabled | Boolean | true | 是否启用身份验证节流。 |
| account_failure_threshold | Integer | 5 | 单个账户触发递增延迟前允许的失败次数。 |
| account_base_delay_seconds | Integer | 30 | 账户首次触发锁定时的基础延迟，单位为秒。 |
| account_max_delay_seconds | Integer | 3600 | 账户递增延迟的上限，单位为秒。 |
| account_reset_seconds | Integer | 86400 | 账户失败状态的重置周期，单位为秒。 |
| account_ip_failure_threshold | Integer | 5 | 同一账户与 IP 组合在窗口内触发锁定所需的失败次数。 |
| account_ip_window_seconds | Integer | 900 | 账户与 IP 组合的统计窗口，单位为秒。 |
| account_ip_block_seconds | Integer | 900 | 账户与 IP 组合的锁定时长，单位为秒。 |
| ip_failure_threshold | Integer | 60 | 同一 IP 在窗口内触发锁定所需的失败次数。 |
| ip_window_seconds | Integer | 600 | IP 失败统计窗口，单位为秒。 |
| ip_block_seconds | Integer | 900 | IP 锁定时长，单位为秒。 |
| record_retention_days | Integer | 7 | 已失效验证失败记录的保留天数。 |

持有相应管理权限的管理员可以查看或精确解除仍在生效的身份验证锁定。

### 请求速率控制 `[security.request_rate_control]` {#request-rate-control}

本节的令牌桶限制独立于始终生效的准入控制。更完整的工作方式、客户端响应和分布式部署注意事项请参阅[请求速率控制](features/rate-limiting.md)。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| mode | String | "observe" | `disabled` 不执行令牌计量；`observe` 记录本应拒绝的请求但仍予放行；`enforce` 实际拒绝超限请求。 |
| connection_capacity | Integer | 20 | 单个 IP 的连接尝试令牌桶容量。 |
| connection_refill_tokens | Integer | 60 | 每个连接补充周期增加的令牌数。 |
| connection_refill_period_seconds | Integer | 60 | 连接令牌的补充周期，单位为秒。 |
| request_refill_period_seconds | Integer | 60 | 请求令牌的补充周期，单位为秒。 |
| account_capacity | Integer | 120 | 单个已认证账户的请求令牌桶容量。 |
| account_refill_tokens | Integer | 120 | 每周期向账户令牌桶补充的令牌数。 |
| ip_capacity | Integer | 600 | 单个 IP 的请求令牌桶容量。 |
| ip_refill_tokens | Integer | 600 | 每周期向 IP 令牌桶补充的令牌数。 |
| state_retention_seconds | Integer | 600 | 不活跃令牌桶状态的保留时间。其值必须覆盖上述所有补充周期。 |

可在 `[security.request_rate_control.action_costs]` 下以请求名称为键、正整数为值，覆盖各请求处理器声明的默认成本。例如：

```toml
[security.request_rate_control.action_costs]
search = 4
upload_document = 8
```

未列出的请求沿用服务端内置成本。未知的请求名称会在启动时产生警告，配置的成本不得大于账户或 IP 令牌桶容量。

## OpenID Connect 单点登录 `[sso.oidc]` {#openid-connect-sso}

本节仅在安装 `ext_oidc_sso` 可选依赖并于 `extensions.enabled` 中启用 `oidc_sso` 扩展后生效。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| issuer | String | "" | OpenID Provider 的 Issuer URL，末尾不应带有 `/`。 |
| client_id | String | "" | 在 OpenID Provider 注册的客户端标识符。 |
| client_secret | String | "" | 在 OpenID Provider 注册的客户端机密。 |
| redirect_uri | String | "" | 已注册且由客户端使用的回调 URI。客户端请求不能覆盖此值。 |
| username_claim | String | "preferred_username" | 用于映射 CFMS 用户名的身份声明字段。 |
| auto_provision | Boolean | false | 当映射后的本地用户不存在时，是否自动创建用户。 |
| default_groups | Array | ["user"] | 自动创建的用户将被加入的用户组。 |

## 访问控制 `[access]`

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| enable_access_recursive_check | Boolean | true | 为 `true` 时，系统会沿目录树向上递归检查启用了继承的父目录。禁用此项可能改善深目录结构的性能，但也需要在每个对象上妥善设置访问规则。 |

## 文档上传 `[document.upload]`

本节控制上传任务的生命周期，以及未完成的新文档对名称空间的占用。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| start_timeout_seconds | Integer | 3600 | 创建上传任务后允许开始传输的时间。必须小于 `max_duration_seconds`。 |
| max_duration_seconds | Integer | 86400 | 上传开始后的硬性最长持续时间。 |
| idle_timeout_seconds | Integer | 300 | 上传期间未收到数据帧时的超时时间，不得大于 `max_duration_seconds`。 |
| cleanup_interval_seconds | Integer | 60 | 对无关的过期上传执行机会式清理时，两批清理之间的最短间隔。 |
| max_pending_documents_per_creator | Integer | 16 | 同一创建者可以保留的空白、尚未开始上传的文档数。此硬限制不受观察模式影响。 |

### 文档创建风险控制 `[document.upload.creation_risk_control]`

该策略根据账户的新旧程度、尚未完成的文档比例、同一 IP 涉及的账户数和近期拒绝次数，将文档创建请求判定为普通、较高或高风险，并以相应成本消耗账户和 IP 的持久化令牌桶。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| mode | String | "enforce" | `observe` 仅记录决策，`enforce` 实际拒绝超限创建。 |
| refill_period_seconds | Integer | 600 | 账户与 IP 令牌桶的补充周期。 |
| account_capacity / account_refill_tokens | Integer | 60 / 300 | 账户令牌桶的容量和每周期补充量。 |
| ip_capacity / ip_refill_tokens | Integer | 200 / 1000 | IP 令牌桶的容量和每周期补充量。 |
| new_account_seconds | Integer | 604800 | 在此时间范围内创建的账户被视为新账户。 |
| pending_elevated_ratio / pending_high_ratio | Float | 0.5 / 0.75 | 未完成文档比例对应的较高和高风险阈值。前者必须小于后者。 |
| ip_account_window_seconds | Integer | 600 | 汇总同一 IP 所涉及账户的窗口。 |
| ip_accounts_elevated / ip_accounts_high | Integer | 4 / 10 | 同一 IP 所涉及账户数对应的较高和高风险阈值。 |
| denial_window_seconds | Integer | 600 | 汇总近期拒绝记录的窗口。 |
| denials_elevated / denials_high | Integer | 1 / 3 | 近期拒绝次数对应的较高和高风险阈值。 |
| elevated_cost / high_cost | Integer | 3 / 10 | 较高和高风险请求消耗的令牌数；普通请求消耗 1 枚令牌。 |
| state_retention_seconds | Integer | 86400 | 不活跃风险状态的保留时间，必须覆盖策略使用的全部窗口。 |

### 文档下载风险控制 `[document.download.risk_control]`

文档下载在签发下载任务和开始或恢复传输两个阶段分别计量。每一阶段都会同时消耗账户和 IP 令牌；每次开始或恢复传输还会消耗该下载任务自身的令牌。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| mode | String | "observe" | `observe` 仅记录决策，`enforce` 实际拒绝超限下载。 |
| refill_period_seconds | Integer | 600 | 账户与 IP 令牌桶的补充周期。 |
| issue_account_capacity / issue_account_refill_tokens | Integer | 60 / 300 | 签发任务时使用的账户令牌桶容量和补充量。 |
| issue_ip_capacity / issue_ip_refill_tokens | Integer | 200 / 1000 | 签发任务时使用的 IP 令牌桶容量和补充量。 |
| transfer_account_capacity / transfer_account_refill_tokens | Integer | 60 / 300 | 开始传输时使用的账户令牌桶容量和补充量。 |
| transfer_ip_capacity / transfer_ip_refill_tokens | Integer | 200 / 1000 | 开始传输时使用的 IP 令牌桶容量和补充量。 |
| task_capacity / task_refill_tokens | Integer | 5 / 10 | 单个下载任务令牌桶的容量和每周期补充量。 |
| task_refill_period_seconds | Integer | 3600 | 下载任务令牌的补充周期。 |
| new_account_seconds | Integer | 604800 | 在此时间范围内创建的账户被视为新账户。 |
| ip_account_window_seconds | Integer | 600 | 汇总同一 IP 所涉及账户的窗口。 |
| ip_accounts_elevated / ip_accounts_high | Integer | 4 / 10 | 同一 IP 所涉及账户数对应的较高和高风险阈值。 |
| denial_window_seconds | Integer | 600 | 汇总近期拒绝记录的窗口。 |
| denials_elevated / denials_high | Integer | 1 / 3 | 近期拒绝次数对应的较高和高风险阈值。 |
| elevated_cost / high_cost | Integer | 3 / 10 | 较高和高风险操作消耗的令牌数。 |
| state_retention_seconds | Integer | 86400 | 不活跃风险状态的保留时间，必须覆盖策略使用的全部窗口。 |

建议先在 `observe` 模式下覆盖一次具有代表性的业务高峰，依据日志调整阈值后再启用强制限制。切换模式不会清空已经累积的令牌桶状态。持有对应旁路权限的用户可以跳过文档创建或下载的风险令牌，但无法绕过准入控制。

## 数据库配置 `[database]`

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
| options | String | "" | 保留字段，当前尚未实现。 |

## 提供者（Providers） `[provider]`

配置存储、缓存、事件系统和请求速率状态的提供者类型。提供者在服务端启动时初始化，修改本节后需要重新启动服务端。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| caching | String | "memory" | 缓存提供者类型。可选值为 `memory` 和 `redis`。 |
| storage | String | "local" | 存储提供者类型。可选值为 `local` 和 `s3`。 |
| event_bus | String | "local" | 事件系统提供者类型。可选值为 `local` 和 `redis`。 |
| rate_limit | String | "memory" | 请求速率状态提供者类型。可选值为 `memory` 和 `redis`。多进程或多主机部署应使用 Redis 以共享限制状态。 |

## Redis `[redis]`

当启用了与 Redis 相关的提供者时，本节配置其连接设置。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| host | String | "localhost" | Redis 服务器的主机名。 |
| port | Integer | 6379 | Redis 服务器的端口。 |
| password | String | "" | 连接到 Redis 使用的密码。 |
| db | Integer | 0 | Redis 数据库索引。注意集群化模式下的 Redis 可能仅支持 `db0`。 |

## Simple Storage Service (S3) `[s3]`

当指定 S3 作为存储提供者时，本节配置其连接设置。服务端理论上兼容任意支持 S3 协议的对象存储服务，而不要求必须使用由 Amazon 提供的对象存储。

| 键 | 类型 | 默认值 | 说明 |
|---|---:|---|---|
| bucket | String | "" | 存储桶名称。**注意：服务端不会在目标存储桶不存在时尝试自动创建它。** |
| endpoint_url | String | "" | 自定义的 Endpoint 地址，供连接到非 Amazon 的 S3 服务器时使用。 |
| access_key_id | String | "" | 访问存储桶所需的 Access Key ID (AK)。 |
| secret_access_key | String | "" | 访问存储桶所需的 Secret Access Key (SK)。 |
| region_name | String | "" | 存储桶的地域。若不指定，将使用服务端内置的默认值 `us-east-1`。 |

!!! note
    服务端被硬编码为在访问 S3 存储桶时使用**虚拟主机风格**（Virtual-Hosted Style），这是 AWS S3 的默认和推荐方式。路径风格（Path-Style）不受支持。

## 已废弃的配置项

旧版本中的 `document.allow_name_duplicate` 已被废弃且会被服务端忽略。当前版本始终要求同一目录内处于活动状态的文档和目录共用一个名称空间，且名称不得重复；被标记为删除的项目会释放其名称。
