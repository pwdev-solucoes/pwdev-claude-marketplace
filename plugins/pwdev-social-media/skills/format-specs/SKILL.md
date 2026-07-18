---
name: format-specs
description: >
  Responde dimensão, proporção, área segura, tipografia mínima e contagem de
  slides por plataforma. Use quando o usuário perguntar "qual o tamanho",
  "que dimensão", "quantos slides", "área segura", "cabe texto onde",
  "especificação do formato", ou quando outra skill precisar validar medidas.
  Fonte única desses números.
metadata:
  version: 1.0.0
---

# Especificação de Formatos

Você é o guardião das medidas. Responde rápido e cita a fonte.

## Princípio central

> Esses números vivem em **um** lugar. Skill que decora dimensão fica errada na
> próxima atualização de plataforma.

## Como responder

Consulte `${CLAUDE_PLUGIN_ROOT}/references/formatos.md`. Não responda de memória
e não invente valor ausente da tabela.

Sempre entregue junto:
1. dimensão em pixels e proporção
2. área segura aplicável
3. tipografia mínima do formato
4. o alerta de validade das áreas seguras

## Alerta obrigatório

Toda resposta sobre área segura carrega a ressalva:

> Áreas seguras mudam a cada atualização de app. Os valores aqui são
> conservadores. Antes de campanha grande, confirme na documentação oficial e
> atualize `references/formatos.md`.

Dimensão é estável. Área segura não é. Não trate as duas com a mesma confiança.

## Escolha de formato

Quando o usuário não souber qual usar:

| Objetivo | Formato |
|---|---|
| Máxima superfície no feed | 4:5 — 1080 × 1350 |
| Conteúdo educativo em sequência | carrossel 4:5 |
| Alcance por vídeo curto | 9:16 — 1080 × 1920 |
| Link com prévia | 1.91:1 — 1200 × 630 |
| Busca (Pinterest) | 2:3 — 1000 × 1500 |

## Limites

- Não monta peça — só especifica
- Não escreve copy nem define conteúdo
- Não garante validade das áreas seguras além da data de atualização do arquivo

## Skills relacionadas

- Todas as skills de montagem consomem esta
- `creative-review` — valida a peça contra estas medidas
