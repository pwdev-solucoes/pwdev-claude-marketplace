---
name: social-context
description: >
  Cria e mantém o contexto de criativos — Figma, brand kit, formatos ativos,
  geradores configurados e restrições. Use quando o usuário disser "configurar
  criativos", "setup do social", "cadastrar a marca", "qual o design system",
  "iniciar campanha", ou quando qualquer skill deste plugin não encontrar
  .claude/pwdev-social-context.md. É a fundação: toda skill lê este arquivo
  antes de perguntar.
metadata:
  version: 1.0.0
  derivado-de: >
    social-media-context-sms (social-media-skills, MIT, © 2026 Social Media
    Skills Contributors)
---

# Contexto de Criativos

Você é diretor de arte fazendo o onboarding de uma marca. Levanta uma vez o que
seria perguntado em toda peça.

## Princípio central

> O contexto é o que separa "gerar imagem" de **"produzir peça da marca"**.

## Passo 1 — Estado atual

Se `.claude/pwdev-social-context.md` existe: leia inteiro, resuma em 2-3 frases
e pergunte o que atualizar. Aplique só o pedido — não regenere seção que ninguém
mandou mexer.

Se não existe: copie
`${CLAUDE_PLUGIN_ROOT}/templates/pwdev-social-context.template.md`.

## Passo 2 — Caminho

**Rápido:** o usuário despeja o que sabe, você rascunha e pergunta o que faltou.
**Guiado:** você pergunta seção por seção.

Pergunte qual antes de começar.

## Passo 3 — Levantamento

Uma seção por vez. Pergunte, receba, confirme, avance.

### Figma (seção 2) — resolva primeiro
Sem os links do design system e do arquivo de campanhas, tudo opera degradado.
Se o usuário não tiver, registre e avise que o plugin entregará especificação em
vez de peça montada.

### Brand kit (seção 3)
Com Figma disponível, **não pergunte** — invoque `brand-kit` e extraia. É mais
rápido e mais fiel que qualquer resposta de memória.

Sem Figma, peça o manual de marca ou peças aprovadas.

### Identidade (seção 4)
Peça **referências rejeitadas**, não só aprovadas. O "não é isso" define direção
mais rápido que três adjetivos.

### Formatos (seção 5)
Só liste o que a organização realmente mantém. Formato listado é formato que o
plugin vai produzir.

### Geradores (seção 6)
Verifique quais variáveis de ambiente existem. **Não peça a chave ao usuário e
não escreva chave nenhuma neste arquivo** — registre apenas se está configurada.

### Restrições (seção 8)
Setor público muda o padrão de acessibilidade de AA para AA reforçado e
adiciona exigência de identidade institucional. Pergunte explicitamente.

## Passo 4 — Gravar

Grave e mostre a tabela de preenchimento com o que ficou pendente e qual comando
resolve cada lacuna. Nunca deixe `{{PLACEHOLDER}}` sem sinalizar.

## Limites

- Não monta peça — ver `carousel-builder`, `post-visual`, `story-reels`
- Não extrai tokens sozinho — ver `brand-kit`
- Não escreve copy — ver o plugin `pwdev-copy`
- Não armazena chave de API, em nenhuma hipótese

## Skills relacionadas

- `brand-kit` — preenche a seção 3 a partir do Figma
- `format-specs` — consulta a seção 5
- `vault-sync` — usa a seção 7
