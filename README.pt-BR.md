# Multi-Agent Dispatcher

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Português (Brasil)](README.pt-BR.md)

Configura assistentes de linha de comando para gerar resultados uniformes com resposta, código de saída, tempo limite, caminhos de arquivos e estado de aceitação. O pacote público inclui o núcleo CLI, esquema de resultados, adaptador echo local e testes do auxiliar de atividade WorkBuddy CLI. A demonstração não exige contas de IA nem gera custos de modelo; a aceitação fica pendente até a verificação do resultado.

## Requisitos

Python 3.10+

## Configuração e pontos de entrada

`assets/agent-registry.json`, `{skill_root}`, `{prompt}`, `{working_dir}`, `--registry`, `--allow-working-dir`, `--allow-writes`, `work/`

## Instalação e uso

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


## Escopo e limitações

Configure IDs, executáveis, argumentos, analisador e limite de tempo em assets/agent-registry.json, sem credenciais ou cookies. Aceita {skill_root}, {prompt} e {working_dir}. --allow-working-dir e --allow-writes são políticas de argumentos e registro, não um sandbox do sistema operacional. Adaptadores IPC/CDP de desktop e NAS pessoais estão excluídos. Ramificações de análise específicas não garantem compatibilidade com clientes atuais. Logs podem conter respostas; work/ é ignorado pelo Git e precisa ser revisado antes de ser compartilhado.

## Registro de validação

2026-10-24 · Python: 6 ✓; local echo + result schema ✓

## Licença e créditos

[MIT](LICENSE)

São versões da documentação. Interfaces, saídas CLI e executáveis mantêm o comportamento da implementação atual.

[Referência completa em chinês](README.zh-CN.md) · [Política de manutenção dos idiomas](docs/LOCALIZATION.md)

[Issues](https://github.com/southingchina/multi-agent-dispatcher/issues) — Relate problemas reproduzíveis com dados sintéticos. Remova credenciais e informações privadas dos logs.
