---
description: Treina o plugin para um contexto — entrevista sobre marca, produto, ICP e voz, e gera .claude/pwdev-copy-context.md
argument-hint: "[nome da organização ou produto]"
---

# /pwdev-copy:treinar — Treinar o plugin

Este é o comando que torna o pwdev-copy **genérico e treinável**. Todas as
skills leem o arquivo que ele gera. Rode uma vez por cliente/produto.

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Diferente dos demais comandos,
`treinar` **sempre** pergunta ou confirma o idioma — e pergunta separadamente
o idioma da conversa e o idioma da copy entregue.

## STEP 1 — Estado atual
Se `.claude/pwdev-copy-context.md` já existe: mostre o que está preenchido,
pergunte se é para completar lacunas ou refazer. Nunca sobrescreva sem confirmar.

Se não existe: copie `${CLAUDE_PLUGIN_ROOT}/templates/pwdev-copy-context.template.md`.

## STEP 2 — Entrevista (máx. 3 rodadas, você roda no contexto principal)

Você entrevista o humano. Subagente não faz isso.

**Rodada 1 — Organização e produto** (seções 1, 2)
O que faz, para quem, qual problema resolve, qual a transformação, qual o
diferencial real, quais provas existem, o que nunca pode ser afirmado.

**Rodada 2 — ICP e restrições** (seções 4, 7, 8, 9)
Quem decide, quem influencia, o que acreditam/rejeitam, gatilho de compra,
objeções, alternativa atual. Compliance, vetos jurídicos, LGPD, acessibilidade.
Canais ativos, conversão principal, baseline.

**Rodada 3 — Voz** (seção 5)
Peça de 5 a 10 amostras de texto **já aprovado e publicado**. Se houver, invoque
a skill `brand-voice` em modo DEFINIR para extrair. Se não houver amostras,
marque a seção 5 como pendente — não invente adjetivos.

## STEP 3 — Lacunas
Seções 3 (posicionamento) e 6 (VOC) ficam intencionalmente vazias aqui.
Diga ao usuário:
- seção 3 → preencher com `/pwdev-copy:brief`
- seção 6 → preencher com `/pwdev-copy:voc`

## STEP 4 — Gravar e resumir
Grave `.claude/pwdev-copy-context.md`. Mostre tabela de preenchimento:

| Seção | Status |
|---|---|
| 1-2 Organização e produto | preenchida |
| 3 Posicionamento | pendente → /pwdev-copy:brief |
| ... | |

Nunca deixe `{{PLACEHOLDER}}` sem sinalizar como pendente.
