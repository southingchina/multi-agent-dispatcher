# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

Configura asistentes de línea de comandos para generar resultados uniformes con respuesta, estado de salida, tiempo límite, rutas de archivos y estado de aceptación. El paquete público incluye el núcleo CLI, el esquema de resultados, un adaptador echo local y pruebas del auxiliar de actividad WorkBuddy CLI. La demostración no requiere cuentas de IA ni genera cargos; la aceptación sigue pendiente hasta verificar el resultado.

## Requisitos

Python 3.10+

## Configuración y puntos de entrada

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## Instalación y uso

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


## Alcance y limitaciones

Configura assets/agent-registry.json con ID, ejecutables, argumentos, analizador y tiempo límite; no incluyas credenciales ni cookies. Admite {skill_root}, {prompt} y {working_dir}. --allow-working-dir y --allow-writes son políticas de argumentos y registro, no un aislamiento del sistema operativo. Se excluyen adaptadores IPC/CDP de escritorio y NAS personales. Las ramas de análisis específicas no garantizan compatibilidad con clientes actuales. Los registros pueden contener respuestas; work/ no se versiona y debe anonimizarse antes de compartirlo.

## Registro de validación

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## Licencia y atribución

[MIT](LICENSE)

Son versiones de la documentación. Las interfaces, salidas CLI y ejecutables mantienen el comportamiento de la implementación actual.

[Referencia completa en chino](README.zh-CN.md) · [Política de mantenimiento de idiomas](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — Comunica problemas reproducibles con datos sintéticos. Elimina credenciales e información privada de los registros.
