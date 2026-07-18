# PWDEV-STATUSLINE v1.1.0

*Read in [English](./README.md)*

> **Barra de status rica para o Claude Code — modelo, branch, contexto, rate limits e tokens em uma linha colorida no terminal.**

---

## Novidades da v1.1.0

- **Bloco de configuração**: toda a personalização (toggles SHOW_*, cores,
  separador, profundidade do diretório) vive em variáveis no topo do script —
  o `/customize` edita 1 linha, de forma idempotente, em vez de comentar código.
- **Uma chamada de jq**: todos os campos extraídos em UMA passada (eram ~8
  por render) — atualização visivelmente mais rápida.
- **Cores dinâmicas**: a barra de contexto fica verde/amarela/vermelha
  (<60 / 60-79 / ≥80%); o rate limit ganha faixa amarela (50-79%).
- **Segmentos legíveis**: tokens formatados como `512k` / `1.2M`; diretório
  com `~` e truncado aos últimos N segmentos (`…/a/b/c`, configurável).
- **Robustez**: valores não-numéricos no payload não causam mais erros — o
  segmento apenas some; template lido via `${CLAUDE_PLUGIN_ROOT}` (o path
  relativo antigo quebrava instalações via marketplace).
- **Comandos mais seguros**: `uninstall` confirma antes de apagar; `install`
  é idempotente quando já atualizado; os 4 comandos são manuais
  (`disable-model-invocation`).

## Funcionalidades

| Seção | Cor | O que exibe |
|-------|-----|-------------|
| **Diretório** | Azul | Diretório atual com `~`, truncado aos últimos N segmentos |
| **Modelo** | Ciano | Nome do modelo Claude ativo |
| **Branch Git** | Magenta | Branch atual (quando dentro de um repositório git) |
| **Contexto** | Verde/Amarelo/Vermelho | Barra visual + porcentagem (vermelho ≥80%) |
| **Rate Limit** | Verde/Amarelo/Vermelho | Uso do rate limit de 5h (amarelo ≥50%, vermelho ≥80%) |
| **Tokens** | Branco | Total entrada+saída, formatado (`512k`, `1.2M`) |
| **Sessão** | Branco | Nome da sessão (quando definido) |
| **PWDEV** | Verde | Nome da empresa (primeiro segmento; todos os segmentos são configuráveis) |
| **Usuário** | Branco | Nome do usuário git via `git config user.name` |

### Exemplo de saída

```
PWDEV | Paulo Soares | demo | …/skills-ia/meu-projeto | Fable 5 | main | ctx:████░░░░░░ 42% | tok:1.5k | 5h:15%
```

---

## Requisitos

- **`jq`** — processador JSON (usado para interpretar o JSON de status do Claude Code)

Instalação do jq:
```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# Fedora
sudo dnf install jq
```

---

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/pwdev-statusline:install` | Instala o script e configura o `settings.json` do Claude Code |
| `/pwdev-statusline:uninstall` | Remove o script e a entrada de configuração |
| `/pwdev-statusline:customize` | Mostrar/ocultar seções, alterar cores, trocar separador |
| `/pwdev-statusline:preview` | Visualizar a saída da status line com dados de exemplo |

---

## Início Rápido

```
/pwdev-statusline:install
```

Reinicie o Claude Code para ver a barra de status.

---

## Personalização

```bash
# Ver configuração atual
/pwdev-statusline:customize show

# Ocultar/exibir seções
/pwdev-statusline:customize hide-tokens     # ocultar contador de tokens
/pwdev-statusline:customize show-tokens     # exibir novamente
/pwdev-statusline:customize hide-rate       # ocultar rate limit
/pwdev-statusline:customize hide-git        # ocultar branch git
/pwdev-statusline:customize hide-session    # ocultar nome da sessão

# Alterar cores das seções
/pwdev-statusline:customize colors

# Profundidade do diretório
/pwdev-statusline:customize dir-depth 2

# Trocar separador (padrão: " | ")
/pwdev-statusline:customize separator ·
/pwdev-statusline:customize separator " ▸ "
/pwdev-statusline:customize separator " — "
```

---

## Como Funciona

O Claude Code envia um JSON com informações da sessão para o script configurado em `statusLine`. O script processa esse JSON com `jq` e monta uma linha formatada com cores ANSI.

```
Claude Code          statusline.sh          Terminal
───────────          ─────────────          ────────
JSON da sessão  →    Parseia com jq    →    Linha colorida
                     Monta segmentos        na barra inferior
                     Aplica cores ANSI
```

### Arquivos

| Arquivo | Caminho |
|---------|---------|
| Script | `~/.claude/statusline.sh` |
| Configuração | `~/.claude/settings.json` → campo `statusLine` |

---

## Desinstalação

```
/pwdev-statusline:uninstall
```

Remove o script e a configuração. Reinicie o Claude Code para aplicar.

---

## Licença

Apache-2.0
