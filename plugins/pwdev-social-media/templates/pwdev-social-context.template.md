# Contexto de Criativos — {{ORGANIZACAO}}

> Gerado por `/pwdev-social:init`. Toda skill deste plugin lê este arquivo antes
> de perguntar qualquer coisa.
>
> Local canônico: `.claude/pwdev-social-context.md`
> Complementa `.claude/pwdev-copy-context.md` (texto) — este cuida do visual.
> Última atualização: {{DATA}}

---

## 1. Organização

- **Nome:** {{ORGANIZACAO}}
- **Setor:** {{SETOR}}
- **Contexto:** privado | setor público | misto
- **Idioma das peças:** {{LANG}}

---

## 2. Figma *(opcional — camada de composição)*

- **Arquivo do design system:** {{FIGMA_DS_URL}}
- **Arquivo de campanhas:** {{FIGMA_CAMPANHAS_URL}}
- **Biblioteca publicada:** sim | não — {{NOME}}
- **Convenção de nomenclatura do time:** {{CONVENCAO}}
- **Quem aprova:** {{APROVADOR}}

> Figma é **opcional** nesta arquitetura. Sem ele, a composição é entregue como
> especificação em camadas, executável em qualquer ferramenta. A geração dos
> ativos (seção 6) não depende do Figma.

---

## 3. Brand kit

Preenchido por `brand-kit`, extraído do Figma quando possível.

### Cores (tokens, não hex solto)
| Token | Uso | Valor |
|---|---|---|
| {{TOKEN}} | {{USO}} | {{VALOR}} |

### Tipografia
- **Display:** {{FONTE}} — pesos {{PESOS}}
- **Corpo:** {{FONTE}} — pesos {{PESOS}}
- **Licença das fontes:** {{LICENCA}}

### Logo
- **Arquivos:** {{CAMINHO}}
- **Área de proteção:** {{VALOR}}
- **Versões:** {{VERSOES}}
- **Usos proibidos:** {{PROIBIDO}}

### Grid
- **Margem:** {{VALOR}} · **Colunas:** {{N}} · **Gutter:** {{VALOR}}

---

## 4. Identidade visual

- **Direção:** {{DIRECAO}}
- **Referências aprovadas:** {{REFS}}
- **Referências rejeitadas** (o "não é isso" ensina mais rápido): {{ANTI_REFS}}
- **Tratamento de imagem:** {{TRATAMENTO}}
- **Uso de ilustração:** {{ILUSTRACAO}}
- **Uso de foto de pessoa:** {{FOTO_PESSOA}}

---

## 5. Formatos ativos

| Plataforma | Formato | Frequência | Responsável |
|---|---|---|---|
| {{PLATAFORMA}} | {{FORMATO}} | {{FREQ}} | {{QUEM}} |

Só produza para o que estiver aqui.

---

## 6. Geradores de imagem e vídeo *(caminho principal)*

| Ferramenta | Chave configurada | Variável | Uso previsto |
|---|---|---|---|
| Ideogram | não | `IDEOGRAM_API_KEY` | imagem com texto |
| Leonardo | não | `LEONARDO_API_KEY` | ilustração |
| Flux | não | `BFL_API_KEY` | fotorrealismo |
| Runway | não | `RUNWAY_API_KEY` | vídeo |
| Freepik/Magnific | não | `FREEPIK_API_KEY` | upscale |

- **Orçamento por campanha:** {{ORCAMENTO}}
- **Exige aprovação antes de gastar:** sim (padrão, não alterar sem decisão)

### Consistência da campanha
Fixado por `visual-consistency` — não alterar no meio da campanha.

- **Ferramenta e modelo:** {{FERRAMENTA}} / {{MODELO}}
- **Bloco base do prompt:** {{BLOCO_BASE}}
- **Referência de estilo:** {{REFERENCIA}}
- **Seeds aprovadas:** {{SEEDS}}

---

## 7. Repositórios

- **Vault Obsidian:** {{CAMINHO_VAULT}} *(pasta local — sem MCP)*
- **Notion — banco de peças:** {{NOTION_URL}}
- **Pasta de exports:** {{CAMINHO_EXPORTS}}

---

## 8. Restrições

- **Manual de marca:** {{MANUAL}}
- **Acessibilidade exigida:** WCAG AA | AA reforçado (setor público)
- **LGPD — imagem de pessoas:** {{LGPD}}
- **Autorização de uso de imagem:** {{AUTORIZACAO}}
- **Vedações do jurídico:** {{VEDACOES}}
- **Identidade institucional obrigatória:** {{IDENTIDADE}}

---

## 9. Aprovação

- **Fluxo:** {{FLUXO}}
- **Prazo:** {{PRAZO}}
- **Onde vive o aprovado:** página `04 — Aprovado` do arquivo de campanha
