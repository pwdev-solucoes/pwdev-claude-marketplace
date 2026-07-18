# PWDEV Copy — Framework de Copywriting Treinável

Plugin genérico de copy para Claude Code. Um arquivo de contexto define marca,
ICP e voz; 20 skills cobrem o ciclo completo — pesquisa VOC, brand voice,
criação, revisão e análise de desempenho — produzindo copy consistente a
partir dele.

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
20 skills → 5 subagentes → 9 comandos

ciclo:  treinar → voc → brief → copy → revisar → publicar → analisar ↺
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
| `/pwdev-copy:repurpose` | Uma peça vira vários derivados nativos |
| `/pwdev-copy:analisar` | Fecha o ciclo — desempenho, padrões, plano |
| `/pwdev-copy:status` | Estado do treino |

### Subagentes

| Agente | Modelo | Papel |
|---|---|---|
| `voc` | sonnet | Pesquisa isolada — coleta consome muito contexto |
| `copywriter` | sonnet | Escreve o rascunho |
| `reviewer` | sonnet | Anti-slop + 7 sweeps |
| `adversarial-copy` | opus | Assume que a copy não converte e tenta provar |
| `analyst` | sonnet | Desempenho → padrões → plano de otimização |

### Skills

**Pesquisa e voz:** `voc-research`, `brand-voice`

**Criação:** `copy-page`, `copy-social`, `copy-hooks`, `copy-repurpose`

**Revisão:** `copy-review`, `page-cro`

**Análise** (fecha o ciclo): `perf-analyzer`, `perf-patterns`, `perf-optimize`

**Stubs** (estrutura pronta, conteúdo a preencher): `storytelling`, `copy-email`,
`copy-ads`, `copy-video`, `ux-writing`, `copy-setor-publico`, `seo-audit`,
`schema-markup`, `content-strategy`, `page-cro`

---

## Regras que o plugin não negocia

1. **Nunca inventa prova.** Sem número ou depoimento, a saída traz
   `[PREENCHER: ...]` — jamais um dado plausível.
2. **Nunca inventa verbatim de pesquisa.** Fonte não acessada é declarada.
3. **Portão de brief.** Sem posicionamento, promessa e big idea, a produção para.
4. **Rascunho nunca é entrega.** Toda copy passa por revisão.
5. **Degrada com aviso.** Sem MCP ou sem contexto, funciona — e diz que está degradado.
6. **Não publica sozinho.** Publicar, agendar ou enviar exige confirmação explícita.
7. **Correlação não é causalidade.** Na análise, hipótese é rotulada como hipótese.
8. **Recusa analisar volume insuficiente.** Padrão inventado guia meses na direção errada.

Todas codificadas em `references/anatomia-skill.md`.

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

Derivado de dois catálogos:

- **`skills-ia/skills`** — `copywriting`, `copy-editing`, `ogilvy`,
  `content-strategy`, `seo-audit`, `schema-markup`, `competitor-alternatives`,
  `stop-slop`, `adversarial-review`
- **[social-media-skills](https://github.com/blacktwist/social-media-skills)**
  (MIT) — camada de análise, biblioteca de ganchos, matriz de reaproveitamento,
  e os padrões Path A/B e Limites

Detalhamento em `NOTICE.md`. Licença Apache-2.0.
