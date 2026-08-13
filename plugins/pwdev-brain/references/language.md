# Protocolo de Idioma (STEP 0)

Todo comando do pwdev-brain roda isto como **STEP 0**, antes de qualquer
outra etapa.

## Ordem de resolução (silenciosa — todos os comandos exceto `init`)

1. Ler `.claude/pwdev-brain-context.md` → seção 1, campo **Idioma**.
   Se válido (`pt-BR` ou `en`) → usar silenciosamente.
2. Se ausente, ler `.planning/config.json` → campo `lang` (compartilhado com
   os demais plugins pwdev).
3. Se ainda ausente, detectar o idioma de `$ARGUMENTS`.
4. Se ambíguo ou vazio, perguntar:

   ```
   Em qual idioma deseja seguir? / Which language would you like to use?

   1. Portugues (PT-BR)
   2. English (EN)
   ```

5. Persistir a escolha em `.claude/pwdev-brain-context.md` **e** mesclar
   `"lang": "<valor>"` em `.planning/config.json` (nunca sobrescrever outros campos).

## Distinção deste plugin

Conversa, discussão de ingestão, relatórios de lint e documentação seguem
`{{LANG}}`.

**Chaves de frontmatter OKF, valores de sistema e nomes reservados nunca são
traduzidos.** Eles são sintaxe do formato, não prosa:

- Chaves de frontmatter: `type`, `title`, `description`, `resource`, `tags`,
  `generated.by`, `generated.at`, `verified`, `status`, `stale_after`,
  `sources`, `usage_window`, `okf_version`, `runtime`, `parameters`,
  `computation`, `executor`, `attester`.
- Valores de sistema: `draft` | `stable` | `deprecated`, atores
  `human:<id>` / `process:<id>` / `<producer>/<version>`, datas ISO 8601.
- Nomes reservados e paths: `index.md`, `log.md`, `AGENTS.md`, `raw/`,
  `wiki/`, `wiki/output/`, pastas `YYYY-MM-DD-<slug>/`.
- Seções convencionais do OKF: `# Schema`, `# Examples`, `# Computation`.

## Regras de aplicação

- **Conteúdo criado NA wiki** (títulos de conceito, corpo, `description`,
  `tags`) segue o idioma do usuário registrado no contexto — pergunte se
  houver dúvida, nunca traduza conteúdo existente sem pedir.
- **Valores de `type`** ficam em inglês por convenção OKF (`Concept`,
  `Entity`, `Source Summary`, `Comparison`, `Synthesis`, `Playbook`,
  `Attested Computation`) — são vocabulário de intercâmbio, não prosa.
- **Nomes de arquivo** de conceito em `kebab-case`, no idioma do conteúdo,
  sem acentos.
