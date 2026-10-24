# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

Configurez des assistants en ligne de commande pour produire un résultat uniforme : réponse, code de sortie, délai, chemins des livrables et état d'acceptation. Le paquet public contient le noyau CLI, le schéma de résultat, un adaptateur echo local et les tests de l'auxiliaire d'activité WorkBuddy CLI. La démonstration n'exige aucun compte IA et ne génère aucun coût de modèle ; l'acceptation reste en attente jusqu'à vérification du résultat.

## Prérequis

Python 3.10+

## Configuration et points d’entrée

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## Installation et utilisation

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


## Périmètre et limites

Configurez ID, exécutables, arguments, analyseur et délai dans assets/agent-registry.json, sans identifiants secrets ni cookies. Les variables {skill_root}, {prompt} et {working_dir} sont reconnues. --allow-working-dir et --allow-writes définissent une politique d'arguments et de traçage, pas un bac à sable système. Les adaptateurs IPC/CDP et NAS personnels sont exclus. Les branches d'analyse spécifiques ne garantissent pas les versions actuelles des clients. Les journaux peuvent contenir des réponses ; work/ est ignoré par Git et doit être expurgé avant partage.

## Historique de validation

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## Licence et attribution

[MIT](LICENSE)

Il s’agit de versions de la documentation. Interfaces, sorties CLI et exécutables conservent le comportement de l’implémentation actuelle.

[Référence complète en chinois](README.zh-CN.md) · [Politique de maintenance des langues](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — Signalez les problèmes reproductibles avec des données synthétiques. Retirez identifiants secrets et informations privées des journaux.
