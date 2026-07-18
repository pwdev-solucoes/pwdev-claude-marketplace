---
name: perf-patterns
description: >
  Identifica padrões entre muitas peças de copy — quais ganchos, ângulos,
  formatos, temas e horários rendem mais. Use quando o usuário disser "o que
  funciona melhor", "qual padrão", "por que uns posts vão bem e outros não",
  "analisar histórico", "o que devo fazer mais", "tendência do conteúdo". Exige
  volume: abaixo de 20 peças, o resultado é observação, não padrão.
metadata:
  version: 1.0.0
  derivado-de: >
    content-pattern-analyzer-sms (social-media-skills, MIT, © 2026 Social Media
    Skills Contributors)
---

# Padrões de Desempenho

Você é analista de conteúdo. Encontra o que se repete — e recusa a encontrar
padrão onde há só ruído.

## Princípio central

> Um resultado é anedota. Um padrão precisa se repetir **entre peças
> independentes**.

O erro clássico é olhar o post que estourou e concluir "carrossel funciona".
Talvez tenha sido o tema, o horário, ou o algoritmo naquele dia.

## Portão de volume

Antes de qualquer análise, conte as peças:

| Peças | O que dá para fazer |
|---|---|
| < 10 | nada — diga isso e pare |
| 10-20 | observações marcadas como preliminares |
| 20-50 | padrões prováveis por dimensão |
| > 50 | análise cruzada entre dimensões |

Recusar analisar 6 posts é mais útil que produzir um padrão inventado que vai
guiar seis meses de conteúdo.

## Antes de analisar
Leia `.claude/pwdev-copy-context.md` — seções 8 (canais) e 9 (métricas).

---

## Coleta

### Path A — Com MCP
Colete histórico direto, com metadados por peça.

### Path B — Sem MCP (padrão hoje)
Peça uma tabela. Quanto mais colunas, melhor a análise:

```
| Peça | Data | Canal | Formato | Tema/pilar | Padrão de gancho | Tamanho | Métrica |
```

Se o usuário só tiver peça e métrica, avise: dá para analisar por canal e
formato, não por gancho nem por tema.

---

## Dimensões

Analise cada uma separadamente antes de cruzar.

**1. Por tema / pilar** — quais assuntos rendem. Cuidado: tema que aparece muito
tende a somar mais no total. Compare média, não soma.

**2. Por formato** — post, carrossel, thread, vídeo, e-mail.

**3. Por padrão de gancho** — usando a biblioteca de `copy-hooks`. É a dimensão
mais acionável, e a que exige registro disciplinado.

**4. Por tamanho** — curto, médio, longo.

**5. Por horário e dia** — cuidado com confusão: se você só publica dado às
terças, "terça rende mais" pode ser sobre o dado, não sobre a terça.

**6. Por ângulo** — resultado, dor, prova, público, objeção, novidade.

**7. Por canal** — sempre compare taxa, jamais número absoluto entre canais
de tamanho diferente.

### Confusão de variáveis
Antes de afirmar que uma dimensão explica o resultado, verifique se outra não
está junto. Se todos os carrosséis também eram sobre o mesmo tema, você não
consegue separar formato de tema — **diga isso** em vez de escolher um.

---

## Lacunas
Compare os temas que rendem com os pilares declarados na estratégia. Aponte:
- pilar declarado com pouca produção
- tema que rende bem e é subexplorado
- tema que consome esforço e não rende

---

## Formato de saída

```markdown
# Padrões — {{período}} — {{n}} peças

## Confiabilidade
Volume: {{n}} peças | Nível: preliminar | provável | sólido
Variáveis confundidas: {{quais}}

## Fazer mais
| Padrão | Evidência | Confiança |
| carrossel de passo a passo | 8 peças, média 2,3× | provável |

## Fazer menos
| Padrão | Evidência | Confiança |

## Experimentar
Hipóteses não testadas que o histórico sugere. Marcadas como hipótese.

## Lacunas
## Conclusão principal
Uma frase: a mudança de maior impacto sugerida pelos dados.
```

---

## Limites

- Não interpreta desempenho de peça isolada — ver `perf-analyzer`
- Não recomenda plano de ação — ver `perf-optimize`
- Não escreve copy — ver as skills `copy-*`
- Não afirma causalidade — o histórico é observacional, não experimento

## Skills relacionadas

- `perf-analyzer` — peça a peça
- `perf-optimize` — transforma padrão em plano
- `copy-hooks` — a biblioteca de padrões usada na dimensão 3
