---
name: social-contexto
description: >
  Use quando for configurar ou conferir o plugin e o contexto da marca — 'configurar
  criativos', 'setup do social', 'status do social media', 'cadastrar a marca', 'guardar a chave do
  Ideogram', 'iniciar campanha' — ou quando outra skill não encontrar o arquivo de contexto. Cria e
  mantém `.claude/pwdev-social-context.md`, confere o pwdev-media, chaves e conectores e mostra o modo
  atual. Não use para extrair tokens (social-marca) nem montar peça.
metadata:
  version: 3.0.0
  derivado-de: >
    social-media-context-sms (social-media-skills, MIT, © 2026 Social Media
    Skills Contributors)
---

# Contexto de Criativos, configuração e status

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md` — na configuração, **sempre** pergunte ou confirme o idioma.

Você é diretor de arte fazendo o onboarding de uma marca. Levanta uma vez o que seria perguntado em
toda peça.

## Princípio central

> O contexto é o que separa "gerar imagem" de **"produzir peça da marca"**.

Arquivo canônico (o mesmo da v2, em qualquer runtime): `.claude/pwdev-social-context.md`, na raiz do
projeto. Ao lado dele vive o contexto de texto do `pwdev-copy` (`.claude/pwdev-copy-context.md`).

## Pedido de "status"

Rode, sem alterar nada:

1. Contexto: quais seções ainda têm `{{PLACEHOLDER}}`.
2. Núcleo: `pwdev-media versao` (precisa ser 0.4.0 ou mais nova) e `pwdev-media status --ao-vivo`
   (chaves e teste gratuito por provedor, idade do catálogo, gasto do mês).
3. Conectores opcionais: o MCP do Figma responde? E o do Notion?
4. Vault do Obsidian acessível (seção 7)?

```
pwdev-social-media — {{organização}}

Contexto     {{n}}/9 seções
  3 Brand kit    pendente → social-marca

Núcleo pwdev-media {{versão}} · catálogo de {{data}} · gasto do mês US$ {{n}}

Chaves (caminho principal)
  Ideogram · BFL (Flux) · Leonardo · Runway · Magnific · OpenRouter · fal
  {{configurada (Keychain|ambiente) | ausente → modo prompt}}

Camadas opcionais
  Figma          conectado | ausente → composição vira especificação
  Notion         conectado | ausente
  Obsidian       {{caminho}} — acessível | não encontrado

Modo atual: completo | prompt | degradado
Próximo passo: {{comando}}
```

Deixe claro o **modo atual** — define o que o plugin consegue entregar.

## Configuração

### Passo 1 — Estado atual

Se `.claude/pwdev-social-context.md` existe: leia inteiro, resuma em 2-3 frases e pergunte o que
atualizar. Aplique só o pedido — nunca sobrescreva sem confirmar.

Se não existe: copie `<plugin-root>/templates/pwdev-social-context.template.md`.

### Passo 2 — Núcleo

```bash
pwdev-media versao
```

Faltou ou é anterior a 0.4.0: carregue a skill `media-setup` do plugin pwdev-media (ou peça para
instalar o plugin `pwdev-media`). Sem o núcleo, o plugin funciona só em modo prompt.

### Passo 3 — Caminho

**Rápido:** a pessoa despeja o que sabe, você rascunha e pergunta o que faltou.
**Guiado:** você pergunta seção por seção. Pergunte qual antes de começar.

### Passo 4 — Levantamento

Uma seção por vez. Pergunte, receba, confirme, avance.

#### Figma (seção 2) — resolva primeiro
Sem os links do design system e do arquivo de campanhas, tudo opera degradado. Verifique se o MCP do
Figma responde; se não, avise que o plugin entregará especificação em vez de peça montada.

#### Brand kit (seção 3)
Com Figma disponível, **não pergunte** — use `social-marca` e extraia. Sem Figma, peça o manual de marca
ou peças aprovadas e marque como inferido.

#### Identidade (seção 4)
Peça **referências rejeitadas**, não só aprovadas. O "não é isso" define direção mais rápido que três
adjetivos.

#### Formatos (seção 5)
Só liste o que a organização realmente mantém, com os ids de `pwdev-media formatos listar`.

#### Geradores (seção 6)
Rode `pwdev-media chaves listar`: registre só **se** cada chave está configurada, nunca o valor. Para
guardar uma chave, a própria pessoa roda (entrada escondida, vai para o Keychain):

- Claude Code: `! pwdev-media chaves guardar ideogram`
- Codex e Hermes: `pwdev-media chaves guardar ideogram` no terminal dela

Provedores: `ideogram`, `bfl`, `leonardo`, `runway`, `magnific`, `openrouter`, `fal`. As variáveis da v2
continuam aceitas (`RUNWAY_API_KEY`, `FREEPIK_API_KEY`). **Nunca peça a chave na conversa e nunca a
escreva em arquivo.** Pergunte uma vez se ela quer um orçamento mensal
(`pwdev-media custo orcamento <valor>`).

#### Restrições (seção 8)
Setor público muda o padrão de acessibilidade de AA para AA reforçado e adiciona exigência de
identidade institucional. Pergunte explicitamente.

### Passo 5 — Gravar

Grave e mostre a tabela de preenchimento com o que ficou pendente e qual comando resolve cada lacuna.
Nunca deixe `{{PLACEHOLDER}}` sem sinalizar.

## Limites

- Não monta peça — ver `social-carrossel`, `social-post`, `social-reels`
- Não extrai tokens sozinho — ver `social-marca`
- Não escreve copy — ver o plugin `pwdev-copy`
- Não armazena chave de API, em nenhuma hipótese

## Skills relacionadas

- `social-marca` — preenche a seção 3 a partir do Figma
- `social-formatos` — consulta a seção 5
- `social-vault` — usa a seção 7
