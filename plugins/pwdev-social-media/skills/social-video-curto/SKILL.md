---
name: social-video-curto
description: >
  Use quando a pessoa pedir um criativo em vídeo curto — 'reels com legenda', 'vídeo do anúncio',
  'anima esse post', 'criativo animado', 'edita meu vídeo para o reels', 'motion para o story'.
  Decide o caminho e encaminha: vídeo gravado ou peça animada com legenda vai para a edição
  (pwdev-video-hyperframes ou pwdev-video-remotion); clipe só gerado por IA vai para social-video.
  Não use para peça estática 9:16 (social-reels).
metadata:
  version: 3.0.0
---

# Vídeo curto para social — roteamento

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`.

Você decide **qual ferramenta faz o vídeo**. Errar aqui é pagar geração por IA para algo que uma
edição faria melhor e de graça.

## 1. Qual é o material?

| Situação | Caminho | Por quê |
|---|---|---|
| Pessoa gravou falando (anúncio, reels, aula) | **edição** — `vhf-editar` (pwdev-video-hyperframes) | corte pela onda, legenda por palavra, zona segura, portão de qualidade |
| Peça estática aprovada que precisa "ganhar vida" (texto entrando, contador, gráfico) | **edição** com cenas sob medida — `vhf-cenas` | texto nítido e entrando na palavra; sem custo de geração |
| Time trabalha em React ou vai produzir em lote por planilha | **edição** com Remotion — `vrm-editar` (pwdev-video-remotion) | mesmo fluxo; confira a licença do Remotion |
| Cena que não existe e não dá para gravar (produto em movimento, ambiente) | **geração** — `social-video` | Runway ou outro modelo de vídeo, com custo |
| Mistura (gravação + clipes gerados) | geração dos clipes em `social-video`, montagem final em `vhf-editar` | os clipes entram como mídia na edição |

Na dúvida, prefira a edição: é local, não custa por segundo e o texto fica legível. Gerar texto dentro
de vídeo por IA sai ilegível.

## 2. Encaminhar

Diga em uma linha qual caminho e por quê, e passe para a skill certa, na forma do runtime atual:

- Claude Code: `/pwdev-video-hyperframes:editar`, `/pwdev-video-remotion:editar`, `/pwdev-social-media:video`
- Codex: `$vhf-editar`, `$vrm-editar`, `$social-video`
- Hermes: `skill_view("pwdev-video-hyperframes:vhf-editar")` e equivalentes

Plugin de edição não instalado: diga qual instalar (`pwdev-video-hyperframes` é o padrão, Apache-2.0)
e ofereça, enquanto isso, o roteiro e o storyboard por `social-video`.

## 3. O que levar junto

Passe para a edição: copy aprovada, brand kit (cores e fonte da seção 3 viram o `estilo` do
`projeto.json`), formato (`reels-9x16` etc.) e os ativos aprovados na curadoria. Isso evita perguntar
de novo.

## Limites

- Não edita vídeo — os plugins de vídeo fazem
- Não gera clipe — `social-video` faz, com confirmação de custo
- Não publica
