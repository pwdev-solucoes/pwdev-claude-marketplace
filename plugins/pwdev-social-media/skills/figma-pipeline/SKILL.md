---
name: figma-pipeline
description: >
  Compõe a peça final no Figma sobre os ativos gerados — texto, marca, layout e
  grid. Camada OPCIONAL: use quando houver Figma conectado e o time precisar do
  arquivo editável. Dispara em "montar no Figma", "compor a peça", "colocar o
  texto na imagem", "aplicar a marca", "arquivo editável". Sem Figma, entrega
  especificação de composição.
metadata:
  version: 2.0.0
---

# Composição no Figma

Camada **opcional**. Os ativos vêm da geração; aqui eles viram peça de marca.

## Onde esta skill entra

```
prompt-craft → image-gen → asset-curation → [figma-pipeline] → creative-review
                                              ↑ opcional
```

Sem Figma, a peça pode ser fechada na própria ferramenta de edição do time. Esta
skill existe para quando o arquivo editável importa — e não trava nada quando
não existe.

## Princípio central

> O gerador entrega o **fundo**. A marca entra aqui.

Texto composto no Figma é editável, acessível e legível. Texto pedido ao gerador
sai deformado e imutável. Essa divisão de trabalho é a que mais economiza
crédito na stack inteira.

## Quando usar Figma

| Situação | Vale? |
|---|---|
| Time de design precisa editar depois | **sim** |
| Peça vira template para muitas variações | **sim** |
| Campanha com design system estabelecido | **sim** |
| Peça única, urgente, sem time de design | não — componha direto |
| Nenhum arquivo Figma existe | não — entregue especificação |

## Path A — Figma conectado

**Portão:** carregue `/figma-use` antes de qualquer `use_figma`. Exigência do
próprio MCP, não convenção do PWDEV. Sem ela, pare.

```
1. get_design_context      contexto do arquivo
2. get_variable_defs       tokens reais
3. search_design_system    o componente já existe?
4. upload_assets           subir o ativo gerado
5. use_figma               compor
6. get_screenshot          conferir
```

### Regras
- **Token, nunca hex solto** — a peça acompanha mudança de marca
- **Auto Layout sempre** — frame absoluto quebra na primeira edição
- O que repete é **componente com variantes**, não frames copiados
- Texto real, nunca lorem
- Nomear `{{campanha}}/{{formato}}/{{n}}`

### Sobre ativo gerado
- Verifique **área limpa** para o texto antes de compor. Se não houver, o
  problema é a seleção — volte para `asset-curation`
- Aplique sobreposição, gradiente ou caixa sob o texto. Nunca confie no
  contraste direto da imagem gerada
- Meça contraste contra a **região mais clara sob o texto**

## Path B — Sem Figma

Entregue especificação de composição executável em qualquer ferramenta:

```
Ativo base:   {{arquivo gerado}}
Dimensão:     {{1080 × 1350}}
Grid:         margem {{n}} · colunas {{n}}
Sobreposição: {{cor}} a {{n}}% · gradiente {{direção}}

Camadas (fundo → topo):
  1. {{ativo}}
  2. {{sobreposição}}
  3. {{texto nível 1}} — {{fonte}} {{tamanho}} {{token de cor}} — {{posição}}
  4. {{texto nível 2}} — ...
  5. {{logo}} — {{posição}} — área de proteção {{n}}
```

Declare que a peça **não foi montada**. Nunca descreva um frame que você não criou.

## Estrutura do arquivo

```
📁 {{Campanha}}
├── 🖼 Ativos gerados     o que veio das APIs, com seed no nome
├── 🧩 Componentes
├── 🖼 Peças
└── ✅ Aprovado
```

Só sai export de `Aprovado`.

## Limites

- Não gera imagem — ver `image-gen`
- Não decide conceito — ver `creative-concept`
- Não seleciona entre variações — ver `asset-curation`
- Não aprova a própria peça — ver `creative-review`
- Não exporta — ver `export-handoff`
- Não publica
- Não altera o design system sem pedido explícito

## Skills relacionadas

- `asset-curation` — entrega o ativo selecionado
- `brand-kit` — de onde vêm os tokens
- `creative-review` — portão de saída
