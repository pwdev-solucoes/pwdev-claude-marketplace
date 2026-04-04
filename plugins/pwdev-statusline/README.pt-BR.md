# PWDEV-STATUSLINE v1.0.0

*Read in [English](./README.md)*

> **Barra de status rica para o Claude Code — modelo, branch, contexto, rate limits e tokens em uma linha colorida no terminal.**

---

## Funcionalidades

| Seção | Cor | O que exibe |
|-------|-----|-------------|
| **Diretório** | Azul | Diretório de trabalho atual |
| **Modelo** | Ciano | Nome do modelo Claude ativo |
| **Branch Git** | Magenta | Branch atual (quando dentro de um repositório git) |
| **Contexto** | Amarelo | Barra de progresso visual + porcentagem da janela de contexto |
| **Rate Limit** | Verde/Vermelho | Uso do rate limit de 5h (vermelho a partir de 80%) |
| **Tokens** | Branco | Total de tokens de entrada + saída |
| **Sessão** | Branco | Nome da sessão (quando definido) |
| **PWDEV** | Verde | Nome da empresa (sempre visível, primeiro segmento) |
| **Usuário** | Branco | Nome do usuário git via `git config user.name` |

### Exemplo de saída

```
PWDEV | Paulo Soares | demo | ~/meu-projeto | Opus 4.6 | main | ctx:████░░░░░░ 42% | tok:1500 | 5h:15%
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
