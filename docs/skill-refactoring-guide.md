---
okf_version: "0.2"
type: guide
title: "Refatoração de skills entre modelos e runtimes"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:30:36Z"
  description: "Revisão genérica com estratégias do skill-creator da Anthropic e adequação ao OKF v0.2."
provenance:
  actor: "agent:codex"
  created_at: "2026-09-12"
  updated_at: "2026-09-14"
  updated_by: "agent:claude"
lifecycle:
  status: reviewed
  scope: "Guia genérico de refatoração e avaliação de skills em diferentes modelos e runtimes."
sources:
  - resource: "https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra"
  - resource: "https://developers.openai.com/api/docs/guides/evaluation-best-practices"
  - resource: "https://developers.openai.com/api/docs/guides/prompt-caching"
  - resource: "https://claude.com/plugins/skill-creator"
    title: "Skill Creator Plugin — Claude by Anthropic"
  - resource: "Anthropic skill-creator / SKILL.md"
    version: "Plugin claude-plugins-official, versão local instalada consultada em 2026-09-12"
    references: ["references/schemas.md", "agents/grader.md", "agents/analyzer.md"]
  - resource: "plugins/pwdev-skills/docs/metodologia-de-refatoracao.md"
    context: "Metodologia exercitada em 2026-09-13; a revisão de 2026-09-14 incorpora o que a prática ensinou."
  - resource: "https://opencode.ai/docs/zen/"
    context: "Política de retenção de dados dos modelos gratuitos usados em benchmark."
verified:
  - by: "agent:codex"
    at: "2026-09-12T23:31:17Z"
    result: pass
    description: "Verificação textual e revisão independente da adaptação. Nenhum benchmark executado."
  - by: "agent:claude"
    at: "2026-09-14"
    result: pass
    description: "Artigo da OpenAI reconferido (citações corretas; sem benchmarks). Guia exercitado em 2026-09-13 com 13 modelos de 4 runtimes (12 concluídos), 1 caso, 1 repetição. SHAs de proveniência do plugin pwdev-skills atualizados; testes do plugin verdes. Nenhum validador OKF foi executado: o repositório não possui um."
verification:
  events:
    - type: manual-review
      result: pass
      description: "2026-09-12: revisão metodológica com segunda leitura; corrigidas unidades de roteamento, custo agregado e sucesso sem recuperação. Não constitui benchmark."
    - type: manual-review
      result: pass
      description: "2026-09-14: enquadramento neutro quanto a modelos; custo por camada; esforço efetivo e exposição por runtime; regras do avaliador; execução cortada por teto; exemplo antes/depois medido. Sem benchmark novo."
---

# Refatoração de skills entre modelos e runtimes

## Objetivo e fundamento

Orientar a refatoração de skills compartilhadas por modelos com necessidades
diferentes de orientação, em runtimes que expõem a skill de formas diferentes.
Os exemplos são genéricos e podem ser adaptados a outros agentes, ferramentas e
domínios.

O [artigo da OpenAI sobre skills e prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
recomenda descrições curtas e específicas, carregamento progressivo de referências,
regras contextuais no `AGENTS.md` e critérios claros de conclusão. Também alerta
que instruções úteis para um modelo podem restringir outro em excesso. Trate isso
como uma propriedade geral: o mesmo texto tem custo e efeito diferentes em cada
modelo, e só a medição diz qual.

O artigo não apresenta benchmarks que permitam concluir que remover determinada
regra sempre melhora o resultado. Trate suas recomendações como hipóteses a
validar em tarefas representativas.

O método incorpora estratégias do `skill-creator` da Anthropic para Claude:
rascunho, casos reais, comparação com uma referência, avaliação dos artefatos,
feedback humano e iteração. Foram consultados o `SKILL.md` e suas referências
de schemas, correção e análise da versão instalada em 2026-09-12. Os perfis
por modelo e o protocolo estatístico são adaptações deste guia.

Este guia foi exercitado em 2026-09-13 pela skill `skill-refactor` (plugin
`pwdev-skills`): 13 modelos de 4 runtimes, 12 com execução concluída, um caso, uma
repetição. A [metodologia do plugin](../plugins/pwdev-skills/docs/metodologia-de-refatoracao.md)
descreve o processo passo a passo e o que a prática ensinou; a revisão de
2026-09-14 deste guia incorpora essas lições.

## Compatibilidade por comportamento

Neste guia, “modelos que precisam de mais orientação” substitui “modelos inferiores”.
A necessidade de estrutura depende da tarefa, das ferramentas e da configuração;
o nome do modelo, isoladamente, não demonstra uma limitação.

Mantenha o mesmo contrato de qualidade para todos. Ajuste o suporte oferecido para
atingi-lo, preservando segurança, escopo autorizado e critérios de aceitação.

| Aspecto | Perfil enxuto (`lean`) | Perfil guiado (`guided`) |
| --- | --- | --- |
| Planejamento | Objetivo, restrições e resultado esperado | Sequência curta com entregáveis intermediários |
| Exemplos | Casos com ambiguidade relevante | Exemplo resolvido e erro comum observado |
| Verificação | Critérios e comandos aplicáveis | Checklist com interpretação de sucesso e falha |
| Ferramentas | Contrato e limites de uso | Exemplos de chamadas e recuperação de erros conhecidos |
| Conclusão | Evidência esperada e ponto de parada | Conferência explícita de itens pendentes |
| Aprovação | Limites definidos pela governança | Os mesmos limites, com situações exemplificadas |

Um perfil é uma configuração de partida, não um ranking de modelos nem um nível
de permissão. A escolha segue esta ordem:

```
o pedido nomeia um perfil? ── sim ──▶ usar o do pedido (seleção explícita sempre vence)
        │ não
        ▼
existe medição para esse modelo   ── sim ──▶ perfil com menor custo por tarefa aceita
(A/B lean × guided, mesmos casos)?           dentro do limite de qualidade
        │ não
        ▼
     guided
```

Uma família de modelo citada num pedido ("modelo X em lean") é roteamento daquele
pedido, não um padrão do guia. Não deduza a identidade do modelo pelo estilo da
resposta, nem escolha o perfil pelo nome: o perfil vem do pedido ou da medição.

## Estrutura sugerida

Use apenas os arquivos necessários à skill; esta árvore é ilustrativa:

```text
nome-da-skill/
├── SKILL.md
├── references/
│   ├── workflow.md
│   └── guided.md
├── scripts/
└── assets/
```

Os metadados (`name` e `description`) permitem descobrir a skill; o corpo do
`SKILL.md` é lido após a seleção; referências, scripts e assets entram conforme
a tarefa. Esses três níveis ajudam a separar descoberta de execução.

O `SKILL.md` contém resultado esperado, limites essenciais e roteamento.
`workflow.md` documenta detalhes específicos do domínio. `guided.md` acrescenta
suporte ao perfil guiado. Scripts existentes podem executar validações determinísticas;
assets podem conter modelos de saída.

O complemento guiado deve referenciar o contrato central. Evite manter cópias
completas da mesma skill para cada modelo: elas podem divergir com o tempo.

Explique a razão das instruções que exigem julgamento. Quando diferentes casos
levarem o agente a recriar o mesmo código auxiliar, considere incluí-lo em
`scripts/` e meça o efeito. Um recurso compartilhado pode evitar trabalho repetido.

## Custo por camada

Uma skill não é carregada de uma vez. Cada camada entra no contexto com uma
frequência diferente, e é essa frequência que define onde otimizar primeiro:

| Camada | Entra no contexto | Custo |
| --- | --- | --- |
| `description` (frontmatter) | Em **toda** conversa, no catálogo de skills | Pago sempre, mesmo quando a skill não é usada |
| Corpo do `SKILL.md` | A cada **ativação** da skill | Pago por uso |
| `references/*.md` | Só quando a **condição** de leitura é atendida | Pago quando necessário |
| `scripts/`, `assets/` | Executados ou copiados, não lidos | Aproximadamente zero contexto |

Consequências:

- Um token na `description` custa mais que um token no corpo. Otimize nesta ordem:
  descrição, corpo, referências. Uma descrição mais longa pode ser o preço de um
  acionamento correto, mas esse aumento precisa ser justificado por medição de
  acionamento, porque é pago em toda conversa.
- Mover para uma referência só economiza se a condição de leitura for real. Uma
  referência que todo pedido acaba lendo custa o mesmo e ainda soma uma consulta.
- O custo real de uma execução não é o tamanho do arquivo: é a entrada acumulada
  ao longo dos turnos (tokens frescos, cache lido e cache gravado), mais a saída,
  mais as referências efetivamente abertas. A contagem estática diagnostica; só a
  execução mede.

## O que manter, mover e remover

| Conteúdo encontrado | Tratamento sugerido |
| --- | --- |
| Limite de autorização ou proteção de dados | Manter explícito e acessível antes da ação relevante |
| Regra de negócio ou formato obrigatório | Manter no contrato ou referência obrigatória do fluxo |
| Requisito obrigatório que só aparece numa referência opcional | Trazer para o núcleo, ou tornar a leitura inevitável no fluxo em que a regra se aplica |
| Procedimento específico de uma ferramenta | Mover para referência carregada ao usar essa ferramenta |
| Explicação extensa para um erro recorrente | Mover para o perfil guiado, com cenário de avaliação |
| Mesma regra repetida em vários arquivos | Eleger uma fonte e referenciá-la |
| Obrigação universal de ler documentos | Substituir por condições concretas de leitura |
| Adjetivos como “excelente” e “perfeito” | Substituir por critérios observáveis |
| Regra sem finalidade identificável | Investigar sua origem e testar a remoção |

A regra que se sobrepõe a todas: nenhum requisito obrigatório pode depender de uma
referência que o agente talvez não leia.

Não reduza o texto removendo requisitos necessários à correção. Também não
transfira tudo para referências que continuem sendo carregadas obrigatoriamente
em todas as tarefas: isso mantém o custo de contexto.

## Exemplo trabalhado

A skill de exemplo abaixo foi escrita com defeitos de propósito. Ela é a fixture
dos casos de avaliação da `skill-refactor`; cada defeito está anotado com a
categoria de diagnóstico correspondente.

Antes:

```markdown
---
name: meeting-summary
description: Use for any text, document, message, or information task.     ← descrição ampla demais
paths: ["**/minutes.txt"]
metadata:
  user_extension: "keep-me"                                                 ← campo do usuário: preservar
---

# Summarize a meeting

Use only supplied content. Never invent decisions, assignees, or dates.     ← requisito obrigatório
Output Key points, Decisions, and Actions. Label missing assignees and dates. ← formato e rótulos exatos
Preserve the editorial note: REVIEW_WINDOW=14.                              ← requisito do usuário

Always read every document before doing any work. Always write a long plan. ← procedimento sem finalidade
Always reread this skill. Always explain every tiny step before editing.     ← procedimento sem finalidade
Use only supplied content. Never invent decisions, assignees, or dates.     ← duplicação
Output Key points, Decisions, and Actions. Label missing assignees and dates. ← duplicação

## Optional CSV export details currently loaded for every task              ← leitura incondicional
If the user requests CSV export, use columns action, assignee, due_date.
Quote fields containing commas. Preserve dates exactly as supplied.
Missing assignees and dates remain empty cells. Do not export without a request.
Use UTF-8 and include the header row. Preserve accents and source ordering.
Check that parsing the CSV yields the expected columns and row count.
```

Diagnóstico e decisões:

| Trecho | Categoria | Decisão |
| --- | --- | --- |
| `description: Use for any text…` | Descrição ampla | Reescrever: capacidade, quando usar, quando não usar |
| Linhas “Always…” | Procedimento sem finalidade | Remover: nenhum requisito as justifica |
| Duas linhas repetidas | Duplicação | Manter uma única vez |
| Seção CSV | Leitura incondicional | Mover para `references/csv-export.md`, com condição no núcleo |
| “Never invent…”, rótulos, `REVIEW_WINDOW=14` | Requisitos | Manter no núcleo, com a redação exata |
| `name`, `paths`, `user_extension` | Metadados do runtime e do usuário | Preservar sem alteração |

Depois (`SKILL.md`; as regras de CSV vão para `references/csv-export.md` sem perder
nenhuma):

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

Efeito medido em tokens (tiktoken `o200k_base`):

| Camada ou cenário | Antes | Depois | Variação |
| --- | ---: | ---: | ---: |
| `description` (paga em toda conversa) | 13 | 39 | +200% |
| Corpo, pedido sem CSV (a maioria) | 199 | 68 | −66% |
| Corpo + referência, pedido com CSV | 199 | 142 | −29% |

A tabela mostra um trade-off, não uma vitória: o corpo caiu 66% no caso comum, mas
a descrição triplicou, e ela é paga mesmo quando a skill não é usada. A refatoração
só é eficiente se a descrição nova melhorar o acionamento o bastante para compensar
os tokens a mais por conversa, e se o custo por tarefa aceita cair nos modelos
consumidores. Nenhuma das duas coisas se conclui olhando a tabela; é para isso que
existe a avaliação entre modelos. Esta versão “depois” é a refatoração de referência
usada nos testes do plugin: está validada estaticamente, não foi gerada por modelo
nem avaliada comportamentalmente.

Na avaliação de acionamento, inclua pedidos em que a skill deve e não deve
disparar. A descrição revisada distingue uma síntese de reunião de uma tradução
ou revisão gramatical do mesmo documento.

## Modelo de SKILL.md

Adapte a linguagem ao público e mantenha `name` e `description` no frontmatter.
Este exemplo não depende de um framework; os caminhos são ilustrativos.

````markdown
---
name: resumo-estruturado
description: Resuma documentos ou transcrições em pontos principais, decisões e pendências quando o usuário pedir uma síntese estruturada.
---

# Resumo estruturado

## Resultado

Produza uma síntese fiel com pontos principais, decisões e pendências.
Associe decisões e ações aos trechos que as sustentam.

## Fidelidade

Use apenas o material fornecido. Sinalize responsáveis ou prazos ausentes:
inferi-los pode transformar uma hipótese em um compromisso inexistente.

## Referências

Leia references/workflow.md se houver ambiguidade entre proposta e decisão.
Leia references/guided.md quando o perfil guiado estiver selecionado.

## Conclusão

Confira a síntese contra o material original e entregue as três seções.
Se uma seção não tiver informações, sinalize isso sem inventar conteúdo.
Informe lacunas que impeçam uma síntese confiável.
````

Um complemento guiado poderia mostrar como distinguir uma sugestão de uma
decisão e incluir um exemplo de ação sem responsável definido. Ele deve
preservar o resultado esperado e os critérios de fidelidade do núcleo.

## Autonomia e conclusão

Descreva quais operações estão autorizadas e quais decisões exigem participação
humana. Uma autorização para implementar deve indicar se inclui executar a
aplicação, verificar o resultado e corrigir falhas relacionadas à mudança.

Exemplo de instrução para uma tarefa de síntese:

```text
Leia o material fornecido, prepare a síntese e confira as afirmações nas fontes.
Corrija omissões ou contradições identificadas nessa conferência.
Entregue o resumo e indique as lacunas que permanecerem.
Solicite esclarecimento se faltar material essencial para atender ao pedido.
```

Adapte o ponto de parada à tarefa e respeite as autorizações do ambiente.

## Procedimento de refatoração

0. Registre o que precisa continuar verdadeiro depois da mudança: gatilhos legítimos
   (inclusive formulações que não citam a skill), requisitos obrigatórios, formato e
   rótulos exatos, permissões, dependências (referências, scripts, campos do runtime e
   do usuário) e condições de conclusão. Essa lista é a matriz de verificação final.
1. Escolha uma skill e registre seu comportamento esperado, consumidores e comandos existentes.
2. Separe requisitos de domínio, limites de autorização e apoio procedural.
3. Diagnostique por categoria, apontando as linhas de origem: duplicação (a mesma regra
   em mais de um lugar), contradição (núcleo e referência discordam), leitura
   incondicional (referência carregada em todo pedido), descrição ampla ou restrita
   demais (dispara em tarefas alheias ou não dispara em pedidos legítimos) e
   procedimento sem finalidade (passo que nenhum requisito ou resultado explica).
4. Prepare cenários, rubrica de qualidade, orçamento e limites de decisão antes de alterar as instruções.
5. Enxugue a descrição e o núcleo; extraia detalhes realmente condicionais.
6. Acrescente apoio guiado apenas onde houver necessidade demonstrada ou já conhecida.
7. Compare a versão anterior e a candidata com o protocolo de eficiência abaixo.
8. Revise os artefatos com o usuário, generalize o feedback e avalie novamente a revisão.

Faça a primeira comparação com uma skill de escopo bem delimitado. Preserve a
versão anterior para permitir comparação e reversão.

## Ciclo prático inspirado no skill-creator

Comece com 2–3 pedidos reais para encontrar problemas rapidamente. Por exemplo,
para a skill acima: sintetizar uma reunião com decisões explícitas; resumir
anotações em que propostas foram rejeitadas; organizar pendências sem prazos.
Use entradas fixas e resultados esperados. Depois amplie a amostra para avaliar
eficiência e generalização.

1. **Preserve a referência.** Para refatoração, congele a versão anterior com seus
   recursos. Para uma skill nova, compare com a execução sem essa skill, mantendo
   as demais instruções do ambiente. Sem skill é um controle adicional opcional
   na refatoração, não substitui a comparação com a versão anterior.
2. **Execute candidata e referência.** Use o mesmo pedido e entradas em sessões
   isoladas. Salve o artefato que o usuário realmente consumirá e o registro dos
   passos da execução. Capture tempo e tokens quando o runtime os disponibilizar.
3. **Avalie conteúdo e evidência.** Verifique expectativas objetivas e inspecione
   os arquivos produzidos. Para estilo ou utilidade, use julgamento humano com
   critérios claros. A presença de um arquivo não demonstra conteúdo correto.
4. **Apresente resultados para revisão.** Mostre pedido, artefatos, métricas e
   feedback por caso. Uma comparação sem revelar a variante reduz influência
   da preferência pelo modelo. Se usar um avaliador automatizado, alterne a
   ordem das saídas e revise discordâncias.
5. **Analise os passos, além da saída.** Procure leituras inúteis, buscas repetidas,
   ferramentas mal utilizadas e código auxiliar recriado. Registre observações
   separadamente das hipóteses de causa; teste a hipótese na próxima versão.
6. **Generalize e repita.** Corrija o padrão que produziu o erro, explique a razão
   da orientação e rode os casos novamente em outra iteração. Evite instruções
   que apenas memorizem a resposta de um exemplo. Leve novos casos à validação final.

Exemplo de expectativa fraca: “O resumo contém uma seção de decisões”. Uma
expectativa mais útil: “A seção inclui as decisões confirmadas na entrada e não
apresenta propostas rejeitadas como decisões”. Registre resultado e evidência
para cada expectativa; examine também resultados importantes não cobertos por elas.

Esse ciclo é para desenvolvimento. A comparação final usa rubrica e limites
congelados antes da execução; critérios descobertos depois passam a compor uma
nova avaliação. O piloto não substitui a amostra necessária à decisão.

## Avaliação entre modelos

A refatoração é eficiente quando reduz o recurso que importa ao projeto e mantém
o resultado exigido. Defina uma métrica principal, como custo por tarefa aceita
ou tempo até a entrega verificada, e limites para as demais. O tamanho do
`SKILL.md` é apenas um diagnóstico: uma skill curta pode causar mais consultas,
retentativas e correções que uma versão longa.

A documentação de [boas práticas de avaliação da OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
orienta usar tarefas representativas, critérios explícitos e avaliação humana
para calibrar a pontuação automatizada. O protocolo a seguir adapta esse princípio
e o ciclo do skill-creator para diferentes modelos e ambientes de execução.

### 1. Defina a unidade de comparação

Um **caso** é um pedido com contexto inicial e resultado esperado. Uma **execução**
é uma tentativa completa de resolver esse caso, incluindo chamadas de ferramentas
e retentativas previstas. Repetições do mesmo caso são novas execuções, com estado
reinicializado; não são casos independentes adicionais.

Compare três variantes: A, skill atual; B, núcleo refatorado enxuto; C, o mesmo
núcleo com complemento guiado. Execute A contra a candidata em cada modelo
suportado. Use B e C no mesmo modelo quando precisar investigar o efeito do
complemento. Não atribua ao texto uma melhora obtida ao trocar simultaneamente
modelo, esforço de raciocínio e ferramentas.

Primeiro meça a refatoração com a configuração do modelo fixa. Depois, em um
experimento separado, ajuste modelo e esforço para encontrar uma combinação
mais econômica que cumpra os mesmos critérios. O mesmo nome de nível de esforço
em dois modelos não garante o mesmo orçamento de computação.

Registre o esforço efetivo de cada execução e a origem do valor. Cada runtime
tem um padrão próprio, definido na configuração do usuário ou embutido na
ferramenta, e esses padrões não coincidem entre si. Uma comparação entre
runtimes com esforços diferentes compara configurações, não modelos; iguale o
esforço antes de comparar, ou declare a diferença junto com o resultado. O mesmo
vale para o modelo: registre o identificador que o runtime informa ter usado, e
marque como desconhecido o que ele não informa.

### 2. Monte a amostra e a rubrica

Separe casos usados para ajustar a skill de um conjunto reservado para a
comparação final. Inclua tarefas simples e complexas, casos reais sanitizados e
os cenários abaixo. Registre a frequência esperada de cada categoria para evitar
que uma maioria de casos fáceis esconda regressões nos difíceis.

| Cenário | Resultado esperado |
| --- | --- |
| Pedido claramente dentro do escopo | Aciona a skill e cumpre o contrato |
| Pedido próximo, mas fora do escopo | Evita acionamento indevido |
| Tarefa simples | Carrega somente referências aplicáveis |
| Tarefa com informação essencial ausente | Identifica a lacuna e solicita a decisão necessária |
| Falha em uma ferramenta | Relata a falha e usa recuperação autorizada quando disponível |
| Ação além do escopo autorizado | Interrompe a ação e explicita a decisão pendente |
| Trabalho aparentemente pronto | Confere os critérios e informa a evidência real |

Para cada caso, defina antes da execução: acionamento esperado, critérios
obrigatórios, comportamento permitido, evidência de sucesso e término correto.
Uma pergunta necessária pode ser a resposta correta de um caso de esclarecimento;
uma interrupção prematura não satisfaz um caso de implementação completa.

Mantenha uma avaliação específica da descrição, além dos testes de execução.
O skill-creator propõe cerca de 20 consultas de acionamento, combinando pedidos
que precisam da skill com casos próximos que usam as mesmas palavras, mas pedem
outro trabalho. No exemplo, resumir uma transcrição é positivo; traduzir a mesma
transcrição sem síntese é negativo. Inclua variações naturais de linguagem e
valide os rótulos antes de otimizar a descrição.

A versão consultada sugere descrições mais enfáticas para combater o baixo
acionamento observado no Claude. Trate essa orientação como hipótese específica
do ambiente: explicite situações legítimas de uso, sem ampliar indiscriminadamente
o escopo compartilhado. Compare falsos positivos e falsos negativos em cada modelo.
Não suponha que uma descrição otimizada em um modelo terá o mesmo efeito em outro.

#### Regras do avaliador

O avaliador é parte do experimento e também erra. Na validação de 2026-09-13,
quatro falsos negativos vieram de verificações que mediam a redação, não a
observação. Regras que evitam isso:

- Uma expectativa testa uma coisa só. Uma verificação que junta duas observações
  não diz qual delas falhou.
- A verificação mede a observação, não o idioma nem a redação. Normalize acentos e
  aceite o vocabulário de todos os idiomas em que a resposta pode vir; uma revisão
  correta em português não pode ser reprovada por não conter a palavra inglesa.
- Citar uma prática proibida para rejeitá-la é conformidade, não violação.
- Evidência ausente conta como critério não demonstrado.
- Leia a evidência de toda falha antes de aceitar o veredito. Uma reprovação não é,
  automaticamente, defeito do modelo.
- Uma execução é direção, não decisão. O mesmo modelo, com o mesmo esforço, produziu
  resultados diferentes em execuções consecutivas; repita antes de concluir.

Se o conjunto reservado orientar repetidamente a escolha da melhor descrição,
ele funciona como validação de desenvolvimento. Preserve um conjunto final ainda
não usado nas escolhas para sustentar a alegação de generalização.

Use testes, schemas e verificações determinísticas onde houver um resultado
objetivo. Para julgamento editorial ou técnico, use rubrica fixa e revisão
humana sem identificação da variante. Um modelo avaliador pode auxiliar, desde
que calibrado com exemplos revisados por humanos; não use a autoavaliação do
executor como prova de sucesso. Registre a versão da rubrica e do avaliador.

Um piloto ilustrativo pode ter 12 casos distintos e 3 repetições por variante
em cada modelo. Isso detecta problemas grosseiros e estima o custo do experimento;
não demonstra superioridade nem estabilidade de percentis altos. Dimensione a
avaliação final pela variabilidade observada, diversidade dos casos e menor
diferença que justificaria a mudança.

### 3. Controle as condições

- Fixe versões da skill e suas referências, modelo, runtime, `AGENTS.md`, ferramentas,
  dados, limites de tokens, timeout, retentativas e concorrência.
- Pareie A e a candidata pelo mesmo caso e contexto. Alterne ou sorteie a ordem
  das variantes para reduzir efeitos de horário, carga e aquecimento.
- Reinicie conversa, memória e fixtures entre execuções; impeça que B reutilize
  soluções ou arquivos produzidos por A. Use o mesmo catálogo de skills nas duas
  variantes, pois a seleção depende das descrições concorrentes.
- Para tarefas interativas, use respostas humanas previamente definidas ou registre
  a intervenção real. Separe espera pelo usuário de tempo ativo do agente.
- Classifique falhas externas com critérios prévios. Preserve tentativas falhas e
  seus custos; apresente resultados brutos e eventual recorte sem incidentes externos.
- Registre como cada runtime recebe a skill. Um runtime pode carregá-la por um plugin
  gerado, outro por instruções em `AGENTS.md`, outro por descoberta nativa no seu
  catálogo. Só a descoberta nativa mede acionamento real; nas demais, o teste mede
  execução com a skill disponível. Precisão e cobertura entre runtimes só são
  comparáveis quando a forma de exposição é a mesma ou está declarada.
- Não edite a skill enquanto uma rodada estiver em andamento. O runtime recebe uma
  cópia e não vê a edição, mas o resultado passa a descrever um alvo em movimento.
  Registre qualquer alteração na fonte durante a rodada e refaça depois que as
  edições terminarem.

Execuções paralelas são úteis quando os ambientes são isolados e a disputa por
recursos é controlada. Execuções sequenciais também permitem comparação válida
com as mesmas condições. A existência de subagentes não é um requisito estatístico.

Cache merece uma comparação própria. A documentação de
[prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
explica que reutilizar prefixos pode alterar custo e latência. Meça condições
sem reaproveitamento e com reaproveitamento, quando controláveis, e registre os
acertos observados. Uma conversa nova não garante cache frio. Se o runtime não
expuser esses dados, registre a limitação e evite atribuir a diferença ao cache.

### 4. Meça o trabalho completo

| Dimensão | Medida e interpretação |
| --- | --- |
| Qualidade | Execuções aceitas / execuções iniciadas; informe também sucesso sem recuperação ou correção adicional dentro da execução e falhas por categoria |
| Custo por resultado | Custo total de todas as execuções / quantidade de execuções aceitas, no mesmo conjunto de casos |
| Latência | Tempo do pedido ao término verificado ou falha; reporte p50 e, com amostra suficiente, p95, mais taxa de timeout |
| Contexto | Tokens de entrada acumulados e pico por chamada, saída, referências efetivamente carregadas e compactações |
| Retrabalho | Retentativas, correções, chamadas repetidas e minutos de intervenção humana por execução |
| Roteamento | Uma decisão binária por execução: precisão = TP / (TP + FP); cobertura = TP / (TP + FN), por variante e modelo |

Nos relatórios do skill-creator, `pass_rate` representa a fração de expectativas
atendidas. Mostre essa medida separada da taxa de execuções aceitas: cumprir nove
de dez expectativas não conclui a tarefa quando a décima é obrigatória. Examine
expectativas que sempre passam nas duas variantes, falham nas duas ou variam
muito; elas podem revelar verificações pouco úteis ou problemas na tarefa.
Média e desvio padrão ajudam a descrever as execuções, mas não substituem uma
medida de incerteza da diferença entre variantes.

No roteamento, TP é execução que exigia a skill e a acionou; FP é execução que
não a exigia e a acionou; FN é execução que a exigia e não a acionou. Conte
acionamentos repetidos dentro da mesma execução como diagnóstico separado.

Mostre quantidade de observações e denominadores. Se não houver sucesso, custo
por resultado não tem valor finito; se não houver acionamentos, a precisão é
indefinida. Use `N/D` com motivo, nunca zero para informação ausente.

Some o custo de todas as chamadas do executor, ferramentas pagas e subagentes,
incluindo retentativas. Use categorias de cobrança sem sobreposição: entrada
comum, leitura ou gravação de cache quando aplicáveis e saída conforme o provedor.
Tokens de raciocínio podem já estar incluídos na saída; não os cobre novamente.
Registre moeda, tabela de preços e data. Não converta tokens em dinheiro quando
o ambiente não fornecer dados suficientes; apresente consumo observado.

As convenções de contagem diferem entre provedores: um pode reportar a entrada já
incluindo os tokens servidos do cache, outro reporta a entrada líquida e o cache à
parte. Normalize para uma forma única (entrada fresca, cache lido, cache gravado,
saída) antes de somar ou comparar, ou a mesma execução terá dois custos.

Uma execução cortada por teto de custo cobra sem entregar. Registre o valor gasto
mesmo quando não houver resposta e classifique a execução como não executada, não
como falha da skill: um teto atingido não diz nada sobre a skill. Dimensione o teto
pela taxa do modelo mais caro da rodada, não pela conta do mais barato; o teto por
execução de um modelo pode ser várias vezes o custo total de outro.

Registre separadamente o custo de avaliar as respostas e o esforço humano. Se a
operação real usar um verificador ou fallback, inclua esses componentes no custo
operacional e reporte a taxa de escalonamento. Um modelo barato que frequentemente
recorre a um modelo caro deve ser avaliado pelo custo do fluxo inteiro.

Apresente latência de todas as execuções e dos sucessos separadamente. Timeouts
entram no relatório pelo tempo consumido, identificados como incompletos; não
representam tempo de conclusão. Com ferramentas paralelas, use tempo de parede
para a experiência do usuário e soma de recursos para o custo.

Tokens de entrada acumulados medem processamento ao longo da tarefa; o pico mede
pressão sobre a janela de contexto. Registre também a parte atribuível à skill
quando observável. Reduzir arquivos lidos ou chamadas de ferramentas só é um ganho
se a qualidade continuar atendida.

### 5. Descubra quais mudanças ajudam

Faça uma ablação: altere um componente por vez e compare com a mesma base.
Priorize uma hipótese concreta; não é necessário executar todas as combinações.

| Alteração isolada | Hipótese a testar | Possível regressão |
| --- | --- | --- |
| Descrição mais específica | Menos acionamentos indevidos | Perder pedidos legítimos |
| Referências sob demanda | Menor entrada acumulada | Mais buscas ou omissão de instrução essencial |
| Remoção de repetições | Menor contexto com mesma aderência | Esquecer condição importante |
| Complemento guiado | Menos falhas e retrabalho | Mais latência sem melhora de resultado |
| Conclusão mais explícita | Menos interrupções prematuras | Trabalho além do escopo |

Depois valide a combinação final, porque alterações que ajudam isoladamente
podem interagir. Meça também no catálogo real de skills: um teste com a skill
forçada verifica execução, mas não verifica descoberta e seleção.

### 6. Tome a decisão com limites prévios

Defina piso de qualidade, regressão máxima aceitável, ganho mínimo relevante na
métrica principal e limites de custo, latência e intervenção humana antes de
examinar a comparação final. Use pontos percentuais para diferenças de taxa de
sucesso e porcentagens para reduções relativas de custo ou tempo.

Informe diferenças entre variantes e uma medida de incerteza, preservando o
pareamento por caso. Quando usar bootstrap, reamostre casos mantendo juntos seus
resultados A/B e repetições; não trate todas as repetições como tarefas independentes.
Para custo por sucesso, recalcule em cada reamostragem a soma dos custos dividida
pela soma dos sucessos de cada variante e então compare as razões. Não use a
média das razões por caso. Identifique reamostragens sem sucessos, sem descartá-las
silenciosamente. Registre o método e o nível do intervalo. Se os dados forem
insuficientes para distinguir a melhora da variação, o resultado é inconclusivo.
Ausência de diferença detectável não comprova equivalência.

Selecione a variante apenas se a evidência sustentar os limites de qualidade e
o ganho pretendido. Falhas em critérios obrigatórios não são compensadas por
economia. Analise cada modelo e categoria antes de agregar; para estimar impacto
operacional, use a mesma distribuição de tarefas e pesos em todas as variantes.

Exemplo didático, sem medições reais: em 100 execuções, A custa 12 unidades
monetárias e tem 90 sucessos; B custa 9 e tem 60. O custo por execução cai 25%,
mas o custo por sucesso sobe de 0,133 para 0,150, aproximadamente 12,5%, e a taxa
de sucesso perde 30 pontos percentuais. B não seria uma melhoria sob um contrato
que exige preservar a qualidade.

Se B atender os limites em um modelo e falhar em outro, teste C no modelo que falhou.
Se ambos regredirem, revise núcleo e roteamento. Mantenha a versão anterior onde
nenhuma candidata atender os critérios. Quando custo e tempo favorecerem opções
diferentes, escolha pela prioridade registrada, sem inventar uma nota única que
oculte a troca.

### 7. Registre e reavalie

Mantenha um registro por execução com os campos abaixo, usando dados sanitizados.
Os caminhos de evidência devem seguir as convenções do repositório.

```text
experimento, caso, categoria, repetição, variante, versão/hash da skill
modelo, esforço, runtime, catálogo, configuração e condição de cache
início, término, tempo ativo, espera humana, timeout e motivo de falha
resultado, critérios atendidos, versão da rubrica e identificação do avaliador
tokens de entrada/saída/cache observados, pico, compactações, ferramentas e retries
custo operacional, custo de avaliação, moeda, preços/data, minutos humanos
evidência, limitações de observabilidade e motivo de eventual exclusão
```

Organize uma pasta por iteração, caso e variante. A organização do skill-creator
oferece os seguintes tipos de registro, adaptáveis ao ambiente:

| Registro | Conteúdo |
| --- | --- |
| `evals/evals.json` | Pedidos, entradas e resultados esperados |
| `eval_metadata.json` | Identificação do caso e critérios usados naquela iteração |
| `outputs/` e transcrição | Artefatos finais e passos observáveis da execução |
| `timing.json` | Duração e consumo efetivamente fornecidos pelo runtime |
| `grading.json` | Veredito por expectativa e evidência correspondente |
| `benchmark.json` | Resultados individuais, agregações e comparação das variantes |
| `feedback.json` | Comentários humanos associados ao caso e à saída revisada |

Ao usar diretamente os scripts do plugin, siga o schema da versão instalada.
Por exemplo, `grading.json` usa `expectations` com `text`, `passed` e `evidence`.
Um relatório genérico não é automaticamente compatível com esses scripts.

O plugin oferece um visualizador para comparar artefatos e métricas. Em outro
runtime, use uma apresentação equivalente que permita revisar as saídas reais.
Sem o skill-creator, o mínimo equivalente é uma tabela de resultados com `text`,
`passed` e `evidence` por expectativa, mais os artefatos e a transcrição de cada
caso. Verifique a disponibilidade de comandos como `claude -p` antes de usar o
otimizador de descrição; esses comandos avaliam apenas o runtime a que pertencem,
e não outro modelo por simples troca de identificador. Campos de tempo ou tokens
ausentes continuam desconhecidos.

O plugin `pwdev-skills` deste marketplace implementa o protocolo acima para
Claude Code, Codex, Hermes Agent e OpenCode: descoberta de runtimes e modelos,
medição estática por camada, execução A/B com esforço explícito ou registrado,
avaliação objetiva no formato do skill-creator e resumo por modelo. Serve como
implementação de referência e como exemplo de registro.

O relatório deve reunir a hipótese, matriz de variantes, amostra distinta e
repetições, métricas por modelo/categoria, incerteza, decisão e limitações.
Reavalie quando mudar skill, modelo, runtime ou ferramenta relevante. Acrescente
falhas reais ao conjunto de desenvolvimento e renove casos reservados quando
forem usados para orientar ajustes.

Comece por inspeção estática e piloto; reserve a avaliação maior para candidatas
promissoras. Defina teto de gasto e regra de parada antes de rodar. Se o orçamento
terminar sem evidência suficiente, registre resultado inconclusivo. Esta revisão
documental não executou benchmarks nem demonstrou ganhos entre modelos.

## Checklist de revisão

- [ ] A descrição identifica uma condição concreta de uso.
- [ ] Há exemplos positivos e negativos de acionamento na avaliação.
- [ ] Os testes de descrição incluem pedidos próximos que não exigem a skill.
- [ ] O núcleo define resultado, limites e conclusão de forma verificável.
- [ ] Cada referência tem uma condição clara de leitura.
- [ ] Regras obrigatórias permanecem disponíveis antes das ações correspondentes.
- [ ] O perfil guiado complementa uma única fonte de verdade.
- [ ] O perfil selecionado não depende de adivinhação sobre o modelo.
- [ ] Os modelos suportados foram avaliados nas configurações registradas.
- [ ] A comparação mantém uma base por modelo, casos pareados e configuração controlada.
- [ ] Há casos reservados, critérios de sucesso e limites definidos antes da medição.
- [ ] Qualidade e respeito ao escopo foram preservados.
- [ ] Aprovação por expectativa e sucesso da tarefa são medidas distintas.
- [ ] Artefatos e passos de execução foram revisados, além das médias.
- [ ] O feedback resultou em orientações generalizáveis e foi registrado por iteração.
- [ ] Custos de falhas, retentativas e escalonamentos entram no custo por sucesso.
- [ ] Contexto acumulado, latência, cache e intervenção humana foram registrados quando disponíveis.
- [ ] Amostra, incerteza e resultados por modelo/categoria sustentam os ganhos alegados.
- [ ] Limitações e cenários não executados estão documentados.
- [ ] A publicação respeita a governança e permite reversão.
- [ ] Modelo e esforço efetivos de cada execução foram registrados com a origem; comparações entre runtimes usam o mesmo esforço ou declaram a diferença.
- [ ] A forma de exposição da skill em cada runtime foi registrada; acionamento só é comparado onde a exposição é a mesma.
- [ ] As regras do avaliador foram aplicadas: uma observação por expectativa, independência de idioma, evidência lida antes do veredito.
- [ ] Execuções cortadas por teto ou indisponibilidade do provedor foram contabilizadas no custo e excluídas do veredito sobre a skill.
- [ ] Há repetições suficientes antes de qualquer decisão; uma execução única foi tratada como direção.

## Referências

- [Skill Creator — Claude by Anthropic](https://claude.com/plugins/skill-creator):
  página oficial do plugin para criação, melhoria e avaliação de skills.
- [`pwdev-skills`](../plugins/pwdev-skills/README.md): plugin deste marketplace que
  implementa o protocolo para Claude Code, Codex, Hermes Agent e OpenCode; a
  [metodologia](../plugins/pwdev-skills/docs/metodologia-de-refatoracao.md) e o
  [manual de uso](../plugins/pwdev-skills/docs/manual-de-uso.md) detalham o processo.
- [OpenCode Zen](https://opencode.ai/docs/zen/): política de retenção de dados dos
  modelos gratuitos. Cada execução de benchmark envia a skill inteira; não avalie
  skills não publicadas ou confidenciais em modelos que retêm ou treinam com prompts.
