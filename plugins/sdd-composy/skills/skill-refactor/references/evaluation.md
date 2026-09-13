---
okf_version: "0.2"
type: evaluation-protocol
title: "Avaliação de refatoração entre modelos"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
sources:
  - resource: "docs/skill-refactoring-guide.md"
    sha256: "b044b3d3246dca295fb93c8e7da094a541b200c262fdc57ad4077fde0c7c60c5"
  - resource: "https://claude.com/plugins/skill-creator"
  - resource: "https://developers.openai.com/api/docs/guides/evaluation-best-practices"
  - resource: "https://www.anthropic.com/claude/fable"
verified: []
---

# Avaliar sem confundir edição com ganho

## Desenho do experimento

Comece pelo ciclo do skill-creator: poucos pedidos reais, execução da candidata
e referência, julgamento dos artefatos, feedback humano e nova iteração.
O piloto de 2–3 casos identifica defeitos; não sustenta superioridade estatística.
Use [os casos da própria skill](../evals/evals.json) para testar este refatorador;
ao avaliar outra skill, crie casos próprios do domínio dela.

Fixe antes da comparação final: casos, rubrica, requisitos obrigatórios, modelos,
configurações, orçamento, timeouts, retentativas, métrica principal e limites
aceitáveis. Não rode lotes pagos ou lance provedores externos sem autorização
e orçamento para isso. Um pedido limitado a preparação gera os casos e o plano,
não execuções. Não amplie um piloto para todos os modelos automaticamente.

Para refatoração, A é a versão anterior completa e B a candidata. Para criar uma
skill nova, A é a execução sem essa skill. Compare A/B dentro de cada modelo
antes de comparar modelos. Se fizer C com complemento guiado, mantenha B como
o mesmo núcleo. Registre qual baseline permanece fixa ao longo das iterações.

Astra e Fable recebem `lean` como ponto de partida solicitado; outros modelos
recebem `guided`. Aceite a seleção explícita. Registre o ID real retornado pelo
runtime, esforço, ferramentas e perfil; não invente slugs nem suponha equivalência
entre níveis de esforço de fornecedores. Não altere salvaguardas para obter uma
comparação. Um modelo indisponível fica `not_run`, com motivo.

Pareie pelo mesmo caso, reinicie contexto e arquivos e varie a ordem A/B. A skill
em avaliação e o baseline não recebem a resposta um do outro nem a rubrica usada
apenas pelo avaliador. Paralelize só com isolamento e concorrência controlada.
Execuções sequenciais isoladas são válidas; subagentes não são requisito estatístico.

## Correção e acionamento

Examine artefatos reais e passos observáveis, não só a declaração do executor.
Use verificações objetivas para conteúdo verificável e revisão humana para
qualidade subjetiva. O avaliador registra `text`, `passed` e `evidence` por
expectativa quando usar o formato `grading.json` do skill-creator.

`pass_rate` de expectativas e taxa de tarefas aceitas são métricas diferentes.
Falhar um requisito obrigatório invalida a tarefa mesmo com alta nota média.
Trate evidência ausente como critério não demonstrado. Mostre resultados para
revisão humana e, quando útil, compare A/B sem revelar a versão ao avaliador.

Examine expectativas que passam em ambas as versões, falham em ambas ou variam
muito. Relacione desperdícios observados a hipóteses de alteração e teste um
componente por vez: descrição, roteamento, repetições ou apoio guiado. Reavalie
a combinação final e generalize as correções além dos exemplos vistos.

Teste descoberta separadamente da execução forçada. Use o catálogo real e pedidos
positivos/negativos próximos: refatorar uma skill é positivo; refatorar uma função
Python ou apenas usar a skill é negativo. Meça uma decisão binária por execução:
precisão = TP/(TP+FP); cobertura = TP/(TP+FN). Chamadas repetidas são diagnóstico,
não novos acertos. Denominadores vazios são `N/D`, não zero.

Descrições mais enfáticas, sugeridas pelo skill-creator para omissões de acionamento
no Claude, exigem teste em cada modelo. Não as trate como regra universal do Fable
ou Astra. Separe desenvolvimento, validação de escolha de descrição e conjunto
final intocado; escolher repetidamente pelo resultado transforma teste em validação.

## Medidas e decisão

- Taxa de sucesso: execuções aceitas / iniciadas. Informe também sucesso sem
  recuperação e falhas por categoria. Repetições do mesmo caso não substituem
  diversidade de casos.
- Custo por sucesso: custo de todas as execuções, inclusive falhas, ferramentas,
  recuperação e fallback, dividido pelos sucessos. Sem sucesso, não há razão
  finita. Separe custo de avaliação e trabalho humano.
- Tempo: pedido até conclusão verificada ou falha, p50 e p95 quando a amostra
  permitir, taxa de timeout e espera humana separada. Não reporte apenas sucessos.
- Contexto: entrada acumulada, pico, saída, referências carregadas e compactações.
  A contagem de linhas do arquivo não substitui esses dados.

Capture observações disponibilizadas pelo runtime ao término de cada execução.
Se tokens, cache ou custos estiverem ausentes, marque `not_available` e explique.
Use tarifas verificadas com moeda/data; não some raciocínio duas vezes quando já
estiver incluído na saída. Registre cache observado: conversa nova não garante
cache frio. Compare condições equivalentes e relate falhas externas sem ocultar
seus custos ou excluir seletivamente resultados desfavoráveis.

Considere ganho apenas com qualidade dentro dos limites previamente definidos.
Apresente resultados por modelo/categoria e incerteza. Média e desvio padrão
descrevem a amostra, não comprovam melhora. Se usar bootstrap, reamostre casos
pareados preservando repetições; recalcule a razão total custo/sucessos em cada
amostra e identifique amostras sem sucessos. Dados insuficientes = inconclusivo.

## Registros e apresentação

Crie uma pasta por iteração/caso/variante na área de artefatos autorizada. Registre
prompt, entradas, hashes das versões, configuração, saída, transcrição, julgamento,
tempo e consumo observados. Não exponha segredos nos registros.

Quando o plugin skill-creator estiver disponível e compatível, use seu agregador
e visualizador em vez de reconstruí-los. Valide schemas da versão instalada;
`claude -p` não executa Astra por troca de nome do modelo. Em outro runtime,
apresente artefatos, tabela de resultados e feedback por caso. Mantenha o mesmo
contrato de avaliação sem pressupor ferramentas ou notificações específicas.

Informe o que foi executado e o que está apenas preparado. Um teste que recebe
o rótulo `Fable` para conferir o roteamento não é uma execução no modelo Fable.
Finalize com a decisão e suas limitações, sem alegar economia a partir de
redução estática de palavras ou de uma única execução.
