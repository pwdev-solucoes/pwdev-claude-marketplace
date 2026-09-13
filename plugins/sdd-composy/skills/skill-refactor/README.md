---
okf_version: "0.2"
type: usage-guide
title: "Skill Refactor"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
sources:
  - resource: "docs/skill-refactoring-guide.md"
  - resource: "https://claude.com/plugins/skill-creator"
verified: []
---

# Skill Refactor

[Skill de entrada](SKILL.md) para refatorar outras skills a partir do guia,
preservando requisitos e medindo eficiência quando houver execuções comparáveis.
Inclui referências portáveis, sem exigir o repositório de origem na instalação.

## Uso

No runtime que carregou a skill, invoque `skill-refactor` com o alvo e a intenção.
Exemplos de pedidos:

```text
Use skill-refactor para refatorar skills/resumo/SKILL.md e seus recursos.
Consumidores: Astra e Fable no perfil lean; outros modelos no perfil guided.
Preserve os requisitos atuais e prepare os casos de avaliação.
```

```text
Use skill-refactor para revisar skills/resumo/SKILL.md, sem editar arquivos.
Indique as mudanças que reduziriam contexto e como avaliar o efeito.
```

```text
Use skill-refactor para comparar a candidata de resumo com a versão anterior.
Execute somente os dois modelos disponíveis que eu indiquei, com três casos,
uma repetição e o orçamento autorizado nesta tarefa.
```

O perfil executor controla a orientação recebida por quem refatora. Os perfis
consumidores controlam o núcleo e complementos entregues na skill refatorada.
Astra/Fable começam em `lean`; demais ou desconhecidos em `guided`. Uma escolha
explícita prevalece, e resultados podem justificar outra configuração.

## Distribuição e validação

A pasta fica em `skills/` do plugin e pode ser copiada como unidade para um
runtime compatível com Agent Skills. A sintaxe de invocação e a descoberta dependem
do host. Esta mudança no código-fonte não instala nem atualiza caches do usuário.

`SKILL.md` segue o formato Agent Skills, com proveniência dentro de `metadata`.
Este README e `references/` seguem OKF v0.2. Essa separação corresponde às
convenções existentes do repositório; não é uma exceção implementada no lint OKF.

Valide a entrada com `scripts/quick_validate.py` do skill-creator quando suas
dependências estiverem disponíveis; valide os documentos narrativos com o
validador OKF do ambiente. Os [casos de avaliação](evals/evals.json) incluem
refatoração real, modelo desconhecido e pedido somente de revisão.

Antes de executar esses casos, o preparador materializa a fixture embutida em
uma pasta temporária nova e substitui `{target}` e `{run_dir}` no pedido. Essa
preparação ocorre fora do executor, inclusive no caso somente leitura. Os campos
`fixture`, `fixture_protocol`, `trigger_evals` e `routing_checks` são extensões
do conjunto de testes; os scripts originais do skill-creator não são presumidos
capazes de executar essa preparação automaticamente.

Os perfis declaram intenção de suporte. Só resultados obtidos nos modelos reais
podem demonstrar desempenho ou compatibilidade comportamental entre eles.
