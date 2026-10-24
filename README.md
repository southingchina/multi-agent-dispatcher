# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

Configure command-line assistants to produce a consistent task result containing their response, exit status, timeout, artifact paths and acceptance status. The public package contains the reusable CLI core, result schema, local echo adapter and WorkBuddy CLI activity helper tests. The demo runs locally without AI accounts or model charges; acceptance remains pending until the task result is checked.

## Requirements

Python 3.10+

## Configuration and entry points

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## Installation and usage

```shell
git clone https://github.com/southingchina/multi-agent-dispatcher.git
cd multi-agent-dispatcher
python scripts/discover_agents.py
python scripts/dispatch_cli.py --agent local-demo --prompt "hello" --job-dir ./work/demo
python scripts/validate_result.py ./work/demo/result.json
```


```shell
python -m unittest discover -s scripts/tests -p "test_*.py"
```


## Scope and limitations

Configure assets/agent-registry.json with IDs, executable/argument arrays, parser and timeout; keep credentials and cookies out of it. The {skill_root}, {prompt} and {working_dir} placeholders are supported. --allow-working-dir and --allow-writes record and constrain command arguments: they are not an OS sandbox. Desktop IPC/CDP and personal NAS adapters are excluded. Existing client-specific parsing branches do not establish compatibility with current clients. Logs may contain responses; work/ is ignored by Git, and shared logs need redaction.

## Validation record

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## License and attribution

[MIT](LICENSE)

These are documentation editions. Application interfaces, CLI output and executable releases retain the behavior of the current implementation.

[Complete Chinese reference](README.zh-CN.md) · [Language maintenance policy](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — Report a reproducible issue with synthetic data. Remove credentials and private information from logs.
