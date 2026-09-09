---
type: TEST_PLAN
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

# Aceitação Hermes, Codex e Claude Code
Status: DRAFT
Source: spec.md e plan.md desta fase
Updated: 2026-09-09

## O que é testado

| Cenário | Offline | Hermes real | Codex real | Claude Code real |
|---|---|---|---|---|
| Descoberta das 17 skills | Todos | Loader e invocação | Pacote e invocação | --plugin-dir e invocação, confirmados no help |
| Status somente leitura | Todos | pt-BR/en-US | pt-BR/en-US | pt-BR/en-US |
| Init → map → import → next | Todos | pt-BR/en-US | pt-BR/en-US | pt-BR/en-US |
| LOOP de cinco estágios | Todos | pt-BR/en-US | pt-BR/en-US | pt-BR/en-US |
| Dois membros fleet pelo launcher | Todos | pt-BR | pt-BR | pt-BR |
| Fleet en-US e runtime mismatch | Todos | Offline | Offline | Offline |
| Handoff, preservando IDs/gates | Todos | recebe de Claude Code | recebe de Hermes | recebe de Codex |
| Timeout, cancelamento e processo filho | Processos controlados | Sem gasto induzido | Sem gasto induzido | Sem gasto induzido |
| Evidência ausente/antiga/adulterada | Todos | Revalidação dos artefatos reais | Revalidação dos artefatos reais | Revalidação dos artefatos reais |
| Compose/cmux e pós-merge | Fixtures e Git real | Recursos isolados | Recursos isolados | Recursos isolados |

Todos os cenários reais exigem saída original, exit code, timestamps, hashes e identidade de
runtime/tarefa/worktree. Sucesso narrado pelo modelo não basta. As verificações de falha executam
processos locais controlados, sem desperdiçar chamadas remotas para provocar timeout.

Fleet real nesta matriz cobre pt-BR; não declarar fleet real en-US testada. Qualquer expansão
da matriz deverá ter orçamento próprio, em vez de consumir chamadas ilimitadas.

## Preflight

Claude Code observado: 2.1.265. Seu adapter deve usar a interface -p e interpretar o envelope
JSON nativo; adicionar essa validação ao LOOP e à fleet. Nunca usar --dangerously-skip-permissions
como padrão nem confundir --add-dir com sandbox.

Comandos existentes, somente diagnósticos:

```bash
hermes --version
hermes --help
hermes plugins doctor plugins/sdd-composy --ci
codex --version
codex exec --help
claude --version
claude --help
git --version
jq --version
docker compose version
cmux --help
```

Não ler arquivos de autenticação. Registrar capacidade e disponibilidade, não valores secretos.
O doctor do Hermes não prova descoberta pelo Codex ou Claude Code. O harness deve comprovar que os três carregaram
a versão local corrigida, e não um cache antigo. Instalação em perfil temporário somente por
mecanismo documentado de cada runtime; não alterar perfil global para contornar essa exigência.

## Fixture e isolamento

Harness cria diretório exclusivo com tempfile.TemporaryDirectory/mkdtemp, repositório Git e
commit base local. Fonte do plugin é copiada sem secrets, .git, estado operacional ou worktrees
do usuário. Fixtures contêm projeto mínimo e bundle PRD/STORIES/TECHSPEC/TASKS com aprovações
explicitamente identificadas como sintéticas e restritas ao cenário de teste.

Tarefa principal: implementar soma de dois inteiros em src/calculator.py e validar casos
positivos, negativos e zero em tests/test_calculator.py usando python3 -m unittest discover
-s tests -v dentro da fixture. Fleet usa duas tarefas independentes: src/addition.py com
tests/test_addition.py e src/subtraction.py com tests/test_subtraction.py. Não compartilhar
arquivos de implementação entre membros.

Providers rodam dentro de fronteira externa de filesystem/rede compatível com sua CLI.
Repositório temporário sozinho não é sandbox. Se não houver isolamento efetivo, o cenário
automatizado Hermes fica BLOCKED até consentimento específico para seu modo de aprovações.
Usar configuração nativa de autenticação sem despejar seu conteúdo em logs e sem mudar defaults.

Sentinelas de projeto verificam read-only. Snapshot de Git, arquivos e recursos de UI do
repositório real antes/depois comprova que o teste não alterou seu conteúdo. Não limpar diretórios
ou sessões por glob/prefixo: guardar IDs e caminhos exatos criados pelo harness.

## Comandos planejados do harness

Estes comandos dependem da implementação da Task 08; ainda não existem como evidência executada.

```bash
python3 scripts/sdd_runtime_smoke.py --mode offline --runtime all --language both --scenario all --output .planning/power/features/sdd-composy-corrections/runs/offline
python3 scripts/sdd_runtime_smoke.py --mode real --runtime all --language both --scenario all --max-calls-per-runtime 28 --output .planning/power/features/sdd-composy-corrections/runs/real
```

O modo real deve usar os adapters corrigidos e launch.sh. Invocar manualmente hermes -z ou codex
exec fora do caminho de produção não conta como teste da fleet. Codex --json gera eventos JSONL:
validar separadamente o arquivo de mensagem final. Hermes deve retornar JSON validado por código,
nunca aceitar explicação textual de que executou algo como prova de execução.

Distribuição máxima estimada por runtime: 2 chamadas read-only, 2 de inicialização, 10 para
dois LOOPs de cinco estágios, 10 para dois membros fleet de cinco estágios e 2 para handoff no ciclo Hermes → Codex → Claude Code → Hermes.
Total planejado: 26 por runtime; teto rígido: 28 por runtime (84 no conjunto dos três). Falha não dispara retry automático. Se o runner real
exigir mais estágios, registrar limite alcançado e revisar orçamento antes de prosseguir.
Limite de 300 segundos por chamada. Testes de falha do processo usam fixtures sem inferência.

## Critérios observáveis

- read-only: bytes dos arquivos de projeto idênticos; logs do runtime são classificados à parte.
- tarefa ready: contrato aprovado, dependências completas e critérios/comandos conhecidos; ID deve
  existir na projeção, não pode ser deduzido de um dict vazio.
- tarefa complete: testes executados, QA/review/verify válidos, trace consistente e artefatos
  vinculados a commit, hash e timestamp. Aprovação sintética nunca migra para o projeto real.
- identidade: cada invocação pertence a runtime, tarefa, loop, branch e worktree esperados.
- segurança: dados malformados, symlinks e contrato alterado bloqueiam antes de executar provider.
- recuperação: falha ou timeout deixa registro recuperável sem marcar COMPLETE nem repetir
  automaticamente etapas já aprovadas.
- handoff: cada runtime lê os artefatos do outro sem reinterpretar idioma, IDs ou aprovações.

## Evidências e veredito

Gerar sumário por cenário com runtime/version, provider/model observados quando disponíveis,
idioma, commit/hash do plugin, comando sanitizado, início/fim reais, exit code, recursos próprios,
hashes dos resultados e tokens/custo quando disponibilizados. Campos indisponíveis são null.
Não publicar dumps de ambiente, prompts privados, tokens de autenticação nem caminhos sensíveis.

Guardar evidências reduzidas e hashes; logs brutos ficam locais e só após sanitização entram em
relatório. Não chamar evidência VERIFIED antes de execução e revisão independente.

APPROVED exige todos os critérios obrigatórios da spec. FAIL produz REJECTED. Cenário real não
executado mantém a aceitação incompleta (BLOCKED ou NOT_RUN), mesmo se testes offline passarem.
Kanban permanece fora do escopo e não pode aparecer como validado. Falha de autenticação, cota,
permissão ou rede é separada de defeito do plugin. Não fazer commit/push de credenciais nem logs
brutos. Publicação é uma etapa posterior.
