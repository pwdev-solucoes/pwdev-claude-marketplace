---
name: github-init
description: >
  Use quando o usuário quiser configurar o pwdev-github — 'configurar github', 'setup do github
  project', 'init github' — verificando gh, autenticação e o scope project e gravando repo e
  Project padrão em .planning/github.json. Não use para criar um Project (github-project).
metadata:
  version: 0.1.0
---

# Setup do GitHub

## 1. Verificação (somente leitura)

```bash
command -v gh >/dev/null && gh --version | head -1 || echo "NO_GH"
gh auth status 2>&1 | grep -E "Logged in|Token scopes" || echo "NO_AUTH"
gh repo view --json nameWithOwner,owner -q '.nameWithOwner + " " + .owner.login' 2>/dev/null || echo "NO_REPO"
cat .planning/github.json 2>/dev/null || echo "NO_CONFIG"
```

| Resultado | Ação |
|---|---|
| `NO_GH` | instruir a instalação (https://cli.github.com/) e PARAR |
| `NO_AUTH` | pedir `! gh auth login` e PARAR |
| scopes sem `project` | pedir `! gh auth refresh -s project` (Projects exige esse scope; `repo` também é necessário) |
| `NO_REPO` | usar `os argumentos` como `owner/repo` ou perguntar |

## 2. Configuração

Pergunte, uma coisa por vez, só o que faltar:
1. **Repositório padrão** das issues (`owner/repo`) — sugira o detectado.
2. **Dono dos Projects**: `@me` (sua conta) ou a organização do repo.
3. **Project ativo**: listar os existentes
   (`gh project list --owner <dono> --format json -q '.projects[] | "\(.number) \(.title)"'`),
   escolher um, ou deixar vazio e criar depois com a skill `github-project`.

Grave `.planning/github.json` (merge, nunca apague chaves existentes):

```json
{
  "repo": "owner/repo",
  "owner": "@me",
  "project": { "number": 7, "url": "https://github.com/users/me/projects/7", "spec": ".planning/github/project-7.spec.json" }
}
```

`.planning/github/` guarda os mapas de publicação (`<slug>.map.json`) e as specs efetivas dos
Projects — devem ser versionados junto com o roadmap para que outro dev continue o publish.

## 3. Resumo

```
✅ pwdev-github configurado
   gh {versão} · scopes: {scopes}
   Repo: {owner/repo} · Projects de: {owner} · Project ativo: {#n título | nenhum}

👉 github-project      → criar Project a partir de template
👉 github-publish <roadmap.json> → publicar roadmap
👉 "fecha a issue #12", "move #14 para Em andamento" → skill github-issues
```

Idioma: responda no idioma de `.planning/config.json` (`lang`); sem config, no idioma do usuário. Caminhos `<plugin-root>/...`, `references/`, `scripts/` e `templates/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do runtime (`references/runtime.md`).
