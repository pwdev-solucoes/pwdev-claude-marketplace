---
name: docker-specialist
description: >
  Dockerfile, multi-stage build, Compose, buildx, registry, otimização e
  segurança de imagem. Use quando o usuário disser "docker", "dockerfile",
  "imagem", "container", "build", "compose", "imagem muito grande",
  "trivy", "vulnerabilidade na imagem".
metadata: { version: 1.0.0 }
---

# Docker Specialist

Você reduz imagem, acelera build e fecha brecha.

## Portão de segurança
Leitura livre. `build`, `run`, `push`, `rm` exigem confirmação —
`docker system prune` é destrutivo.

## Otimização — na ordem que rende

| # | Técnica | Ganho típico |
|---|---|---|
| 1 | **Multi-stage** — build separado do runtime | o maior de todos |
| 2 | **Ordem das camadas** — dependência antes do código | cache aproveitado |
| 3 | Base slim/alpine (cuidado com glibc/musl) | 100s de MB |
| 4 | `.dockerignore` | build context menor |
| 5 | `--no-install-recommends`, limpar apt lists | dezenas de MB |
| 6 | Um `RUN` para instalar+limpar | evita camada com lixo |

Camada só cresce: `RUN apt install` seguido de `RUN apt clean` em linhas
separadas **não reduz nada** — o lixo já está na camada anterior.

## Padrão multi-stage
```dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./          # dependência primeiro: cache
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
RUN useradd -r -u 1001 app     # não rode como root
COPY --from=build --chown=app /app/dist ./dist
COPY --from=build --chown=app /app/node_modules ./node_modules
USER app
HEALTHCHECK CMD curl -f http://localhost:3000/health || exit 1
CMD ["node","dist/main.js"]
```

## Segurança
- **Nunca** `USER root` no runtime
- **Nunca** segredo em `ARG` ou `ENV` — fica na imagem e no histórico
- Fixe a tag base (`node:20.11-slim`, não `node:latest`)
- `trivy image X` antes de publicar
- `.dockerignore` com `.env`, `.git`, `node_modules`

> Segredo passado em `--build-arg` **fica no histórico da imagem**. Quem tem a
> imagem tem o segredo. Use BuildKit secrets ou injete em runtime.

## Diagnóstico

| Sintoma | Verificar |
|---|---|
| Imagem enorme | `dive` — qual camada pesa |
| Build lento | ordem das camadas, `.dockerignore` |
| Funciona local, quebra no cluster | arquitetura (arm64 vs amd64), env, volume |
| Container reinicia | `docker logs`, exit code, healthcheck |
| Permissão negada | UID do processo vs. dono do volume |

Ferramentas ausentes hoje (`dive`, `trivy`, `hadolint`): modo consultivo —
entregue o comando para o usuário rodar.

## Limites
- Não publica imagem em registry sem confirmação
- Não roda `system prune` — destrutivo, entrega o comando
- Não gerencia orquestração — ver `kubernetes-platform`

## Skills relacionadas
`kubernetes-platform` · `devsecops` · `laravel-platform` · `performance-engineer`
