---
description: Produz roteiro, storyboard e prompts de vídeo para Runway, Higgsfield ou produção manual
argument-hint: "[duração] [tema]"
---

# /pwdev-social:video

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## STEP 1 — Alinhar expectativa
Diga logo: este comando entrega **especificação**, não arquivo de vídeo.
Runway tem API (integração possível). Higgsfield não tem evidência de API
pública estável — execução manual.

Não deixe ninguém esperando um .mp4.

## STEP 2 — Produzir
Invoque `video-gen`: roteiro, storyboard cena a cena, prompt por cena,
texto na tela, legenda completa.

Os 3 primeiros segundos precisam funcionar **mudos**.

## STEP 3 — Frames estáticos
Capa e thumbnail via `story-reels` + `figma-builder`.

## STEP 4 — Acessibilidade
Legenda embutida é obrigatória. Texto dentro da área segura. Sem piscar acima
de 3 Hz.

## STEP 5 — Entregar
Brief com status **ESPECIFICADO, não gerado** em destaque.
