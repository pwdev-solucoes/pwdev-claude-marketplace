---
okf_version: "0.2"
type: guide
title: "Refatoração de skills para Astra e outros modelos"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:30:36Z"
  description: "Revisão genérica com estratégias do skill-creator da Anthropic e adequação ao OKF v0.2."
provenance:
  actor: "agent:codex"
  created_at: "2026-09-12"
  updated_at: "2026-09-12"
lifecycle:
  status: draft
  scope: "Guia genérico de refatoração e avaliação de skills em diferentes modelos."
sources:
  - resource: "https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra"
  - resource: "https://developers.openai.com/api/docs/guides/evaluation-best-practices"
  - resource: "https://developers.openai.com/api/docs/guides/prompt-caching"
  - resource: "https://claude.com/plugins/skill-creator"
    title: "Skill Creator Plugin — Claude by Anthropic"
  - resource: "Anthropic skill-creator / SKILL.md"
    version: "Plugin claude-plugins-official, versão local instalada consultada em 2026-09-12"
    references: ["references/schemas.md", "agents/grader.md", "agents/analyzer.md"]
verified:
  - by: "agent:codex"
    at: "2026-09-12T23:31:17Z"
    result: pass
    description: "Validador OKF nativo, verificação textual e revisão independente da adaptação. Nenhum benchmark executado."
verification:
  events:
    - type: manual-review
      result: pass
      description: "Revisão metodológica com segunda leitura; corrigidas unidades de roteamento, custo agregado e sucesso sem recuperação. Não constitui benchmark."
---

# Refatoração de skills para Astra e outros modelos

## Objetivo e fundamento

Orientar a refatoração de skills compartilhadas entre GPT-6 Astra e modelos que
precisam de mais orientação. Os exemplos são genéricos e podem ser adaptados a
diferentes agentes, ferramentas e domínios.

O [artigo da OpenAI](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
recomenda descrições curtas e específicas, carregamento progressivo de referências,
regras contextuais no `AGENTS.md` e critérios claros de conclusão. Também alerta
que instruções úteis para Sol ou Luna podem restringir Astra em excesso.

O artigo não apresenta benchmarks que permitam concluir que remover determinada
regra sempre melhora o resultado. Trate suas recomendações como hipóteses a
validar em tarefas representativas.

O método incorpora estratégias do `skill-creator` da Anthropic para Claude:
rascunho, casos reais, comparação com uma referência, avaliação dos artefatos,
feedback humano e iteração. Foram consultados o `SKILL.md` e suas referências
de schemas, correção e análise da versão instalada em 2026-09-12. Os perfis
por modelo e o protocolo estatístico são adaptações deste guia.

## Compatibilidade por comportamento

Neste guia, “modelos que precisam de mais orientação” substitui “modelos inferiores”.
A necessidade de estrutura depende da tarefa, das ferramentas e da configuração;
o nome do modelo, isoladamente, não demonstra uma limitação.

Mantenha o mesmo contrato de qualidade para todos. Ajuste o suporte oferecido para
atingi-lo, preservando segurança, escopo autorizado e critérios de aceitação.

| Aspecto | Perfil enxuto, candidato para Astra | Perfil guiado, quando necessário |
| --- | --- | --- |
| Planejamento | Objetivo, restrições e resultado esperado | Sequência curta com entregáveis intermediários |
| Exemplos | Casos com ambiguidade relevante | Exemplo resolvido e erro comum observado |
| Verificação | Critérios e comandos aplicáveis | Checklist com interpretação de sucesso e falha |
| Ferramentas | Contrato e limites de uso | Exemplos de chamadas e recuperação de erros conhecidos |
| Conclusão | Evidência esperada e ponto de parada | Conferência explícita de itens pendentes |
| Aprovação | Limites definidos pela governança | Os mesmos limites, com situações exemplificadas |

Selecione o perfil explicitamente no ambiente ou na tarefa quando possível.
Se o modelo ou suas capacidades forem desconhecidos, use o núcleo comum e um
checklist curto. Não deduza a identidade do modelo pelo estilo da resposta.

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

## O que manter, mover e remover

| Conteúdo encontrado | Tratamento sugerido |
| --- | --- |
| Limite de autorização ou proteção de dados | Manter explícito e acessível antes da ação relevante |
| Regra de negócio ou formato obrigatório | Manter no contrato ou referência obrigatória do fluxo |
| Procedimento específico de uma ferramenta | Mover para referência carregada ao usar essa ferramenta |
| Explicação extensa para um erro recorrente | Mover para o perfil guiado, com cenário de avaliação |
| Mesma regra repetida em vários arquivos | Eleger uma fonte e referenciá-la |
| Obrigação universal de ler documentos | Substituir por condições concretas de leitura |
| Adjetivos como “excelente” e “perfeito” | Substituir por critérios observáveis |
| Regra sem finalidade identificável | Investigar sua origem e testar a remoção |

Não reduza o texto removendo requisitos necessários à correção. Também não
transfira tudo para referências que continuem sendo carregadas obrigatoriamente
em todas as tarefas: isso mantém o custo de contexto.

## Exemplo de acionamento

Antes:

```yaml
description: Use sempre que trabalhar com textos, documentos, mensagens ou informações.
```

Depois, para uma skill de resumo estruturado:

```yaml
description: Resuma documentos ou transcrições em pontos principais, decisões e pendências quando o usuário pedir uma síntese estruturada.
```

O texto revisado permite distinguir uma síntese de uma tradução ou revisão
gramatical do mesmo documento. Na avaliação, inclua pedidos em que a skill deve
e não deve disparar.

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

1. Escolha uma skill e registre seu comportamento esperado, consumidores e comandos existentes.
2. Separe requisitos de domínio, limites de autorização e apoio procedural.
3. Identifique conflitos, repetições e condições de acionamento excessivamente amplas.
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
suportado, incluindo Astra. Use B e C no mesmo modelo quando precisar investigar
o efeito do complemento. Não atribua ao texto uma melhora obtida ao trocar
simultaneamente modelo, esforço de raciocínio e ferramentas.

Primeiro meça a refatoração com a configuração do modelo fixa. Depois, em um
experimento separado, ajuste modelo e esforço para encontrar uma combinação
mais econômica que cumpra os mesmos critérios. O mesmo nome de nível de esforço
em dois modelos não garante o mesmo orçamento de computação.

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
Não suponha que uma descrição otimizada no Claude terá o mesmo efeito no Astra.

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

Registre separadamente o custo de avaliar as respostas e o esforço humano. Se a
operação real usar um verificador ou fallback, inclua esses componentes no custo
operacional e reporte a taxa de escalonamento. Um modelo barato que frequentemente
recorre ao Astra deve ser avaliado pelo custo do fluxo inteiro.

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

Se B atender os limites no Astra e falhar em outro modelo, teste C nesse modelo.
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
Verifique a disponibilidade de comandos como `claude -p` antes de usar o
otimizador de descrição; esses comandos não avaliam Astra por simples troca de
identificador. Campos de tempo ou tokens ausentes continuam desconhecidos.

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

## Referência do plugin

[Skill Creator — Claude by Anthropic](https://claude.com/plugins/skill-creator):
página oficial do plugin para criação, melhoria e avaliação de skills.
