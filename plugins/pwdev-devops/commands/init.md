---
description: Mapeia a plataforma — contas, clusters, ambientes, bancos e hosts; define o que é produção
argument-hint: "[organização]"
---

# /pwdev-devops:init

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando sempre pergunta.

## STEP 1 — Mapeamento de ambiente (primeiro, sempre)
Sem ele o plugin trata tudo como produção. Colete de fato:

```bash
aws sts get-caller-identity          # por perfil
kubectl config get-contexts
```

Monte a tabela ambiente → conta → contexto → host → banco.
**Nome contendo "prod" não basta** — exija o identificador real.

## STEP 2 — Inventário
Contas · clusters · bancos · hosts · domínios · repositórios · janela de
manutenção · quem é dono do quê.

## STEP 3 — Operação
Quem aprova mudança em produção · canal de incidente · onde vivem os runbooks ·
SLO por serviço · retenção de backup.

## STEP 4 — Ferramentas
`${CLAUDE_PLUGIN_ROOT}/scripts/check-tools.sh`. Registre. Ausente = consultivo.

## STEP 5 — Gravar
`.claude/pwdev-devops-context.md` + tabela de pendências.

**Nunca grave credencial.** Registre o local do segredo, nunca o valor.
