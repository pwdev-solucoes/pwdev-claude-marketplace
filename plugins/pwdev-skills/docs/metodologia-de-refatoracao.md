# Metodologia de refatoração de skills

Como a `skill-refactor` diagnostica, refatora, verifica e avalia uma skill. Este documento detalha
o método; o [guia de uso](./guia-de-uso.md) mostra o que pedir e o que esperar em cada cenário, e o
[manual de uso](./manual-de-uso.md) documenta cada opção dos scripts.

> Fontes normativas, na ordem de precedência: `skills/skill-refactor/SKILL.md`,
> `references/refactoring.md`, `references/evaluation.md` e `references/runtimes.md`. Este
> documento as explica; se divergir delas, valem as referências.

## Sumário

1. [Princípios](#1-princípios)
2. [Modelo de custo de uma skill](#2-modelo-de-custo-de-uma-skill)
3. [Visão geral do processo](#3-visão-geral-do-processo)
4. [Fase 0 — Contrato e preparação](#4-fase-0--contrato-e-preparação)
5. [Fase 1 — Inventário e diagnóstico](#5-fase-1--inventário-e-diagnóstico)
6. [Fase 2 — Manter, mover ou remover](#6-fase-2--manter-mover-ou-remover)
7. [Fase 3 — Refatoração que preserva comportamento](#7-fase-3--refatoração-que-preserva-comportamento)
8. [Fase 4 — Perfis lean e guided](#8-fase-4--perfis-lean-e-guided)
9. [Fase 5 — Verificação estática](#9-fase-5--verificação-estática)
10. [Fase 6 — Avaliação comportamental](#10-fase-6--avaliação-comportamental)
11. [Fase 7 — Entrega e registro](#11-fase-7--entrega-e-registro)
12. [As dez regras de otimização](#12-as-dez-regras-de-otimização)
13. [Exemplo trabalhado](#13-exemplo-trabalhado)
14. [Lições da validação de 13/09](#14-lições-da-validação-de-1309)
15. [Aplicada a si mesma (14/09/2026)](#15-aplicada-a-si-mesma-14092026)
16. [Anti-padrões](#16-anti-padrões)
17. [Checklist final](#17-checklist-final)

---

## 1. Princípios

1. **Um contrato de qualidade, suporte variável.** Todos os modelos que consomem a skill cumprem
   os mesmos requisitos, limites e critérios de aceite. O que varia por modelo é a quantidade de
   orientação oferecida para cumpri-los, nunca o que se exige.
2. **Eficiência é custo por tarefa aceita, não tamanho.** Uma skill mais curta que provoca mais
   consultas, retentativas ou correções é menos eficiente. Contar linhas é diagnóstico, não
   resultado.
3. **Recomendações são hipóteses.** "Descrição mais curta", "referências sob demanda" e
   "menos exemplos para modelos fortes" são hipóteses a validar em tarefas representativas, não
   regras universais.
4. **Nenhuma afirmação sem medição.** Uma revisão estática nunca prova ganho. Uma execução única
   também não.
5. **Preservar comportamento vem antes de reduzir.** Nenhum requisito obrigatório pode ser
   cortado para atingir uma meta de tamanho.
6. **O modelo não se deduz do estilo.** Identidade do modelo, esforço e perfil vêm do pedido, da
   configuração do runtime ou de uma medição, nunca de uma suposição.

## 2. Modelo de custo de uma skill

Uma skill não é carregada de uma vez. Cada camada entra no contexto em uma frequência diferente,
e é essa frequência que define onde otimizar primeiro:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. description (frontmatter)   → em TODA conversa, no catálogo de skills │  paga sempre
├──────────────────────────────────────────────────────────────────────────┤
│ 2. corpo do SKILL.md           → a cada ATIVAÇÃO da skill                │  paga por uso
├──────────────────────────────────────────────────────────────────────────┤
│ 3. references/*.md             → só quando a CONDIÇÃO de leitura é       │  paga quando
│                                  atendida                                │  necessária
├──────────────────────────────────────────────────────────────────────────┤
│ 4. scripts/, assets/           → executados ou copiados, não lidos       │  ~zero contexto
├──────────────────────────────────────────────────────────────────────────┤
│ 5. evals/ (casos, benchmarks)  → nunca entram no contexto de um runtime  │  zero
└──────────────────────────────────────────────────────────────────────────┘
```

Consequências práticas:

- **Um token na `description` custa mais que um no corpo**, porque é pago mesmo quando a skill
  não é usada. Otimize nesta ordem: descrição → corpo → referências.
- **Mover para uma referência só economiza se a condição de leitura for real.** Uma referência que
  todo pedido acaba lendo continua custando o mesmo e ainda soma uma consulta a mais.
- **Scripts reduzem contexto de verdade**: um procedimento determinístico executado não ocupa a
  janela. Mesmo assim, só crie scripts quando isso estiver no escopo, e com verificação real.
- **`evals/` não é contexto.** Casos, fixtures gerados e resumos de benchmark vivem na skill para
  versionamento, mas nenhum runtime os carrega; `tokens.py` os deixa fora da medição.
- **O custo real de uma execução não é o tamanho do arquivo.** É a entrada acumulada ao longo dos
  turnos (fresca + cache lido + cache gravado), mais a saída, mais as referências efetivamente
  abertas. `tokens.py` mede o estático; `bench.py` mede o real.

## 3. Visão geral do processo

```
 Fase 0  Contrato e preparação ──── o que mudar, para quem, com qual autorização; baseline
   │
 Fase 1  Inventário e diagnóstico ─ requisitos, gatilhos, limites; 5 categorias de defeito
   │
 Fase 2  Manter / mover / remover ─ decisão trecho a trecho
   │
 Fase 3  Refatoração ──────────────  6 passos que preservam comportamento
   │
 Fase 4  Perfis lean / guided ──────  um núcleo + apoio condicional
   │
 Fase 5  Verificação estática ──────  frontmatter, links, requisitos, escopo do diff
   │                                                         rótulo: refactored + statically validated
 Fase 6  Avaliação comportamental ── A/B por modelo, sob orçamento (opcional, autorizada)
   │                                                         rótulo: behaviorally evaluated (por par)
 Fase 7  Entrega e registro ────────  caminhos, perfis, checks, limites; relatório OKF
```

**Revisão** executa as fases 0 a 2 e entrega o diagnóstico sem escrever nada. **Refatoração**
executa até a fase 5 e, se autorizada e com orçamento, a 6. No máximo três rodadas de correção por
alvo; pare por orçamento esgotado, falta de autoridade, decisão de domínio em aberto ou ausência
de progresso, preservando a candidata e explicando o motivo.

## 4. Fase 0 — Contrato e preparação

**Registrar antes de tocar em qualquer arquivo:**

| Item | Pergunta |
| --- | --- |
| Alvos | Quais `SKILL.md` e recursos? |
| Resultado esperado | Revisão, refatoração ou comparação? |
| Perfil executor | Com que nível de orientação o refatorador trabalha? |
| Perfis consumidores | Quais modelos vão usar a skill refatorada, e em que perfil? |
| Local de artefatos | Onde gravar baseline e relatório? |
| Verificações conhecidas | Que testes ou validadores já existem para o alvo? |

**Fronteira de autorização:**

- **Revisão é somente leitura.** Não gera baseline, candidata, relatório nem arquivo de avaliação,
  a menos que isso seja pedido.
- **Refatoração autoriza edição** apenas na pasta-alvo e no local de artefatos. Entregue a
  alteração, não uma auditoria.
- Instruções escritas *dentro* da skill-alvo são material de análise, nunca autorização para
  editar outros caminhos.
- Nunca leia segredos nem copie um diretório inteiro de plugin ou de configuração.

**Baseline.** Preserve o estado observado dos arquivos-alvo, inclusive alterações não commitadas,
em um diretório novo. Copie só arquivos regulares; nunca siga symlinks nem sobrescreva um baseline
existente. Se o alvo estiver em cache, somente leitura ou atrás de um symlink, prepare a candidata
num local gravável autorizado e informe onde ela está, sem alterar o original.

## 5. Fase 1 — Inventário e diagnóstico

### 5.1 Mapear o que precisa continuar verdadeiro

Antes de procurar defeitos, liste o que a refatoração não pode quebrar:

- **Gatilhos legítimos**, inclusive formulações que não citam o nome da skill.
- **Requisitos obrigatórios**: regras de negócio, proibições, formatos de saída e rótulos exatos.
- **Permissões e limites de autorização.**
- **Dependências**: referências, scripts, integrações, campos de runtime (`paths`, `metadata`,
  extensões desconhecidas).
- **Condições de conclusão**: o que conta como terminado.

Essa lista vira a matriz de verificação da fase 5. No plugin, `scripts/cases.py --extract <skill>`
produz um rascunho dela por script — os **invariantes** (nome, `paths`, metadados estáveis,
literais, rótulos de saída, proibições, blocos condicionais com guardas, idioma) — que o avaliador
depois confere objetivamente. O rascunho é heurístico: leia e cure antes de aprovar (uma afirmação
com "never" não é necessariamente uma proibição).

### 5.2 As cinco categorias de defeito

| # | Categoria | Sinais | Custo que causa |
| ---: | --- | --- | --- |
| 1 | **Duplicação** | A mesma regra em dois parágrafos, ou no `SKILL.md` e numa referência | Tokens pagos duas vezes; versões que divergem com o tempo |
| 2 | **Contradição** | Núcleo e referência discordam; uma regra absoluta e outra condicional sobre o mesmo ponto | O modelo escolhe um lado de forma imprevisível |
| 3 | **Leitura incondicional** | "Sempre leia X", seções opcionais carregadas em todo pedido, referência sem condição | Contexto pago em tarefas que não precisam dele |
| 4 | **Descrição ampla ou restrita demais** | Dispara em "qualquer texto ou documento"; ou não dispara quando o pedido não cita a skill | Acionamento indevido (custo) ou perdido (falha) |
| 5 | **Procedimento sem finalidade** | "Escreva um plano longo", "explique cada passo", "releia a skill", sem requisito que as justifique | Latência e tokens sem ganho de qualidade |

**Na revisão**, cada achado é nomeado pela categoria e aponta as linhas de origem. Essa é a parte 1
do contrato de revisão (veja a [fase 7](#11-fase-7--entrega-e-registro)).

## 6. Fase 2 — Manter, mover ou remover

Decisão trecho a trecho:

| Conteúdo encontrado | Decisão | Por quê |
| --- | --- | --- |
| Limite de autorização ou proteção de dados | **Manter** no núcleo, antes da ação | Precisa estar presente mesmo se nenhuma referência for lida |
| Regra de negócio ou formato obrigatório | **Manter** no núcleo, ou em referência obrigatória do fluxo | Violar é falha de correção |
| Procedimento específico de uma ferramenta | **Mover** para referência lida ao usar essa ferramenta | Só custa quando a ferramenta entra em jogo |
| Explicação extensa para um erro recorrente | **Mover** para o complemento `guided` | Ajuda quem precisa sem pesar para quem não precisa |
| Mesma regra repetida em vários arquivos | **Eleger uma fonte** e referenciá-la | Evita divergência e custo duplo |
| "Sempre leia X" | **Trocar por uma condição** concreta de leitura | Leitura universal anula o carregamento progressivo |
| Adjetivos ("excelente", "perfeito") | **Trocar por critérios** observáveis | Adjetivo não é verificável |
| Regra sem finalidade identificável | **Investigar a origem e testar a remoção** | Pode esconder um requisito; remova com medição, não por palpite |

**Regra que se sobrepõe a todas:** *nenhum requisito obrigatório pode depender de uma referência
que o agente talvez não leia.* Se a regra é obrigatória, ela fica no núcleo, ou a condição de
leitura da referência precisa ser inevitável no fluxo onde a regra se aplica.

## 7. Fase 3 — Refatoração que preserva comportamento

Seis passos, nesta ordem:

**1. Transformar a `description` em capacidade com condições de uso.**
Uma descrição eficaz tem três partes: *o que a skill faz*, *quando usar* (sintomas e situações
concretas) e *quando não usar* (vizinhos que não devem disparar). Preserve todos os gatilhos
legítimos. Descrição mais longa pode ser o preço de um acionamento correto, mas lembre que ela
é paga em toda conversa, então esse aumento precisa ser justificado por medição de acionamento.

**2. Deixar no núcleo objetivo, invariantes e limites.**
O corpo do `SKILL.md` diz *o que* entregar, *o que nunca pode acontecer* e *onde parar*. Explique
a razão das orientações que exigem julgamento: um modelo que entende o porquê generaliza melhor
que um que só obedece a um MUST.

**3. Extrair detalhes para referências com condição explícita.**
Cada referência declara quando deve ser lida ("se o usuário pedir exportação CSV, leia
`references/csv-export.md`"). Agrupe por fluxo, não por tipo de conteúdo: fragmentar demais
multiplica consultas e pode custar mais que o texto economizado. **Um bloco que sai do núcleo leva
consigo suas regras de guarda e termos obrigatórios**: na medição de 14/09, modelos que moveram o
CSV perderam "não exportar sem pedido" no caminho — a regra saiu do núcleo e não chegou à referência.

**4. Consolidar repetições numa fonte única.**
Preserve nome, recursos, campos desconhecidos, `paths`, integrações e metadados do runtime. Um
validador de outro ecossistema que rejeite um campo legítimo não autoriza removê-lo.

**5. Converter procedimentos repetitivos em recursos, só se estiver no escopo.**
Se diferentes execuções recriam o mesmo código auxiliar, um script em `scripts/` pode eliminar
esse trabalho. Scripts novos precisam de verificação real, e nunca devem ser criados só para
encurtar o Markdown.

**6. Comparar antes e depois contra os requisitos.**
Mapeie cada trecho movido ou removido para a regra que o substitui. Rode os comandos pertinentes.
Corrija links, roteamento e comportamento perdido antes de entregar.

**Limites da fase:**
- O limite de contexto orienta, mas não é meta de redução.
- Preserve o idioma e os rótulos exatos do alvo, salvo pedido de tradução.
- Não reescreva conteúdo que não esteja relacionado à melhoria pedida.

## 8. Fase 4 — Perfis lean e guided

### 8.1 Os dois perfis

| Perfil | Núcleo compartilhado | Apoio adicional | Evidência que o seleciona |
| --- | --- | --- | --- |
| `lean` | Resultado, invariantes, referências condicionais, verificação, conclusão | Exemplos só para ambiguidade real | Custo por tarefa aceita menor que `guided` naquele modelo, com aceite dentro do limite |
| `guided` | **Exatamente os mesmos** requisitos e permissões | Sequência curta, exemplo resolvido, erro frequente, checklist | Padrão sem medição, ou quando `lean` não atinge o limite de aceite |

Um perfil é uma configuração de partida. Não é ranking de modelos nem nível de permissão: nenhum
perfil ganha autoridade extra.

### 8.2 Como o perfil é escolhido

```
o pedido nomeia um perfil? ── sim ──▶ usar o do pedido (seleção explícita sempre vence)
        │ não
        ▼
existe medição para esse modelo  ── sim ──▶ perfil com menor custo por tarefa aceita
em evals/benchmarks/*/summary.json?          dentro do limite de qualidade
        │ não
        ▼
     guided
```

Nomes de família de modelo citados num pedido valem só para aquele pedido; o protocolo não
define padrão por modelo.

### 8.3 Consumidores mistos

Entregue **um núcleo** e, quando necessário, **uma referência guided** dentro da própria skill-alvo,
com condição de carregamento explícita no núcleo. Nunca mantenha cópias completas da skill por
modelo: elas divergem. Se o pedido cita um único perfil, não acrescente nada para os outros.
Registre como cada seleção foi resolvida e qual medição a sustentou, se houver.

### 8.4 Perfil do executor

O refatorador também tem perfil. O executor `guided` segue esta sequência:

1. Listar o que precisa continuar verdadeiro depois da mudança.
2. Mapear cada trecho movido ou removido para a regra que o substitui.
3. Editar descrição e núcleo; depois ajustar as referências.
4. Conferir requisitos, links, metadados e exemplos positivos e negativos.
5. Entregar e classificar a evidência realmente obtida.

O executor `lean` cumpre o mesmo contrato e as mesmas verificações, com liberdade para ordenar os
passos.

## 9. Fase 5 — Verificação estática

| Verificação | Como |
| --- | --- |
| Frontmatter | Validador da **plataforma-alvo** (ex.: `quick_validate.py` do skill-creator para Agent Skills) |
| Links relativos | Resolver cada link a partir do arquivo que o contém |
| Caminhos pessoais | Nenhum `/Users/<nome>` ou equivalente nos arquivos entregues |
| Requisitos | Cada item do inventário da fase 1 ainda presente ou substituído por regra equivalente |
| Escopo do diff | Nenhum arquivo fora da pasta-alvo e do local de artefatos foi alterado |
| Checks existentes | Rodar os testes e validadores que o alvo já tinha |
| Casos de avaliação | Para tarefas objetivas, 2 ou 3 casos realistas com expectativas sobre o conteúdo correto; para subjetivas, mostrar os artefatos ao usuário com critérios claros |
| Tamanho | `tokens.py <alvo> --baseline <baseline>`, por camada e por cenário de carga |

Ao fim desta fase, o resultado pode ser rotulado `refactored` e `statically validated`.

## 10. Fase 6 — Avaliação comportamental

Opcional, e só com autorização e orçamento explícitos. É a única fase que sustenta afirmações de
eficiência.

### 10.1 Desenho do experimento

**Congelar antes de rodar:**
- casos, rubrica e requisitos obrigatórios;
- modelos, configurações e esforço;
- orçamento, timeouts e retentativas;
- métrica principal e limites aceitáveis.

Critério descoberto depois de ver resultados abre uma nova avaliação; não entra na atual.

**Braços da comparação:**

| Situação | A (referência) | B (candidata) |
| --- | --- | --- |
| Refatoração | Versão anterior completa | Versão refatorada |
| Skill nova | Execução sem a skill | Execução com a skill |
| Refatoração com controle | A = versão anterior, B = candidata | C = execução sem skill nenhuma: mostra o que a skill acrescenta em cada caso; se C empata com B, a skill não agrega ali |
| Teste de apoio guiado | B | C = mesmo núcleo de B + complemento guided |

**Casos do contexto da skill-alvo.** O fixture fixo mede a skill-refactor; para medir a skill que
está sendo refatorada, os casos vêm dela: um script extrai os invariantes (identidade, literais,
rótulos, proibições, blocos condicionais, idioma) e os defeitos detectáveis; um modelo propõe
pedidos e consultas de acionamento no domínio dela, validados por esquema; uma pessoa aprova o
conjunto, que fica amarrado ao hash do `SKILL.md` de origem. Nada que o modelo escreve vira
verificação objetiva sem passar pelos invariantes extraídos e pela aprovação (no plugin:
`scripts/cases.py`, etapas `--extract`, `--propose`, `--approve`).

**Condições:**
- Compare A com B **dentro de cada modelo** antes de comparar modelos entre si.
- Mesmo caso, contexto e arquivos reiniciados, ordem A/B alternada.
- Nenhum braço recebe a resposta do outro nem a rubrica do avaliador.
- **Esforço igual e registrado.** Comparar runtimes com esforços diferentes compara
  configurações, não modelos. Registre o ID real do modelo, o esforço e sua origem.
- Modelo indisponível é `NOT_RUN`, com o motivo. Nunca invente slugs nem suponha que níveis de
  esforço de fornecedores diferentes sejam equivalentes.

### 10.2 Um componente por vez (ablação)

| Alteração isolada | Hipótese | Regressão possível |
| --- | --- | --- |
| Descrição mais específica | Menos acionamentos indevidos | Perder pedidos legítimos |
| Referências sob demanda | Menor entrada acumulada | Omitir instrução essencial; mais consultas |
| Remoção de repetições | Mesma aderência com menos contexto | Esquecer uma condição |
| Complemento guiado | Menos falhas e retrabalho | Mais latência sem melhora |
| Conclusão mais explícita | Menos paradas prematuras | Trabalho além do escopo |

Mude um componente contra a mesma base, meça, e só então valide a combinação final: alterações que
ajudam isoladas podem interagir.

### 10.3 Acionamento, medido à parte

Testar a skill forçada verifica **execução**, não **descoberta**. Meça acionamento separadamente, no
catálogo real, com pedidos positivos e negativos próximos:

- positivo: "refatore esta SKILL.md";
- negativo: "refatore esta função Python", "use a skill de resumo para resumir esta reunião".

```
precisão  = TP / (TP + FP)      acionou quando devia / todas as vezes que acionou
cobertura = TP / (TP + FN)      acionou quando devia / todas as vezes que devia
```

Uma decisão binária por execução; chamadas repetidas são diagnóstico, não acertos novos.
Denominador vazio é `N/A`, não zero. Descrições mais enfáticas precisam ser testadas **em cada
modelo**. No harness do plugin só o OpenCode expõe a skill por descoberta nativa (`.opencode/skills/`);
Claude Code recebe um plugin gerado e Codex e Hermes um `AGENTS.md` que a nomeia — nesses três, o
acionamento se mede fora do `bench.py`, no catálogo real, com as consultas de `trigger_evals`.

### 10.4 Correção dos artefatos

- Examine os artefatos reais e os passos observáveis, não só a declaração do executor.
- **Uma expectativa testa uma coisa só.** Uma verificação que junta duas observações não diz qual
  delas falhou.
- **A verificação mede a observação, não o idioma nem a redação.** Normalize acentos e aceite o
  vocabulário de todos os idiomas em que a resposta pode vir.
- **Citar uma prática proibida para rejeitá-la é conformidade**, não violação.
- Evidência ausente conta como critério não demonstrado.
- Falhar um requisito obrigatório invalida a tarefa, mesmo com média alta.
- **O status de um run vem do runtime, não do texto da resposta.** Cota, sobrecarga e modelo
  rejeitado contam só com saída diferente de zero ou envelope quebrado, lidos do stderr e dos
  eventos de erro; um agente que *cita* "rate limit" ao explicar a documentação completou o run.
- **O relatório mora onde a skill mandou gravar.** O avaliador lê a área de artefatos ao lado do
  alvo, não só a resposta em chat; senão reprova entregas corretas.
- **Guarde stdout, stderr, artefatos e snapshots de cada run.** O avaliador e o classificador também
  erram; com os runs no disco, uma correção reavalia a rodada sem nova chamada
  (`bench.py --regrade`). Sem isso, cada correção custa uma rodada.
- **Leia a evidência antes de acreditar num veredito.**

### 10.5 Medidas e decisão

| Medida | Definição | Armadilha |
| --- | --- | --- |
| Taxa de aceite | Execuções com todas as expectativas atendidas / execuções iniciadas | `pass_rate` médio não é taxa de aceite |
| **Custo por sucesso** | Custo de **todas** as execuções (inclusive falhas, retentativas, ferramentas, fallback) / sucessos | Sem sucesso, não existe razão finita; execução cortada pelo teto também custou |
| Tempo | Do pedido à conclusão verificada ou falha; p50 e p95; taxa de timeout | Nunca reportar só os sucessos |
| Contexto | Entrada acumulada + pico + referências carregadas + compactações | Tamanho do arquivo não substitui esses dados; convenções de cache variam entre provedores |

**Regra de decisão:** só há ganho com qualidade dentro dos limites fixados antes. Resultado fora de
qualquer limite não é ganho, mesmo que a média melhore. Média e desvio descrevem a amostra; não
provam melhora. Dados insuficientes = **inconclusivo**.

Com três braços, a regra fica concreta, e é escrita **antes** da rodada:

1. aceite da candidata ≥ baseline **em cada modelo** que rodou os mesmos casos;
2. custo por tarefa aceita da candidata ≤ baseline no mesmo modelo;
3. o braço sem skill é controle: se empata ou vence a candidata num caso, a skill não agrega ali
   — um achado, não um ruído;
4. regressão em qualquer modelo → manter a versão anterior e registrar o motivo.

A comparação pareada por caso e modelo (`paired_by_case`) é onde essa regra se aplica; a média
geral por modelo esconde exatamente o que a regra 1 pergunta.

Detalhes de fontes de uso e custo por runtime estão em `references/runtimes.md`.

## 11. Fase 7 — Entrega e registro

### 11.1 Contrato de uma revisão

Toda revisão tem três partes, nesta ordem:

1. **Achados**, cada um nomeado por uma das cinco categorias e com as linhas de origem.
2. **Mudanças propostas**, cada uma ligada ao achado que resolve e ao requisito que preserva.
3. **Como verificar o efeito**: tamanho estático com `tokens.py`, depois A/B com `bench.py`
   decidido pelo custo por tarefa aceita, usando as medidas do protocolo. Métricas inventadas na
   hora ("índice de clareza", "linhas por execução") não são comparáveis com nada.

A revisão diz com clareza o que é diagnóstico estático e o que depende de medição.

### 11.2 Rótulos de evidência

| Rótulo | Quando usar |
| --- | --- |
| `refactored` | O alvo foi alterado |
| `statically validated` | A fase 5 foi concluída |
| `behaviorally evaluated` | A fase 6 rodou; vale **apenas** para os pares (runtime, modelo) executados |

Os rótulos **se acumulam**: a entrega fecha com uma linha nomeando todos os conquistados — uma
refatoração sem benchmark termina `refactored, statically validated`. A redação antiga do núcleo
("`refactored`, `statically validated` **ou** `behaviorally evaluated`") era lida pelos modelos
como escolha, e foi a expectativa mais reprovada na medição de 14/09.

### 11.3 O que a entrega contém

- caminhos alterados;
- perfis usados e como cada um foi resolvido;
- requisitos preservados;
- verificações executadas e resultados observados;
- modelos efetivamente executados e medições disponíveis;
- limites e próximos passos.

Quando houve edição autorizada, grave também um relatório OKF v0.2 fora do núcleo da skill, com
eventos `verified` apenas para verificações realmente feitas e com dados reais: nunca horários ou
aprovações fictícios. Não instale, publique, faça push nem commit sem pedido.

## 12. As dez regras de otimização

Cada regra nomeia a medição que a decide: regra sem medição é opinião.

| # | Regra | Decidida por |
| ---: | --- | --- |
| 1 | **Custo por tarefa aceita, não tamanho** | `cost_per_success_usd` com aceite dentro do limite |
| 2 | **Camadas pagam em frequências diferentes**: descrição → corpo → referências | `tokens.py` por camada e cenário |
| 3 | **Manter, mover, remover** (tabela da [fase 2](#6-fase-2--manter-mover-ou-remover)) | Inventário de requisitos da fase 1 |
| 4 | **Perfil por modelo vem de medição, nunca do nome** | `evals/benchmarks/*/summary.json` |
| 5 | **Uma alteração por vez** (ablação), depois a combinação | Δ por componente contra base fixa |
| 6 | **Acionamento medido à parte da execução** | Precisão e cobertura por modelo |
| 7 | **Contexto é entrada acumulada + pico + referências carregadas** | `usage.context_tokens` e transcrição |
| 8 | **Limites fixados antes de rodar** | Critérios escritos no plano ou no relatório antes da rodada; o `summary.json` grava matriz, esforço e orçamento, não os limites |
| 9 | **Custo completo**: falhas, retentativas e fallback no numerador | `cost_usd` + `cost_source` por execução |
| 10 | **Evidência rotulada por (runtime, modelo)** | Rótulo de entrega |

## 13. Exemplo trabalhado

A skill de exemplo `meeting-summary` é a fixture dos casos de avaliação (`evals/evals.json`). Ela
foi escrita com defeitos de propósito.

### 13.1 Antes

```markdown
---
name: meeting-summary
description: Use for any text, document, message, or information task.     ← (4) ampla demais
paths: ["**/minutes.txt"]
metadata:
  user_extension: "keep-me"                                                 ← campo desconhecido: preservar
---

# Summarize a meeting

Use only supplied content. Never invent decisions, assignees, or dates.     ← requisito obrigatório
Output Key points, Decisions, and Actions. Label missing assignees and dates. ← formato e rótulos exatos
Preserve the editorial note: REVIEW_WINDOW=14.                              ← requisito do usuário

Always read every document before doing any work. Always write a long plan. ← (5) sem finalidade
Always reread this skill. Always explain every tiny step before editing.     ← (5) sem finalidade
Use only supplied content. Never invent decisions, assignees, or dates.     ← (1) duplicado
Output Key points, Decisions, and Actions. Label missing assignees and dates. ← (1) duplicado

## Optional CSV export details currently loaded for every task              ← (3) leitura incondicional
If the user requests CSV export, use columns action, assignee, due_date.
Quote fields containing commas. Preserve dates exactly as supplied.
Missing assignees and dates remain empty cells. Do not export without a request.
Use UTF-8 and include the header row. Preserve accents and source ordering.
Check that parsing the CSV yields the expected columns and row count.
```

### 13.2 Diagnóstico e decisões

| Trecho | Categoria | Decisão |
| --- | --- | --- |
| `description: Use for any text…` | 4. descrição ampla | Reescrever: capacidade + quando usar + quando não usar |
| Linhas "Always…" | 5. procedimento sem finalidade | Remover: nenhum requisito as justifica |
| Duas linhas repetidas | 1. duplicação | Manter uma única vez |
| Seção CSV | 3. leitura incondicional | Mover para `references/csv-export.md`, com condição no núcleo |
| "Never invent…", rótulos, `REVIEW_WINDOW=14` | Requisitos | Manter no núcleo, com a redação exata |
| `name`, `paths`, `user_extension` | Metadados do runtime e do usuário | Preservar sem alteração |

### 13.3 Depois

`SKILL.md`:

```markdown
---
name: meeting-summary
description: Summarize supplied meeting notes into Key points, Decisions and Actions. Use when the
  user shares minutes, a transcript or notes from a meeting and wants a summary; not for general
  text tasks.
paths: ["**/minutes.txt"]
metadata:
  user_extension: "keep-me"
---

# Summarize a meeting

Use only supplied content. Never invent decisions, assignees, or dates.
Output Key points, Decisions, and Actions. Label missing assignees and dates.
Preserve the editorial note: REVIEW_WINDOW=14.

If the user requests CSV export, read references/csv-export.md before exporting.
```

`references/csv-export.md` recebe as regras de CSV, sem perder nenhuma: colunas, aspas, datas,
células vazias, "não exportar sem pedido", UTF-8, cabeçalho e verificação final.

Esta é a **refatoração de referência** usada pelos testes do plugin. Ela atende a todas as
expectativas objetivas do `grade.py`, portanto é `refactored` + `statically validated`. **Não** é
uma saída gerada por modelo nem foi avaliada comportamentalmente.

### 13.4 Efeito medido em tokens (tiktoken `o200k_base`)

| Camada ou cenário | Antes | Depois | Δ |
| --- | ---: | ---: | ---: |
| `description` (paga em toda conversa) | 13 | 39 | **+200%** |
| Corpo, pedido sem CSV (a maioria) | 199 | 68 | **−66%** |
| Corpo + referência, pedido com CSV | 199 | 142 | −29% |

**A leitura correta mostra um trade-off, não uma vitória automática.** O corpo caiu 66% no caso
comum, mas a descrição triplicou, e ela é paga em *toda* conversa, inclusive quando a skill não é
usada. A refatoração só é eficiente se:
- a descrição nova melhorar o acionamento o bastante para compensar os 26 tokens a mais por
  conversa (regra 6, medida por precisão e cobertura); e
- o custo por tarefa aceita cair nos modelos consumidores (regra 1, medida por A/B).

Nenhuma das duas coisas se conclui olhando a tabela. É por isso que a fase 6 existe.

## 14. Lições da validação de 13/09

A metodologia foi aplicada à própria `skill-refactor` e exercitada em 13 modelos de 4 runtimes
(12 com execução concluída), no caso de revisão, com uma repetição cada.
O que a prática ensinou, e que já está incorporado ao protocolo:

| Lição | O que aconteceu | Regra resultante |
| --- | --- | --- |
| **O avaliador mede o idioma, se deixar** | Uma revisão correta em português foi reprovada porque o check procurava "static" | Normalizar acentos; aceitar vocabulário de todos os idiomas |
| **Uma expectativa, uma observação** | Um check juntava "propõe A/B" e "separa estático de medido"; não dava para saber qual tinha falhado | Dividir em expectativas independentes |
| **Citar não é usar** | Um modelo foi reprovado por "métrica inventada" quando estava citando a proibição | Menção em contexto de rejeição não conta |
| **Esforço desigual invalida comparação entre runtimes** | Codex rodou em `low` (configuração do usuário) e Claude em `high`; a vantagem aparente do Codex era parcialmente esforço | Registrar esforço efetivo e sua origem; igualar para comparar runtimes |
| **Execução falha também custa** | Um run cortado pelo teto de US$ 0,75 cobrou US$ 1,05 e tinha sido registrado com custo nulo | Ler custo antes de julgar o código de saída; teto por modelo |
| **Uma repetição é ruído** | O mesmo modelo, com mesmo esforço, deu 7/7 e 6/7 em execuções diferentes | Repetições antes de decidir; 1 run = direção, não conclusão |
| **Omissão se corrige no formato, não com proibição** | Faltava a parte "como medir" nas revisões; a correção foi um formato em três partes, seguindo a orientação do `writing-skills`. O efeito não foi medido em A/B | Para omissões, criar um slot no formato de saída, e medir antes de afirmar que funcionou |
| **Nem todo modelo aproveita o contrato** | O modelo menor continuou inventando métricas mesmo com o contrato no núcleo | Perfil por medição: esse modelo precisa de `guided` ou não serve para a tarefa |
| **A skill também engorda** | Ao ganhar contrato, regras e descoberta, o núcleo da própria `skill-refactor` cresceu 70% | Aplicar a regra 2 a si mesma: medir e mover o que for condicional |
| **Afirmar sem braço de comparação é erro** | Chegamos a afirmar que três modelos "passaram de falha para 7/7" sem nunca tê-los rodado na versão antiga | Só há "antes e depois" quando os dois braços rodaram no mesmo modelo |

## 15. Aplicada a si mesma (14/09/2026)

A `skill-refactor` 0.2.1 foi refatorada com este processo, medindo antes, sem skill e depois
(`skills/skill-refactor/evals/benchmarks/2026-09-14/report.md`):

- **Antes** (rodada 1, 2 reps, Sonnet 5 / Terra / Hermes default / Ling, `medium` no Claude e no
  Codex, 47/48 runs, US$ 7,58): na revisão a skill decide — 7/8 aceitos contra 0/8 sem skill; nas
  edições o aceite era raro nos dois braços, e a expectativa mais reprovada **com** a skill era o
  rótulo de entrega, porque o próprio texto dizia "`refactored`, `statically validated` **ou**
  `behaviorally evaluated`". Segundo motivo: a regra de guarda do CSV se perdia ao mover o bloco.
- **Mudança** (0.3.0): núcleo 1 258 → 998 tokens (−21 %), descrição intacta, contrato de revisão e
  *Measure* movidos para referências condicionais, mais as duas correções que a medição apontou.
- **Depois** (rodada 2a, 1 rep, três braços): candidata ≥ baseline em todo modelo que rodou
  (Claude 3/3 × 2/3; OpenCode 3/3 × 2/3; Codex sem regressão nos casos que a cota permitiu);
  `no_skill` 0/8. Custo por tarefa aceita no Claude 0,45 × 0,66. Rótulo honesto: `behaviorally
  evaluated` com uma repetição — direção com controle, não prova.
- **O que o processo ensinou:** três defeitos do harness só apareceram com dinheiro gasto (cota
  citada em texto virando `NOT_RUN`, relatório na área de artefatos que o avaliador não lia, erro
  de conexão virando `FAIL`). Regradar a partir do disco (`bench.py --regrade`) evitou pagar de
  novo — deixe o harness capaz disso antes da primeira rodada cara.

## 16. Anti-padrões

| Anti-padrão | Por que é problema | Faça em vez disso |
| --- | --- | --- |
| Cortar texto até atingir um número de linhas | Remove requisitos junto | Decidir trecho a trecho pela tabela da fase 2 |
| Mover tudo para referências | Referência lida sempre custa igual e soma consulta | Mover só o que tem condição de leitura real |
| Uma cópia da skill por modelo | As cópias divergem | Um núcleo + apoio `guided` condicional |
| Escolher perfil pelo nome do modelo | Nome não prova necessidade | Medir `lean` × `guided` no modelo |
| Proibições em sequência ("não faça X, não faça Y") para corrigir formato | Modelos negociam com proibições | Descrever o formato esperado (receita) |
| Declarar ganho por redução de tokens | Tamanho não é custo por tarefa | A/B por modelo, com limites fixados antes |
| Comparar runtimes com esforços diferentes | Compara configurações | Igualar e registrar o esforço |
| Mudar várias coisas e medir uma vez | Não se sabe o que ajudou | Ablação, depois a combinação |
| Confiar no veredito do avaliador sem ler a evidência | Falsos negativos parecem defeito do modelo | Ler `evidence` de toda falha |
| Declarar `behaviorally evaluated` para modelos não executados | Afirmação sem dado | Rótulo por par (runtime, modelo) |

## 17. Checklist final

**Preparação**
- [ ] Alvos, resultado, perfis e local de artefatos registrados
- [ ] Revisão ou refatoração deixada explícita
- [ ] Baseline preservado (refatoração)

**Diagnóstico**
- [ ] Gatilhos, requisitos, formato, permissões, dependências e conclusão mapeados
- [ ] Cada achado nomeado por categoria, com as linhas

**Refatoração**
- [ ] Descrição com capacidade, quando usar e quando não usar
- [ ] Nenhum requisito obrigatório depende de referência opcional
- [ ] Toda referência tem condição de leitura explícita
- [ ] Repetições consolidadas; metadados e campos desconhecidos preservados
- [ ] Cada trecho movido ou removido mapeado para a regra que o substitui; bloco movido levou suas guardas
- [ ] Idioma e rótulos exatos preservados

**Perfis**
- [ ] Perfil de cada consumidor resolvido e justificado (pedido, medição ou padrão `guided`)
- [ ] Um núcleo só; apoio `guided` condicional quando necessário

**Verificação**
- [ ] Frontmatter validado pela plataforma-alvo
- [ ] Links relativos resolvem; sem caminhos pessoais
- [ ] Diff restrito ao escopo autorizado
- [ ] `tokens.py --baseline` por camada e cenário

**Avaliação (se autorizada)**
- [ ] Casos, rubrica, modelos, esforço, orçamento e limites congelados antes
- [ ] A/B dentro de cada modelo; esforço igual e registrado
- [ ] Braço sem skill quando a pergunta inclui "a skill agrega alguma coisa?"
- [ ] Acionamento medido à parte
- [ ] Evidência de toda falha lida antes de aceitar o veredito; status vindo do runtime, não do texto
- [ ] Runs guardados no disco para reavaliar sem pagar de novo
- [ ] Decisão por custo por tarefa aceita dentro dos limites, por modelo; repetições suficientes

**Entrega**
- [ ] Revisão em três partes (achados, mudanças, como medir)
- [ ] Rótulos de evidência corretos, por par (runtime, modelo)
- [ ] Relatório OKF com dados reais (se houve edição)
- [ ] Nada instalado, publicado ou commitado sem pedido
