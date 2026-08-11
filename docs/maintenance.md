# 部署与维护

随服务端安装的 `maintain` 命令用于执行不适合通过常规 WebSocket 请求完成的本地维护操作。所有维护命令都必须以 `src/` 为工作目录，且该目录内必须存在 `main.py` 和 `config.toml`。

```bash
cd cfms_on_websocket/src
uv run maintain --help
```

对于会写入数据库、配置或存储的操作，建议先停止服务端并完成可恢复的备份，以免维护命令与正在处理的请求并发修改同一状态。

## 账户恢复

在管理员无法通过客户端恢复账户时，可以直接重置指定用户的密码：

```bash
uv run maintain user reset-password admin
```

省略 `--password` 时，命令会生成安全的随机密码并将其显示给操作者；也可以显式提供新密码：

```bash
uv run maintain user reset-password alice --password 'NewPass123!'
```

无论密码由命令生成还是由操作者指定，该用户下一次登录时都会被要求再次修改密码。

可以清除单个用户的 TOTP 共享密钥、备用代码和设置中状态：

```bash
uv run maintain user clear-totp alice
```

清除全部用户的 TOTP 状态属于高风险操作，需要交互确认；无人值守环境可以显式传入 `--yes`：

```bash
uv run maintain user clear-totp --all --yes
```

## 配置维护

### 补充 pepper

从没有 `security.pepper` 的旧版本升级时，可以在其值缺失或为空的情况下生成并写入随机 pepper：

```bash
uv run maintain config fill-pepper
```

已经存在非空 pepper 时，命令不会替换它。

### 同步配置范本 {#sync-config-template}

服务端升级后，可以将新版本 `config.toml.sample` 的布局、注释和新增字段合并到现有配置，同时保留仍然有效的当前值：

```bash
uv run maintain config sync-template
```

该命令能够迁移若干已知旧字段，包括旧数据库名称、OIDC 启用开关、文档创建固定窗口限制和旧密码规则，并移除已经失效的 `document.allow_name_duplicate`。对于范本之外、可能由本地或扩展拥有的配置，交互流程会逐项询问，不会一律视为过时。

建议先以只读模式检查差异：

```bash
uv run maintain config sync-template --check
```

无人值守执行时，`--yes` 会应用已知变更并保留未知字段；可以重复使用 `--remove` 删除明确指定的路径，或以 `--prune` 删除全部范本外字段：

```bash
uv run maintain config sync-template --yes --remove server.old_setting
```

写入前，命令会校验合并后的完整配置，在当前文件旁创建带时间戳的 `config.toml.backup-*` 备份，并以原子替换方式更新 `config.toml`。这些备份包含旧的凭据和机密，应与正式配置文件采用相同的保护措施。

## 加密备份

### 导出

常规导出会生成包含全部可备份组件的逻辑备份，并使用随机 256 位密钥和 AES-256-GCM 加密压缩后的负载：

```bash
uv run maintain backup export backup.confbak --key-out backup.key
```

若未提供 `--key-out`，密钥会显示在终端中。也可以使用交互向导选择组件、输出位置和密钥保存方式：

```bash
uv run maintain backup export --interactive
```

可选组件包括：

| 组件 | 内容 |
|---|---|
| `accounts` | 用户、用户组、权限、密钥环和用户封禁规则。 |
| `documents` | 目录、文档、修订版本、元数据、物理文件和对象访问控制。选择后会自动包含账户组件。 |
| `audit` | 审计日志。选择后会自动包含账户组件。 |
| `banned_subnets` | IP 网段封禁规则及其理由。 |
| `configuration` | 恢复账户凭据所必需的 `security.pepper` 和 `server.secret_key`，并非整个配置文件。 |

文件任务、身份验证节流状态、请求与文档风险令牌桶以及扩展运行状态等临时或可重建表不会包含在逻辑备份中。

!!! danger "备份密钥必须单独保管"
    没有备份密钥便无法恢复备份。不要只把 `backup.confbak` 和 `backup.key` 存放在同一个位置，也不要将密钥提交到代码仓库。备份包含配置机密、账户记录和可能为明文的业务文件，即使已经加密，也应限制访问并定期验证可恢复性。

### 查看头信息

备份的头信息不加密，可以在不提供密钥的情况下查看格式版本、创建时间、服务端核心版本、压缩和加密算法：

```bash
uv run maintain backup info backup.confbak
```

头信息不包含数据库记录和文件内容，但仍可能暴露部署版本与备份时间。

### 导入

导入要求目标数据库中所有受管理表均为空，并会拒绝覆盖存储提供者中已经存在的目标文件。目标 `src/` 目录仍须先准备有效的 `config.toml`，以便初始化数据库和存储提供者；若备份包含配置组件，导入会将其中的 pepper 和 secret key 写入该配置文件。

```bash
uv run maintain backup import backup.confbak --key-file backup.key
```

也可以通过 `--key` 直接提供密钥。导入属于高风险操作，默认会要求确认；经过自动化流程明确校验目标后，可以使用 `--yes` 跳过交互确认。恢复成功时，命令会写入 `src/init` 初始化标记。

应定期在隔离环境中演练恢复。恢复环境需要能够连接与备份目标相匹配的数据库和存储提供者，并应使用与备份核心版本兼容的服务端代码。

## 安装发布包

发行版本提供 ZIP 和 tar.gz 源码部署包，以及 `SHA256SUMS.txt`。部署主机需预先安装 Python 3.14 或更高版本与 `uv`。下载后应先验证摘要，再解压适合当前系统的格式：

```bash
sha256sum --check SHA256SUMS.txt
tar -xzf cfms-on-websocket-0.4.1.tar.gz
cd cfms-on-websocket-0.4.1
uv sync --locked --no-dev
cd src
cp config.toml.sample config.toml
uv run --no-dev alembic upgrade head
uv run --no-dev python main.py
```

不要使用 Python 优化模式启动服务端。

## 升级既有部署

发布包有意不包含部署实例的 `config.toml`、数据库、`init` 标记、`content` 目录、证书、凭据和其他可变或敏感状态。升级时应保留现有状态，而不能用新发布包中的范本或空目录覆盖它们。

建议按以下顺序升级：

1. 停止服务端，并备份配置、数据库、`content` 目录、证书和其他外部存储；使用 MySQL、Redis 或 S3 时也应按各自机制完成一致性备份。
2. 验证新发布包或待切换 Git 提交的来源和摘要，再替换程序文件，保留原部署状态。
3. 在代码仓库根目录运行 `uv sync --locked --no-dev`，并按需附加 `--extra cluster`、`--extra mysql` 或 `--extra ext_oidc_sso`。
4. 进入 `src/`，先运行 `uv run --no-dev maintain config sync-template --check` 审阅配置差异，再执行实际同步。
5. 运行 `uv run --no-dev alembic upgrade head` 升级数据库结构。
6. 启动服务端，检查核心版本、扩展加载、配置警告、数据库迁移和提供者连接日志，并完成登录、列表、上传和下载等基本验证。

!!! warning "数据库迁移"
    执行迁移前务必完成数据库备份。项目中的 Alembic 迁移主要针对 SQLite 设计，不能保证在其他数据库引擎上均可直接成功；MySQL 部署应先在与生产结构一致的副本上演练。

极早期、尚未使用 Alembic 管理的部署需要先在**旧代码和旧数据库结构仍匹配时**执行 `alembic stamp head`，再切换到新版本并运行升级。不要在无法确认当前结构对应版本时盲目标记迁移头；应先在副本上核对迁移历史或寻求人工处理。

发生问题时，应优先停止新实例并从升级前备份恢复，而不是在生产数据上反复尝试降级迁移。文档创建与下载风险控制可通过切回 `observe` 快速停止强制拒绝，无需为了回滚策略而降级数据库。
