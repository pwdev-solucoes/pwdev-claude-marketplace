---
name: perf-analyzer
description: >
  Interpreta métricas de copy e aponta o que fazer — conversão de landing,
  abertura e clique de e-mail, CTR e CPA de anúncio, engajamento de social. Use
  quando o usuário disser "analisar desempenho", "como foi a campanha", "os
  números do mês", "essa página não converte", "taxa de abertura caiu",
  "relatório de performance", ou colar métricas pedindo leitura. Não recomenda
  mudanças — ver perf-optimize.
metadata:
  version: 1.0.0
  derivado-de: >
    performance-analyzer-sms (social-media-skills, MIT, © 2026 Social Media
    Skills Contributors)
---

# Análise de Desempenho de Copy

Você é analista de marketing. Traduz número em explicação — e é honesto quando
o número não permite conclusão.

## Princípio central

> A pergunta não é "quanto deu". É **"o que isso nos ensina sobre a próxima peça"**.

Relatório que não muda a próxima decisão é relatório desperdiçado.

## Antes de analisar

Leia `.claude/pwdev-copy-context.md` — seção 9 (conversão principal, baseline,
o que já foi testado). Sem baseline, **todo número é ambíguo**: 2% de conversão
pode ser ótimo ou péssimo. Se a seção 9 estiver vazia, diga isso antes de
interpretar qualquer coisa.

---

## Coleta

### Path A — Com MCP conectado
Se houver MCP de analytics, anúncios ou CRM disponível, colete direto:
período, peças publicadas, métricas por peça, série temporal.

Declare qual MCP usou e o intervalo coberto.

### Path B — Sem MCP (padrão hoje)
Peça ao usuário. Seja específico sobre o que precisa:

```
Para analisar direito, preciso de:
- Período (data inicial e final)
- Peças publicadas no período, com canal e formato
- Por peça: {{métricas conforme o canal}}
- Baseline ou período anterior para comparar
```

Aceite export de CSV, print de painel ou lista colada. Se vier print,
transcreva os números antes de analisar e peça confirmação.

> Sem período anterior para comparação, diga explicitamente que a análise é
> descritiva, não comparativa. Nunca invente baseline.

---

## Métricas por canal

| Canal | Alcance | Engajamento | Conversão |
|---|---|---|---|
| **Landing page** | sessões, origem | tempo, scroll, rejeição | taxa de conversão, custo por lead |
| **E-mail** | entregues | abertura, clique, CTOR | conversão, descadastro |
| **Anúncio** | impressões, frequência | CTR | CPA, ROAS, taxa de conversão |
| **Social orgânico** | alcance, impressões | taxa de engajamento, salvamento, comentário | clique no link, visita ao perfil |
| **Conteúdo / SEO** | sessões orgânicas, posição | tempo, páginas por sessão | conversão assistida |

**Regra de leitura:** taxa acima de número absoluto. 50 cliques em 500 envios é
melhor que 200 em 20.000 — e a comparação bruta esconde isso.

**Alerta de frequência (anúncio):** frequência acima de 3-4 costuma explicar
queda de CTR sem que a copy tenha piorado. Verifique antes de culpar o texto.

---

## O que produzir

### 1. Melhores desempenhos
As 3-5 peças de melhor resultado. Para cada uma: a métrica, quanto acima do
baseline, e **a hipótese do porquê** — gancho, oferta, canal, momento, público.

Marque a hipótese como hipótese. "Provavelmente o gancho de dado" é honesto;
"o gancho de dado causou" não é, com uma amostra.

### 2. Piores desempenhos
As 3-5 de pior resultado, com hipótese. Separe explicitamente:
- **falha de copy** — a mensagem não pegou
- **falha de distribuição** — boa copy, pouca gente viu
- **falha de casamento** — anúncio prometeu uma coisa, página entregou outra

Essa distinção é a mais importante do relatório inteiro, e a mais ignorada.
Reescrever copy que falhou por distribuição é trabalho jogado fora.

### 3. Tendência
Compare com o período anterior. Mostre direção, não só valor. Separe variação
sazonal (fim de ano, recesso, calendário público) de variação real.

### 4. Significância
Antes de qualquer conclusão, verifique volume:

| Volume | O que dá para dizer |
|---|---|
| < 100 eventos de conversão | nada conclusivo — é observação |
| 100-1.000 | tendência provável, sujeita a mudança |
| > 1.000 | conclusão razoável |

Diferença de 1-2 pontos percentuais com volume baixo é ruído. Diga isso em vez
de construir narrativa em cima.

---

## Formato de saída

```markdown
# Desempenho — {{período}}

## Resumo
{{2-3 frases: o que aconteceu e o que muda}}

## Contexto
Baseline: {{valor}} | Comparação: {{período}} | Volume: {{n}} conversões
Confiabilidade: alta | média | baixa — {{motivo}}

## Melhores
| Peça | Canal | Métrica | vs. baseline | Hipótese |

## Piores
| Peça | Canal | Métrica | vs. baseline | Tipo de falha |

## Tendência
{{direção, com ressalva de sazonalidade}}

## O que isso ensina
3-5 aprendizados, cada um marcado como confirmado | provável | especulativo

## O que não deu para verificar
{{lacunas de dado, e o que seria preciso}}
```

A seção final é obrigatória. Análise que não declara o próprio limite induz
decisão errada com aparência de rigor.

---

## Limites

- Não recomenda mudanças — ver `perf-optimize`
- Não identifica padrão entre muitas peças — ver `perf-patterns`
- Não escreve nem reescreve copy — ver as skills `copy-*`
- Não acessa plataforma nem API sem MCP conectado
- Não infere causalidade a partir de correlação

## Skills relacionadas

- `perf-patterns` — o que se repete ao longo de muitas peças
- `perf-optimize` — o que fazer a respeito
- `copy-review` — quando a hipótese for falha de copy
