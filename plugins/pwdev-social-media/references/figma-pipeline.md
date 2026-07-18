# Pipeline do Figma

O Figma é a **camada opcional de composição** deste plugin. Os ativos vêm da
geração por API; aqui eles ganham texto, marca e layout.

Sem Figma o plugin não trava: a composição é entregue como especificação em
camadas, executável em qualquer ferramenta de edição.

---

## Portão obrigatório

> **Antes de qualquer chamada a `use_figma`, carregue a skill `/figma-use`.**

Isso não é recomendação do PWDEV — é exigência do próprio MCP do Figma. Pular
esse passo produz chamadas malformadas e estruturas que o time de design não
consegue editar depois.

Skills do Figma disponíveis, conforme o plugin instalado:

| Skill | Quando |
|---|---|
| `/figma-use` | **sempre, antes de `use_figma`** |
| `/figma-generate-design` | traduzir um layout em design no Figma |
| `/figma-generate-library` | construir design system a partir de código |
| `/figma-use-figjam` | quadros de conceito e moodboard |

Se o plugin do Figma não estiver instalado, use os recursos servidos pelo MCP
(`skill://figma/figma-use/SKILL.md`).

---

## Fluxo de leitura (Figma → contexto)

Sempre nesta ordem, antes de montar qualquer coisa:

```
1. get_design_context(nodeId | URL)   ← sempre primeiro
2. get_variable_defs(nodeId)          ← tokens formais: cor, tipo, espaçamento
3. search_design_system(query)        ← componentes já existentes
4. get_screenshot(nodeId)             ← referência visual
```

**Nunca crie um componente sem antes procurar se ele já existe.** O erro que mais
irrita time de design é receber um arquivo com o quinto botão diferente.

---

## Fluxo de escrita (ativo gerado → Figma)

```
1. /figma-use                      ← portão
2. get_variable_defs               ← usar tokens reais, nunca hex solto
3. search_design_system            ← reaproveitar componente existente
4. use_figma                       ← montar
5. get_screenshot                  ← conferir o que foi criado
6. creative-review                 ← auditar antes de exportar
```

### Regras de montagem

- **Token, nunca valor solto.** Cor vem de variável, não de `#0A5C36`.
- **Auto Layout sempre.** Frame com posição absoluta quebra na primeira edição.
- **Nomear como o time nomeia.** Consulte a convenção do arquivo antes.
- **Um frame por peça**, nomeado `{{campanha}}/{{formato}}/{{n}}`.
- **Componente para o que repete.** Slide de carrossel é componente com variantes,
  não dez frames copiados.

---

## Estrutura de arquivo

```
📁 {{Campanha}}
├── 📄 00 — Brief            texto do conceito e da copy aprovada
├── 🎨 01 — Tokens           cores, tipografia, grid (referência ao DS)
├── 🧩 02 — Componentes      slide base, card, badge, rodapé
├── 🖼 03 — Peças
│   ├── IG-feed-4x5
│   ├── IG-stories-9x16
│   └── LI-carrossel-4x5
└── ✅ 04 — Aprovado         só o que passou na revisão
```

Exportar **apenas** de `04 — Aprovado`. Isso impede que rascunho vá para
publicação, que é o acidente mais comum e mais caro.

---

## Sem MCP do Figma

O plugin **não trava**. Path B:

1. Produza a **especificação completa** da peça: dimensões, grid, hierarquia,
   token de cor por elemento, tamanho de fonte, área segura, conteúdo exato
2. Entregue como documento que o designer executa
3. Diga explicitamente que a peça não foi montada, apenas especificada

Especificação honesta vale mais que peça inventada. Nunca descreva um frame do
Figma que você não criou.

---

## Export

| Uso | Formato | Escala |
|---|---|---|
| Feed e stories | PNG | 1× (já em 1080) |
| Carrossel LinkedIn | PDF | 1× |
| Miniatura YouTube | JPG < 2 MB | 1× |
| Arquivo de origem | link do Figma | — |

Nomenclatura: `{{campanha}}_{{plataforma}}_{{formato}}_{{n}}_{{versão}}.png`

Exemplo: `dashsaude-out_IG_4x5_01_v2.png`
