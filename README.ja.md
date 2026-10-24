# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

コマンドラインの AI アシスタントを設定し、応答、終了状態、タイムアウト、成果物パス、検収状態を共通形式で記録します。公開版は再利用可能な CLI コア、結果スキーマ、ローカル echo アダプター、WorkBuddy CLI 活動補助のテストを含みます。デモは AI アカウントやモデル料金なしで動作し、業務結果を確認するまで検収は pending のままです。

## 必要な環境

Python 3.10+

## 設定とエントリーポイント

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## 導入と使用方法

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


## 公開範囲と制限

assets/agent-registry.json に ID、実行ファイル/引数配列、パーサー、タイムアウトを設定し、認証情報や Cookie は保存しないでください。{skill_root}、{prompt}、{working_dir} に対応します。--allow-working-dir と --allow-writes は引数の方針と記録であり、OS サンドボックスではありません。デスクトップ IPC/CDP や個人 NAS のアダプターは含みません。クライアント固有の解析分岐があっても現行版との互換性を保証しません。ログには応答本文が入り得るため共有前に機密を除去してください。work/ は Git 対象外です。

## 検証記録

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## ライセンスと出典

[MIT](LICENSE)

これらは文書の言語版です。アプリ画面、CLI 出力、実行ファイルは現在の実装に従います。

[中国語の詳細リファレンス](README.zh-CN.md) · [言語版の保守方針](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — 再現できる問題は合成データで報告し、ログの認証情報や個人情報を除いてください。
