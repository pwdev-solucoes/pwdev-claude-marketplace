# Contexto de Criativos — {{ORGANIZACAO}}

> Gerado por `social-contexto` (`/pwdev-social-media:init`). Toda skill deste plugin lê este arquivo antes
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

Preenchido por `social-marca`, extraído do Figma quando possível.

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

Gerado pelo núcleo `pwdev-media` (≥ 0.4.0). Registre só **se** a chave existe — nunca o valor.
Para guardar: `pwdev-media chaves guardar <provedor>` (Keychain).

| Item do catálogo | Chave configurada | Provedor | Uso previsto |
|---|---|---|---|
| `ideogram:ideogram-3` | não | `ideogram` | imagem com texto |
| `bfl:flux-2-pro` | não | `bfl` | fotorrealismo |
| `leonardo:conta` | não | `leonardo` | ilustração |
| `runway:gen4_turbo` | não | `runway` | vídeo a partir de imagem |
| `magnific:upscale` | não | `magnific` | upscale |
| agregadores (OpenRouter, fal) | não | `openrouter`, `fal` | alternativa por custo |

- **Orçamento por campanha:** {{ORCAMENTO}} · teto mensal no núcleo: `pwdev-media custo orcamento`
- **Exige aprovação antes de gastar:** sim (padrão, não alterar sem decisão)

### Consistência da campanha
Fixado por `social-consistencia` — não alterar no meio da campanha.

- **Item do catálogo e modelo:** {{ITEM}} / {{MODELO}}
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
