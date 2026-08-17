# PWDEV Flow — Desenvolvimento Portátil Orientado a Especificação

> [English version](./README.md)

Desenvolvimento com aprovação em portões, rodando nativamente **tanto no Claude
Code quanto no Codex** a partir de um único pacote. O fluxo vive em skills e
references neutras de runtime; cada host recebe um adaptador fino sobre os
mesmos contratos.

```
DISCOVER ─▶ DESIGN ─▶ PLAN ─▶ EXECUTE ─▶ [SIMPLIFY] ─▶ REVIEW ─▶ VERIFY
```

Cada fase tem entrada explícita, artefato durável e um portão visível ao humano.
Um fluxo iniciado em um runtime pode continuar no outro: os dois leem e escrevem
os mesmos artefatos `.planning/flow`.

## Instalação

Claude Code:

```bash
claude plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
claude plugin install pwdev-flow@pwdev-claude-marketplace
```

O Codex lê o mesmo pacote por `.codex-plugin/plugin.json` e invoca as skills como
`$flow-<nome>`, em vez de comandos de barra.

## Comandos

| Comando | Para quê |
|---|---|
| `/pwdev-flow:init` | Inicializa, inspeciona, retoma ou migra o workspace portátil `.planning/flow` |
| `/pwdev-flow:discover` | Levanta e aprova requisitos delimitados |
| `/pwdev-flow:design` | Produz a especificação central e suas decisões |
| `/pwdev-flow:plan` | Decompõe uma especificação aprovada em tarefas atômicas |
| `/pwdev-flow:execute` | Executa um plano aprovado, com correções delimitadas |
| `/pwdev-flow:review` | Revisa uma implementação ou um conjunto explícito de arquivos |
| `/pwdev-flow:verify` | Verifica de forma adversarial, com evidência nova, que a fase terminou |
| `/pwdev-flow:simplify` | Analisa uma fase concluída e aplica as simplificações aprovadas |
| `/pwdev-flow:quick` | Entrega uma mudança pequena e delimitada (até cinco arquivos de implementação) |
| `/pwdev-flow:product` | Cria um requisito de produto com portão de aprovação |
| `/pwdev-flow:memory` | Cura ou consulta a memória durável do projeto |
| `/pwdev-flow:health` | Diagnostica a saúde do repositório e do workspace sem alterar nada |
| `/pwdev-flow:audit` | Registra, inspeciona, resume ou valida eventos de auditoria semântica |
| `/pwdev-flow:maintenance` | Inventaria, arquiva ou resume artefatos com segurança |
| `/pwdev-flow:compat` | Inspeciona ou planeja a migração de artefatos legados do PWDEV Code |
| `/pwdev-flow:delegate` | Delega uma tarefa delimitada a uma CLI de código externa, sob guarda |
| `/pwdev-flow:fleet` | Lança, inspeciona ou desmonta frotas autônomas de fases isoladas |

## O protocolo compartilhado de artefatos

Tudo vive sob `.planning/flow/`: `config.json`, `state.md`, contratos de fase em
`phases/<slug>/`, memória, relatórios e a escrituração da frota. O campo
`runtime` no `config.json` registra qual adaptador inicializou o workspace por
último; é metadado e nunca torna os artefatos ilegíveis no outro host.

## Frotas autônomas

O `/pwdev-flow:fleet` roda fases aprovadas em paralelo, cada uma no seu próprio
worktree Git, com stack Docker Compose e painel tmux próprios. Cada membro
executa `PLAN → EXECUTE → REVIEW → VERIFY` sem supervisão, commita por estágio
dentro do próprio branch e para após no máximo dois ciclos de correção
rejeitados.

Cada runtime conduz a sua própria CLI headless:

```text
codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <schema> --output-last-message <result> <prompt>
claude -p --dangerously-skip-permissions --no-session-persistence --output-format json <prompt>
```

Cada vetor é construído em exatamente um adaptador,
`scripts/fleet-engine-<runtime>.sh`, e nada mais pode montar um comando de
provider nem acrescentar flag de permissão. O runtime é fixado pelo lançador que
você escolhe, antes de qualquer mutação, e fica vinculado ao membro central — um
runner cujo adaptador discorde desse membro se recusa a iniciar. Todo o resto —
locks, hashes de contrato, posse do process group, validação de resultado,
commits, o limite de correções — é compartilhado.

**Lançar uma frota exige reconhecimento explícito da flag perigosa do runtime.**
Esse reconhecimento autoriza apenas o lançamento solicitado.

## Delegação

O `/pwdev-flow:delegate` entrega uma tarefa delimitada a uma CLI externa da lista
permitida (Codex, OpenCode, Kimi, Gemini, Kiro). O runner empacotado monta
arrays de argumentos, nunca strings de shell; exibe o vetor exato expandido com
um token de confirmação SHA-256; aplica lock de escrita e checagem de mutação em
modo leitura; e nunca herda autorização de frota. O agente primário precisa
revisar o diff resultante de forma independente — resumo do delegado não é prova.

## Auditoria

Opt-in por `"audit": true`. Os eventos são anexados a
`.planning/flow/audit/events.jsonl` **somente depois** que a ação descrita
realmente aconteceu, e carregam apenas metadados semânticos — nunca prompts,
saída do provider, ambiente ou caminhos absolutos.

Hooks do Claude estão ausentes de propósito: telemetria de hook seria específica
de um host e poderia ser confundida com uma trilha portátil do fluxo.

## Postura de segurança

- Ler e escrever somente dentro do repositório e de locais explicitamente autorizados.
- Nunca ler ou expor `.env`, credenciais, tokens, chaves ou `.env.fleet`.
- Nunca commitar, dar push, criar branch ou mutar serviços externos sem autorização.
- Rodar o comando que prova cada afirmação de conclusão; nunca confiar num resumo.
- Parar após dois ciclos de correção falhos e pedir direção humana.

## Estrutura

```text
plugins/pwdev-flow/
├── .claude-plugin/plugin.json   # manifesto Claude
├── .codex-plugin/plugin.json    # manifesto Codex
├── commands/                    # 17 adaptadores de comando Claude
├── skills/                      # 17 skills portáteis
├── references/                  # contratos compartilhados de fluxo e segurança
├── scripts/                     # ciclo de vida mais um adaptador por runtime
└── templates/                   # schema de resultado e stack Compose da frota
```

## Licença

Apache-2.0. Veja [LICENSE](../../LICENSE).
