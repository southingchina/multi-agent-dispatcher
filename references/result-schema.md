# 任务包与结果记录格式

## 任务包

必须包含以下字段：

- `job_id`：稳定且唯一的任务编号。
- `agent_id`：注册表中准确的节点 ID。
- `objective`：一个明确、可验证的目标。
- `context`：已经授权提供给该节点的材料或路径。
- `constraints`：安全、范围和行为限制。
- `expected_outputs`：必须交付的文件或回答内容。
- `acceptance_criteria`：能够实际检查的验收条件。
- `timeout_seconds`：明确的最大执行时间。
- `allowed_side_effects`：通常为 `read-only` 或 `workspace-write`。

## 结果记录

```json
{
  "schema_version": 1,
  "job_id": "20260712-001",
  "agent_id": "workbuddy-cli",
  "family": "workbuddy",
  "surface": "cli",
  "model": null,
  "working_directory": null,
  "directory_access": "prompt_only",
  "process_directory": "D:\\project\\reviews\\job-001\\workbuddy-cli",
  "status": "completed",
  "response": "智能体回复",
  "raw_output": "未经摘要的原始输出",
  "artifacts": [],
  "ephemeral_cleanup": [],
  "duration_seconds": 12.4,
  "exit_code": 0,
  "acceptance": "pending",
  "errors": []
}
```

执行状态只能是：

- `completed`：执行完成且取得有效回复。
- `completed_no_response`：执行结束但没有取得回复。
- `blocked_auth`：被登录或认证阻止。
- `timed_out`：执行超时。
- `failed`：执行失败。

验收状态单独记录为 `pending`、`passed`、`failed` 或 `needs_review`。

`directory_access` 只能按实际调用记录为：`prompt_only`（没有开放用户工作目录）、`read_only`（用户授权准确目录，只读）或 `workspace_write`（用户同时明确授权修改）。节点进程始终从 `process_directory` 指向的隔离任务目录启动。

`working_directory` 在 `prompt_only` 时必须为 `null`；只有传入目录授权参数时才记录实际授权目录。`ephemeral_cleanup` 记录结果和转录已经落入隔离任务目录后，从客户端缓存中清除的本次精确会话项目；没有清理时为空数组。

结果校验要求节点 ID 准确、入口类型已知、执行状态合法；使用可切换模型的节点时必须记录实际 `model`；`completed` 结果必须包含非空回复。必须保留 `raw_output` 和证据文件路径，方便追踪和复核。

`dsh` 的 `model` 来自注册表 `reported_model`，表示 NAS Harness 工作区在最近一次人工核对时显示的模型。更换工作区模型后必须同步更新该值。
