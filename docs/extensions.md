# 扩展

服务端通过 [Pluggy](https://pluggy.readthedocs.io/) 扩展功能。每个扩展位于 `src/include/extensions/` 下的独立目录中，并且至少包含 `_extension.py` 入口和 `manifest.toml` 清单。服务端可以在不导入扩展 Python 代码的情况下先读取清单、验证元数据并判断兼容性。

!!! warning
    扩展代码运行在服务端进程内，能够访问数据库、配置、存储提供者和敏感数据。只应安装来源可信且已经过审查的扩展。

## 清单格式

当前只支持第 2 版清单。元数据和服务端兼容性分别位于不同的 TOML 表中：

```toml
manifest_version = 2

[extension]
identifier = "example_extension"
name = "Example Extension"
version = "1.0.0"
authors = ["Example Author"]
license = "Apache-2.0"
description = "An optional short description."
homepage = "https://example.com/extensions/example"

[compatibility]
minimum_server_version = "0.4.1.260811_alpha"
```

`manifest_version` 和 `[extension]` 是必需的。`[extension]` 内必须提供 `identifier`、`name`、`version`、`authors` 和 `license`；`description` 与 `homepage` 可省略。`[compatibility]` 及其 `minimum_server_version` 均可省略，此时表示不声明最低服务端版本。未知的表和字段会被拒绝。

扩展自身的版本建议使用语义化版本，许可证建议使用 SPDX 标识符。最低服务端版本使用 `server_info.version` 返回的 CFMS 核心版本格式：

```text
MAJOR.MINOR.PATCH[.BUILD][_TYPE[NUMBER]]
```

发行类型可以是 `alpha`、`beta`、`rc` 或 `release`，并按这一顺序从早到晚比较；省略类型等价于 `release`。版本值只包含版本本身，不应带有比较运算符。

第 1 版扁平清单已经不受支持。旧扩展需将描述字段移入 `[extension]`，设置 `manifest_version = 2`，并在需要时加入 `[compatibility]`。

## 扩展标识符

`identifier` 是配置和 Pluggy 注册使用的稳定键，必须符合 `^[a-z][a-z0-9_]*$`，长度不得超过 255 个字符，不能是为服务端核心保留的 `core`，并且在已安装扩展目录中必须唯一。服务端按原值严格验证标识符，不会删除空白或执行其他规范化。

扩展目录名和展示名称发生变化时，标识符仍应保持不变，否则已有配置和扩展持久状态将无法继续以原所有者访问。

## 启用扩展

可选扩展按配置数组中的顺序加载：

```toml
[extensions]
enabled = ["example_extension"]
```

`builtin` 扩展提供服务端的内置行为，总是最先加载，因此不得写入 `enabled`。修改启用列表后需要重新启动服务端。

启动时，服务端会验证安装目录内的每一份扩展清单，但只导入 `builtin` 和明确启用的标识符。已安装但未启用的扩展可以要求更高的服务端版本而不阻止启动，不过其清单本身仍须有效。

服务端会在导入任何可选扩展代码之前检查本次选中的完整扩展集合。若当前核心版本低于任一扩展声明的最低版本，启动将失败并报告扩展标识符、所需版本和当前版本，且不会导入这组选中的扩展。扩展目录无效、标识符重复、启用了未安装扩展或导入失败时同样会中止启动，避免服务端在缺失预期能力的情况下静默运行。

## 配置与生命周期钩子

扩展可以实现 `ext_validate_config(config)` 校验自己的配置。该钩子在扩展加载和全局配置重新加载时运行；无效配置应抛出 `ConfigValidationError`，重新加载失败时服务端会继续使用上一次有效配置。

拥有后台服务的扩展可以实现 `ext_on_startup()` 和 `ext_on_shutdown()`。启动钩子在数据库、提供者和请求处理器就绪后执行；关闭钩子会在服务循环退出时执行，也会覆盖启动失败后的清理路径，因此实现应当可以安全重复调用。需要访问 WebSocket 服务端实例时，启动钩子可以接收已绑定的 `server` 参数。

非空文件上传还会依次触发三个扩展点：

1. `ext_before_file_upload_finalize(session, id, path, sha256)` 在上传完成事务内执行。扩展可以使用调用方提供的数据库会话追加工作，但不能自行提交、回滚或关闭会话。
2. `ext_on_file_uploaded(id, path, sha256)` 在该事务提交后、成功响应发送前执行。
3. `ext_on_file_upload_completed(id, path, sha256)` 在成功响应已经发送后执行，不能再尝试改变客户端已经得到的结果。

内置扩展通过这些钩子和生命周期钩子实现持久化的后台文件去重；核心上传处理只负责发布生命周期事件。

## 持久运行状态

核心功能和受信任扩展可以通过 `include.database.system_states` 持久保存体积小、写入频率低的运行状态。扩展应以清单标识符作为 `owner`；`core` 保留给服务端自身。状态键使用小写标识符，并可包含点号、连字符和下划线。

状态 API 接受由调用方管理的 SQLAlchemy 会话，不会自行提交、回滚或关闭。创建操作只在键不存在时插入，更新和删除则要求提供读取时得到的修订号；比较失败表明有其他事务已经修改状态，调用方应重新读取后再决定是否重试。

负载的模式版本由所有者管理。扩展应显式迁移自己支持的旧版本，且不能覆盖无法识别的更新版本。禁用或移除扩展不会删除其状态行。

!!! note "运行状态的用途边界"
    扩展运行状态不应存放机密、配置、业务记录、高频计数器、大型负载、任务队列，或需要字段索引、外键和数据库级字段约束的数据；这些场景应使用专门的数据模型和迁移。运行状态也不会包含在逻辑备份中，必须能够安全地重新构建。

## 内置的可选扩展

### OpenID Connect 单点登录

安装相应依赖并启用扩展：

```bash
uv sync --extra ext_oidc_sso
```

```toml
[extensions]
enabled = ["oidc_sso"]
```

具体配置项和安全语义请参阅[配置文件](configuration.md#openid-connect-sso)与[身份验证及安全管理](features/security-controls.md#openid-connect)。

### 自动暴力破解锁定

`brute_force_lockdown` 不需要额外的可选依赖。将其标识符加入 `extensions.enabled` 后，即可使用 `[extensions.brute_force_lockdown]` 调整检测窗口、失败次数、不同账户和 IP 阈值及公开理由。触发后的锁定不会自动过期，需由管理员明确解除。
