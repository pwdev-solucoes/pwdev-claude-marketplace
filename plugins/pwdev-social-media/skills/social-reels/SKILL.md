---
name: social-reels
description: >
  Use quando a peça for vertical 9:16 — 'story', 'reels', 'shorts', 'TikTok', 'vertical',
  '9:16', 'capa de reels', 'template de story'. Monta respeitando a zona segura da interface de cada
  app. Não use para gerar ou editar vídeo (social-video, social-video-curto) nem para peça de feed
  (social-post).
metadata:
  version: 3.0.0
---

# Vertical 9:16

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma: `<plugin-root>/references/language.md`.

Você monta no formato onde o app **come parte da tela**. Ignorar isso é o erro
que mais gera republicação.

## Princípio central

> A tela tem 1080 × 1920, mas o app **cobre topo, base e a lateral direita** (perfil, legenda, botões).
> Projetar para 1920 de altura é projetar para ser coberto.

## Zonas seguras

Os números vivem no catálogo de formatos do `pwdev-media` — cada app tem a sua:

```bash
pwdev-media formatos mostrar reels-9x16      # Instagram/Facebook Reels
pwdev-media formatos mostrar stories-9x16
pwdev-media formatos mostrar tiktok-9x16     # botões ocupam mais da lateral direita
pwdev-media formatos mostrar shorts-9x16
```

Peça que vai para várias redes: monte dentro da **interseção** das zonas seguras (a mais restritiva
de cada lado).

> Erro mais comum: chamada no rodapé, onde a legenda do app cobre.
> Segundo mais comum: elemento à direita, atrás dos botões de ação.

**Ressalva de validade:** zonas seguras mudam a cada atualização de app. As margens do catálogo são
conservadoras e têm data de verificação; confirme antes de campanha grande.

## Estrutura

```
0-1s     gancho — precisa funcionar mudo e sem contexto
1-3s     desenvolvimento
3s-fim   entrega
final    CTA dentro da área segura
```

Story em sequência: cada card precisa sobreviver sozinho. As pessoas entram no
meio da sequência o tempo todo.

## Vídeo

- **Legenda embutida é obrigatória.** A maioria assiste sem som — e sem legenda
  a peça é inacessível para pessoa surda. Não é preferência, é acessibilidade.
- Legenda dentro da área segura, nunca no rodapé
- Sem piscar acima de 3 Hz — risco de convulsão fotossensível
- Texto na tela: mínimo 32 px, alto contraste, tempo de leitura suficiente

## Montagem

**Portão:** `/figma-use` antes de `use_figma`.

1. Criar frame 1080 × 1920
2. **Criar guias da zona segura como primeira ação** — antes de qualquer conteúdo
3. Montar o conteúdo inteiro dentro da zona segura (`pwdev-media formatos mostrar <id>`)
4. Conferir com `get_screenshot` que nada crítico saiu da área
5. Nomear `{{campanha}}/9x16/{{n}}`

Faça um componente `Story base` com as guias — assim toda peça nasce correta.

## Anti-padrões

- CTA no rodapé
- Elemento importante na faixa direita
- Texto colado na borda superior
- Vídeo sem legenda
- Reaproveitar peça 4:5 esticada para 9:16
- Texto pequeno "porque é vertical" — a distância de leitura é a mesma

## Limites

- Não edita nem gera vídeo — ver `social-video`
- Não escreve copy — ver `pwdev-copy`
- Não publica
- Não garante a zona segura além da data de verificação do catálogo de formatos

## Skills relacionadas

- `social-conceito`, `social-figma`, `social-revisao`, `social-video`, `social-formatos`
