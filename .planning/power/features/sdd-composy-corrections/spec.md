---
type: SPEC
okf_version: "0.2"
generated:
  by: agent:codex
  at: "2026-09-09T17:02:36Z"
lifecycle:
  status: APPROVED
human_approval:
  status: APPROVED
  at: "2026-09-09T17:14:54Z"
verified: []
---

# SDD Composy — Correções e paridade Hermes/Codex/Claude Code
Status: APPROVED
Source: revisão do plugin e solicitação de plano completo de correção
Updated: 2026-09-09

## Problem

A revisão encontrou tarefas vazias consideradas válidas, erros mascarados por status ativo,
leitura do estado pelo Markdown, comando Hermes inexistente, registros fleet incompatíveis com
schema, caminho Compose incorreto e confirmação imprecisa de init/idioma. Os 299 testes da
última revisão passaram, mas incluem assertivas textuais que não comprovam execução.

Inspeção adicional para este plano: Codex 0.153.4 documenta `--json` como eventos JSONL,
enquanto `scripts/loop-engine-codex.py` aplica `json.loads` à saída inteira. Hermes instalado:
0.20.4; possui `-z/--oneshot` e `--in`, mas não possui `run`. Essas versões são baseline observado,
não promessa de compatibilidade com todas as versões futuras. Contexto Power ausente neste
checkout; scripts, schemas e ajuda das CLIs foram usados como fontes de interfaces.

## Approach

Corrigir primeiro contratos e estado compartilhados, depois publicação e idioma, adaptadores,
fleet, documentação e integração real. Executar o mesmo cenário isolado com Hermes, Codex e Claude Code.
Testes de core, simuladores de processos, descoberta real e inferência real são evidências distintas.

## Decisions

- DEC-001: JSON validado em `.planning/sdd-composy/tasks/` é autoridade operacional; Markdown
  expressa intenção e aprovação. Alternativa rejeitada: deduzir prontidão de arquivos Markdown.
  Divergência produz diagnóstico e exige reconciliação explícita; nenhuma migração silenciosa.
- DEC-002: erros têm precedência sobre tarefas e fleet ativas. JSON parseável não significa
  contrato válido. Contrato ausente ou vazio não gera tarefa executável.
- DEC-003: usar CLI real documentada e validar seu resultado fora do modelo. Para Codex, mensagem
  final em arquivo próprio; eventos JSONL separados. Para Hermes, saída final do one-shot validada
  por schema e identidade. O modo one-shot pode pular aprovações: só executar em isolamento
  externo ou mediante consentimento específico registrado; `--safe-mode` e prompt não são sandbox.
- DEC-004: `.claude` existente permanece intacto. Verificação distingue `symlink`, `existing_directory`
  e `conflict`; nunca representa diretório como symlink. Novo projeto recebe `.claude -> .agents`.
- DEC-005: preservar nomes de runtime públicos existentes. CLI `claude` é normalizado para
  metadado `claude-code`; acrescentar `hermes`, mantendo `codex`. Worktrees externos usam caminho
  absoluto canônico validado contra Git, com migração explícita para registros antigos.
- DEC-006: restaurar o requisito original de idioma obrigatório também na API do mapa. Gerar
  governança em pt-BR/en-US com renderer localizado; textos de evidência e identificadores permanecem
  intactos. Arquivos de governança existentes não são reescritos automaticamente.
- DEC-007: cada decisão é reversível por commit, mas migrações de estado exigem backup e relatório.
  Custo: consumidores antigos podem receber diagnóstico de inconsistência até reconciliarem registros.

## Global Constraints

- Preservar alterações locais existentes em sdd_status.py e test_sdd_composy_hermes.py; registrar baseline antes da execução.
- Não marcar tarefas completas, gates aprovados ou evidências verificadas por existência de arquivo, texto do modelo ou teste de substring.
- Não traduzir IDs, enums, chaves JSON, nomes de arquivos, comandos ou evidências do usuário; idioma somente pt-BR ou en-US, escolhido no init.
- Manter campos JSON desconhecidos, publicação atômica e recusa de symlinks nos destinos e ancestrais controlados pelo plugin.
- Read-only significa nenhum arquivo de projeto criado/modificado; logs nativos do runtime são medidos separadamente.
- Não alterar autenticação, modelo padrão, configuração global, tarefas reais, branches reais ou publicar releases como parte dos testes.
- Testes reais usam repositórios temporários próprios, dois membros fleet e no máximo 300 segundos por invocação de provider; sem repetição automática de inferência malsucedida.
- Executar serialmente os providers; até 28 invocações remotas por runtime no ciclo de aceitação, registrando custo/uso quando disponível, nunca inventando zero.
- Inferência real e fleet que não possam executar por permissão, autenticação, custo ou indisponibilidade ficam BLOCKED/NOT_RUN, nunca PASS.
- Hermes, Codex e Claude Code são alvos obrigatórios de aceitação real e regressão offline.
- Kanban Hermes não está implementado neste escopo; documentação deve dizer indisponível, sem promessa de suporte operacional.

## Acceptance criteria

- AC-01: tarefas vazias, schema inválido, dependências impossíveis e JSON/Markdown divergentes são diagnosticados; estado inválido nunca vira active.
- AC-02: status lê projeção JSON e trace no diretório operacional correto; seleção de feature funciona; ausência de fila pronta não sugere executar tarefa inexistente.
- AC-03: init retorna apenas criações reais e estado de compatibilidade preciso; plan/inspect não escrevem; verify diagnostica configuração/estado ausente; reaplicar é idempotente.
- AC-04: init e map respeitam os dois idiomas e impedem geração sem idioma inclusive pela API; worktrees aninhados e saída do próprio mapa não contaminam inventário.
- AC-05: descoberta registra as 17 skills; bootstrap não executa init implicitamente; Hermes, Codex e Claude Code executam vetores reais e resultados estruturados válidos.
- AC-06: LOOP nos três runtimes rejeita resultado inválido, timeout, estágio errado, aprovação ausente e VERIFY ausente/antigo/adulterado.
- AC-07: launcher, runner, status e teardown concordam com schema fleet; runtime errado, caminho externo não registrado e contrato alterado são recusados.
- AC-08: dois membros têm branches/worktrees/portas distintos; Compose encontra template; cancelamento e falhas preservam recuperação e encerram processos próprios.
- AC-09: merge somente em repositório descartável de teste com autorização do harness; verificação após merge falhando impede limpeza e conclusão.
- AC-10: resultados reais Hermes, Codex e Claude Code cobrem consulta somente leitura, init/map/import/next, tarefa mínima e fleet pelo launcher; portabilidade conserva IDs, aprovações e histórico.
- AC-11: documentação e evidências diferenciam inferência real, mocks, checks locais e limitações; nenhum teste é enfraquecido para obter verde.

## Out of scope

Publicação, deploy, instalação permanente no perfil do usuário, migração automática do bundle do
manual existente, implementação de Kanban, alterações no Hermes/Codex/Claude Code upstream e novas features
de produto. Dados inválidos existentes serão diagnosticados e não receberão aprovação retroativa.

## Risks

Hermes one-shot pode dispensar confirmação; ambiente isolado é pré-condição. Provider pode falhar
por rede/cota. CLI pode mudar; help/version entram nas evidências. Schema atual exige caminho
relativo, incompatível com worktree irmão: evolução deve versionar o formato e preservar leitura
legada sem autorizar execução de um registro ainda não migrado.
