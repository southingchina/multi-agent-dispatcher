# Multi-Agent Dispatcher · 可配置 CLI 调度核心

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

将配置的命令行助手包装成统一任务结果：保留响应、退出状态、超时、产物路径与待验收标记。公开版先发布可复用的 **CLI 核心、结果协议和本地演示适配器**，无需账号即可验证调用流程。

## 快速开始

Python 3.10+，核心只用标准库：

```shell
git clone https://github.com/southingchina/multi-agent-dispatcher.git
cd multi-agent-dispatcher
python scripts/discover_agents.py
python scripts/dispatch_cli.py --agent local-demo --prompt "hello" --job-dir ./work/demo
python scripts/validate_result.py ./work/demo/result.json
```

演示只启动 `examples/echo_agent.py`，不会调用真实 AI、登录外部服务或产生模型费用。结果中 `acceptance: pending` 表示执行结果仍需按任务目标验收，进程成功不等于业务正确。

## 接入自己的 CLI

编辑 `assets/agent-registry.json`：设置唯一 ID、命令数组、参数、响应解析方式及超时。支持 `{skill_root}`、`{prompt}`、`{working_dir}` 占位符；Windows 可填自己的可执行文件绝对路径。不要把令牌、Cookie 或账号缓存写进注册表。

默认只传提示词。`--allow-working-dir` 和 `--allow-writes` 显式声明目录访问范围；这些是参数与结果记录策略，**不是操作系统沙盒**。调用不可信命令时应使用另外的权限隔离。使用 `--registry` 可保留独立的本地配置文件。

## 发布范围

源项目还有面向特定桌面客户端、IPC、CDP 与个人 NAS 的适配器；其版本与认证方式尚不适合通用分发，因此公开版不包含它们。`workbuddy_cli_activity.py` 保留活动状态辅助层和独立测试，不含个人账号或应用安装路径。已存在的特定 CLI 响应解析分支不表示所有客户端版本都经过当前验证。

## 验证

```shell
python -m unittest discover -s scripts/tests -p "test_*.py"
```

还应执行上面的本地演示和结果验证，验证真实的子进程到结果文件链路。任务日志可能包含响应正文，默认 `work/` 不跟踪；分享前请脱敏。MIT。
