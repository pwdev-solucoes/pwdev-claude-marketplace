# PWDEV Copy — Framework de Copywriting Treinável

Plugin genérico de copy para Claude Code. Um arquivo de contexto define marca,
ICP e voz; 14 skills especializadas produzem copy consistente a partir dele.

**A mesma instalação atende qualquer cliente** — troca-se o arquivo de treino.

---

## Instalação

```
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-copy
```

## Primeiro uso

```
/pwdev-copy:treinar   # entrevista → .claude/pwdev-copy-context.md
/pwdev-copy:voc       # pesquisa de voz do cliente → seção 6
/pwdev-copy:brief     # posicionamento, promessa, big idea → seção 3
/pwdev-copy:copy page # produz a copy
```

`/pwdev-copy:status` mostra o que já foi treinado e o que falta.

---

## Arquitetura

```
.claude/pwdev-copy-context.md      ← a memória de treino (9 seções)
        ↓ toda skill lê antes de perguntar
14 skills → 4 subagentes → 7 comandos
```

### Comandos

| Comando | Função |
|---|---|
| `/pwdev-copy:treinar` | Entrevista e gera o contexto |
| `/pwdev-copy:brief` | Hierarquia Ogilvy: posicionamento → promessa → big idea |
| `/pwdev-copy:voc` | Pesquisa de voz do cliente |
| `/pwdev-copy:copy` | Orquestra brief → escrita → revisão |
| `/pwdev-copy:revisar` | Anti-slop + 7 sweeps |
| `/pwdev-copy:variar` | N variações com ângulos distintos |
| `/pwdev-copy:status` | Estado do treino |

### Subagentes

| Agente | Modelo | Papel |
|---|---|---|
| `voc` | sonnet | Pesquisa isolada — coleta consome muito contexto |
| `copywriter` | sonnet | Escreve o rascunho |
| `reviewer` | sonnet | Anti-slop + 7 sweeps |
| `adversarial-copy` | opus | Assume que a copy não converte e tenta provar |

### Skills

**Completas:** `voc-research`, `brand-voice`, `copy-page`, `copy-review`

**Stubs** (estrutura pronta, conteúdo a preencher): `storytelling`, `copy-email`,
`copy-social`, `copy-ads`, `copy-video`, `ux-writing`, `copy-setor-publico`,
`seo-audit`, `schema-markup`, `content-strategy`

---

## Regras que o plugin não negocia

1. **Nunca inventa prova.** Sem número ou depoimento, a saída traz
   `[PREENCHER: ...]` — jamais um dado plausível.
2. **Nunca inventa verbatim de pesquisa.** Fonte não acessada é declarada.
3. **Portão de brief.** Sem posicionamento, promessa e big idea, a produção para.
4. **Rascunho nunca é entrega.** Toda copy passa por revisão.
5. **Degrada com aviso.** Sem MCP ou sem contexto, funciona — e diz que está degradado.

---

## Idioma

Dois eixos independentes: o idioma da **conversa** e o idioma da **copy entregue**.
Podem divergir. Ver `references/language.md`. A preferência é compartilhada com
`pwdev-code` e `pwdev-feat` via `.planning/config.json`.

---

## MCPs

Nenhum é obrigatório. Ver `references/mcp-roadmap.md` para o status verificado
de cada conector planejado (Playwright, Notion, Perplexity, Meta Ads, Higgsfield)
e o que exige construção.

---

## Créditos

Derivado do catálogo em `skills-ia/skills`, com base em `copywriting`,
`copy-editing`, `ogilvy`, `content-strategy`, `seo-audit`, `schema-markup`,
`competitor-alternatives`, `stop-slop` e `adversarial-review`.

Licença Apache-2.0.
