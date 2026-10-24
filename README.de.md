# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

Konfiguriert Kommandozeilen-Assistenten für einheitliche Aufgabenergebnisse mit Antwort, Exit-Status, Zeitlimit, Artefaktpfaden und Abnahmestatus. Das öffentliche Paket enthält CLI-Kern, Ergebnisschema, lokalen Echo-Adapter und Tests der WorkBuddy-CLI-Aktivitätshilfe. Die Demo benötigt keine KI-Konten und verursacht keine Modellkosten. Die Abnahme bleibt bis zur Ergebnisprüfung pending.

## Voraussetzungen

Python 3.10+

## Konfiguration und Einstiegspunkte

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## Installation und Verwendung

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


## Umfang und Einschränkungen

IDs, Programm-/Argumentlisten, Parser und Zeitlimit in assets/agent-registry.json konfigurieren; keine Zugangsdaten oder Cookies ablegen. {skill_root}, {prompt} und {working_dir} werden unterstützt. --allow-working-dir und --allow-writes sind Argument- und Protokollierungsregeln, keine Betriebssystem-Sandbox. Desktop-IPC/CDP- und private NAS-Adapter sind ausgeschlossen. Vorhandene clientbezogene Parser garantieren keine aktuelle Kompatibilität. Protokolle können Antworten enthalten; work/ ist von Git ausgeschlossen und vor Weitergabe zu bereinigen.

## Prüfstand

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## Lizenz und Herkunft

[MIT](LICENSE)

Dies sind Sprachfassungen der Dokumentation. Oberflächen, CLI-Ausgaben und ausführbare Pakete folgen weiterhin der aktuellen Implementierung.

[Vollständige chinesische Referenz](README.zh-CN.md) · [Pflege der Sprachfassungen](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — Reproduzierbare Probleme mit synthetischen Daten melden. Zugangsdaten und private Informationen aus Protokollen entfernen.
