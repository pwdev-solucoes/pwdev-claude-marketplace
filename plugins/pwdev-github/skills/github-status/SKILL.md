---
name: github-status
description: >
  Use quando o usuário perguntar o estado da integração com o GitHub — 'status do github', 'qual
  project está configurado', 'o que já foi publicado' — gh, scopes, repo, Project e roadmaps
  publicados. Somente leitura.
metadata:
  version: 0.1.0
---

# Estado do pwdev-github

Somente leitura. Responda no idioma de `.planning/config.json` (`lang`).

```bash
gh --version 2>/dev/null | head -1 || echo "NO_GH"
gh auth status 2>&1 | grep -E "Logged in|Token scopes" || echo "NO_AUTH"
cat .planning/github.json 2>/dev/null || echo "NO_CONFIG"
for m in .planning/github/*.map.json; do
  [ -f "$m" ] || continue
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1], d.get('repo'), d.get('project_url'), len(d.get('issues',{})), 'issues', len(d.get('blocked_by',[])), 'deps')" "$m"
done
```

Apresente:

```
GH: {versão} · auth: {ok|faltando} · scope project: {sim|não}
REPO: {owner/repo | não configurado}
PROJECT: {#n url | nenhum}
PUBLICADOS: {slug → N issues, M dependências, url}
PRÓXIMO: {github-init | github-project | github-publish ...} (na forma de comando do runtime)
```

Idioma: responda no idioma de `.planning/config.json` (`lang`); sem config, no idioma do usuário. Caminhos `<plugin-root>/...`, `references/`, `scripts/` e `templates/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do runtime (`references/runtime.md`).
