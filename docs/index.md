# CFMS on WebSocket 服务端文档

本文档介绍 Confidential File Management System (CFMS) 的 WebSocket 实现之服务端部分。

CFMS 是针对“如何在互联网环境下尽可能使保密信息得到安全的管理和传输”这一问题所实现的一套解决方案。在您计划应用本项目来解决您的需求之前，请务必首先参阅 [CFMS 不是什么](what-cfms-is-not.md)。错误地使用本项目可能导致不可估量的损失，因此请您务必谨慎对待。

若希望快速设置本基于 WebSocket 协议实现的服务端（后称“服务端”），请参阅 [快速开始](getting-started.md)。

参阅 [功能概览](features/index.md) 以粗略地了解服务端支持的功能。

!!! note
    本项目仍处于活跃开发阶段，协议、配置和部署要求可能随服务端版本变化。本文档以当前开发版本的实现为依据；若文档与您实际部署的版本存在差异，应以该版本的源码、`config.toml.sample`、数据库迁移和发布说明为准。
