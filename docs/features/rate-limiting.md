# 请求速率控制

尽管 CFMS 是为内部档案管理而设计的，但仍需面对连接洪泛、逻辑流滥用、耗时请求过多和持续高频调用等不同形式的资源压力。服务端因此在多个边界分别实施硬性准入限制和令牌桶速率控制。

## 控制层次

| 边界 | 作用域 | 拒绝方式 | 目的 |
|---|---|---|---|
| HTTP WebSocket 升级 | 来源 IP | HTTP `429`，含 `Retry-After` | 限制反复建立连接的尝试。 |
| 已建立的 WebSocket | 进程及来源 IP | 关闭代码 `1013` | 限制同时存在的连接资源。 |
| 等待处理的逻辑流 | 单条连接 | 关闭代码 `1013` | 阻止在一条连接上无界创建逻辑流。 |
| 正在处理的逻辑请求 | 进程及单条连接 | 请求结论 `503` | 限制请求工作线程数量。 |
| 已知请求类型 | 来源 IP 及已认证账户 | 请求结论 `429` | 按请求成本实施持续使用配额。 |

`429` 表示客户端已达到配额；`503` 和关闭代码 `1013` 则表示服务端暂时承受容量压力。客户端应优先等待响应中的 `retry_after_seconds` 或 HTTP `Retry-After` 所指定的时间；没有明确时间时，应使用带随机抖动且具有上限的指数退避。

硬性准入限制由 `[server.admission_control]` 配置，并且始终在单个进程内生效。请求令牌桶由 `[security.request_rate_control]` 配置，可以处于 `disabled`、`observe` 或 `enforce` 模式。各配置项的完整默认值请参阅[配置文件](../configuration.md#request-rate-control)。

## 令牌桶与请求成本

连接尝试按来源 IP 消耗独立的连接令牌。通过身份验证的已知请求会同时消耗账户和 IP 请求令牌；未认证请求只消耗 IP 令牌。未知请求会在计量前被拒绝，而无效的认证凭据也不会在身份得到信任前消耗账户令牌。

每个请求处理器声明一个正整数成本。内置请求使用六个相对成本层级：

| 成本 | 请求类型 |
|---:|---|
| 1 | `cancel_2fa_setup`、`get_2fa_status`、`get_user_key`、`server_info`、`shutdown` |
| 2 | `refresh_token`、`validate_2fa`、`list_banned_subnets`、`get_document_access_rules`、`list_revisions`、`get_directory_access_rules`、`unblock_user`、`get_user_info`、`revoke_access`、`upload_user_key`、`delete_user_key`、`set_user_preference_dek`、`list_user_keys` |
| 3 | `list_auth_lockouts`、`get_document`、`restore_document`、`rename_document`、`move_document`、`get_document_info`、`set_document_tags`、`get_revision`、`set_current_revision`、`list_directory`、`get_directory_info`、`create_directory`、`rename_directory`、`move_directory`、`list_deleted_items`、`search`、`manage_user_status`、`block_user`、`list_user_blocks`、`list_users`、`get_user_avatar`、`set_user_avatar`、`change_user_groups`、`change_user_permissions`、`list_groups`、`create_group`、`get_group_info`、`change_group_permissions`、`grant_access`、`view_access_entries`、`view_audit_logs`、`sso_oidc_start`、`throw_exception` |
| 5 | `login`、`disable_2fa`、`create_banned_subnet`、`update_banned_subnet`、`delete_banned_subnet`、`create_document`、`upload_document`、`delete_document`、`set_document_rules`、`delete_revision`、`download_file`、`upload_file`、`set_directory_rules`、`create_user`、`delete_user`、`rename_user`、`delete_group`、`rename_group` |
| 10 | `unlock_auth_lockouts`、`purge_document`、`delete_directory`、`restore_directory`、`set_passwd`、`lockdown`、`sso_oidc_callback` |
| 20 | `setup_2fa`、`purge_directory` |

以默认每分钟向账户桶补充 120 枚令牌为例，成本为 1、2、3、5、10 和 20 的请求，其大致持续调用上限分别为每分钟 120、60、40、24、12 和 6 次。IP 桶的默认补充量是账户桶的五倍。这些数值只表达相对压力，不代表请求实际耗时，也不能替代针对列表大小、目录子树规模和文件大小的专门限制。

可以在 `[security.request_rate_control.action_costs]` 中覆盖请求的成本。服务端在启动时会检查内置处理器和扩展处理器；配置中出现未知请求名称时会记录警告，成本超过账户或 IP 桶容量时则会拒绝该配置。

## 观察、强制与旁路

`observe` 模式仍会维护令牌桶并在日志中记录本应阻止的决定，但不会仅因为请求令牌不足而拒绝请求。建议新策略首先以该模式运行至少一个有代表性的业务高峰，再依据日志调整容量、补充速率和高成本请求的权重。

切换到 `enforce` 后，超限请求返回 `429`，并在 `data` 中包含 `scope`、`limit` 和 `retry_after_seconds`。降低桶容量不会直接删除已有状态，后续决定会将已存令牌钳制到新的容量。

持有 `bypass_request_rate_limit` 权限的用户可以跳过账户和 IP 请求令牌桶，但仍无法绕过连接尝试限制及任何硬性准入上限。文档创建和下载另有各自的自适应风险令牌及独立的旁路权限，不会被折算到本页所述的通用请求成本中。

## 单机与集群

`provider.rate_limit = "memory"` 使用线程安全且有界的进程内状态，适合单进程部署。若启动多个进程或将服务端部署到多台主机，每个进程的内存桶会分别计量，实际可用配额将随实例数增加，而且客户端可能在实例间切换。

需要共享配额时，应安装 `cluster` 可选依赖并设置 `provider.rate_limit = "redis"`。Redis 提供者以一段 Lua 操作原子地完成读取、判断和更新，并使用 Redis 服务端时间及过期机制管理不活跃状态。

若共享的请求速率提供者发生故障，令牌桶限制会采取故障开放策略，以避免 Redis 故障使整个服务不可用；进程内的连接、逻辑流和并发请求上限仍会继续生效。提供者类型的变化需要重新启动服务端。

令牌桶中的账户和 IP 标识是以 `server.secret_key` 为密钥生成的 HMAC-SHA256 摘要，不会直接把用户名和原始 IP 放入提供者键中。替换该密钥会使已有令牌桶状态失效。由于解析出的客户端 IP 同时参与准入、速率控制和安全封禁，`server.trusted_proxy_networks` 必须只包含可信且会清理转发标头的反向代理。

## 建议的启用流程

1. 先保持 `mode = "observe"`，收集至少一个代表性高峰期间的 `request_rate_control` 日志。
2. 依据数据库、文件存储和 CPU 容量调整硬性准入上限、桶容量、补充速率及请求成本。
3. 集群部署应先启用并验证 Redis 提供者，再切换至 `mode = "enforce"`。
4. 仅向受严格控制的服务账户或应急账户授予旁路权限。
5. 需要立即停止强制拒绝时，将模式改回 `observe` 或 `disabled`；硬性准入上限会按设计继续生效。
