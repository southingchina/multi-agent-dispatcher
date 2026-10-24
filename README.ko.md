# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

명령줄 AI 도구를 설정해 응답, 종료 상태, 시간 초과, 산출물 경로와 검수 상태를 일관된 결과 형식으로 기록합니다. 공개판에는 재사용 가능한 CLI 코어, 결과 스키마, 로컬 echo 어댑터와 WorkBuddy CLI 활동 보조 테스트가 포함됩니다. 데모는 AI 계정이나 모델 비용 없이 로컬에서 동작하며 작업 결과를 확인하기 전 검수 상태는 pending입니다.

## 필요 환경

Python 3.10+

## 설정 및 진입점

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## 설치 및 사용

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


## 공개 범위와 제한

assets/agent-registry.json에 ID, 실행 파일/인수 배열, 파서와 시간 제한을 설정하고 자격 증명이나 쿠키는 넣지 마세요. {skill_root}, {prompt}, {working_dir}를 지원합니다. --allow-working-dir와 --allow-writes는 명령 인수 정책과 기록 기능이며 운영체제 샌드박스가 아닙니다. 데스크톱 IPC/CDP 및 개인 NAS 어댑터는 제외됩니다. 클라이언트별 파싱 분기가 있어도 최신 버전 호환성을 보장하지 않습니다. 로그에 응답 본문이 들어갈 수 있으므로 공유 전 민감 정보를 제거하세요. work/는 Git에서 제외됩니다.

## 검증 기록

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## 라이선스 및 출처

[MIT](LICENSE)

프로젝트 문서의 언어별 버전입니다. 앱 화면, CLI 출력과 실행 파일은 현재 구현을 따릅니다.

[중국어 상세 참고 문서](README.zh-CN.md) · [언어 문서 유지 관리 정책](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — 재현 가능한 문제는 합성 데이터로 보고하고 로그의 자격 증명과 개인 정보를 제거하세요.
