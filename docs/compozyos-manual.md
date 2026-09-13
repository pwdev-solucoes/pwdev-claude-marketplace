# Manual de uso do CompozyOS

Guia prático para operar o CompozyOS com segurança. Recursos mutáveis exigem confirmação explícita e escopo conhecido.

## 1. Visão geral

O CompozyOS conecta agentes, extensões, Loops, workspaces, rede e evidências. A CLI `compozy` é a interface local; o daemon mantém o estado operacional e expõe a Network Local.

Consulta, validação e execução são etapas diferentes. `--help`, `version` e `status` não comprovam execução bem-sucedida. Aprovações devem estar ligadas ao conteúdo e aos digests aprovados; desconhecidos permanecem `NOT_RUN` ou `BLOCKED`.

## 2. Pré-requisitos e init

```bash
command -v compozy
compozy version
compozy --help
```

O `init` deve detectar dependências e recomendar instalações. Não deve instalar ferramentas, iniciar Docker, abrir navegador ou ativar Network Live automaticamente.

Nunca leia `.env`, tokens, chaves, certificados, cookies ou credenciais.

## 3. Daemon e identidade

```bash
compozy status --json
compozy whoami --json
compozy daemon --help
```

Use `daemon start` somente com autorização. Registre PID, socket, versão, saúde e proprietário. Não pare daemon que não foi iniciado pela execução atual. Se `whoami` retornar `{}`, a identidade humana não está comprovada.

## 4. Network Local, Live e Gateway

Network Local é o padrão para desenvolvimento e testes. Network Live é opcional para conectar ambientes remotos. Gateway e Tailscale são camadas de exposição/conectividade, não pré-requisitos do fluxo local.

Mantenha o Gateway desabilitado por padrão. Tailscale fornece rede privada entre dispositivos autenticados, mas não substitui autorização do CompozyOS.

## 5. Extensions

Uma Extension é um bundle versionado de agentes, skills, templates ou Loops. Prefira bundles resource-only para documentação e validação controlada.

```bash
compozy extension validate <diretorio>
compozy extension dev <diretorio> --workspace <workspace-isolado>
```

`validate` deve ser usado antes de `dev`; registre diretório, revisão, versão, workspace e evidências. Não altere fontes de outros plugins nem substitua `AGENTS.md`.

## 6. Agents

Cada Agent precisa de identidade, permissões e escopo explícitos. Permissão de leitura não implica escrita ou execução. `AGENT.md` deve documentar objetivo, entradas, saídas, limites e erros.

## 7. Loops

Separe validação, criação e execução:

```bash
compozy loop validate --file <loop.yaml> --name <nome> --workspace <workspace>
compozy loop create --file <loop.yaml> --expected-version <versao> --workspace <workspace>
compozy loop run --dry-run --name <nome> --network local --workspace <workspace> --config-file <run-config.yaml>
compozy loop run --name <nome> --network local --workspace <workspace> --config-file <run-config.yaml>
```

Use concorrência, tentativas e janela de ausência de progresso explícitas. IDs do Loop são diferentes dos IDs de aprovação Power.

## 8. Worktrees e Docker Compose

Worktree por feature isola revisão e estado mutável. Docker Compose pode provisionar aplicação e dependências de teste; use nome de projeto e portas diferentes por worktree. Detecte e recomende Docker, sem presumir disponibilidade. Não use `down --volumes`.

## 9. Probes e QA

Probe é um ensaio controlado de comportamento real:

1. confirme versão e sintaxe;
2. valide fixtures, paths, digests e permissões;
3. obtenha aprovação ligada ao snapshot;
4. execute somente argv e escopos aprovados;
5. registre comando, revisão, resultado, exit code e hash.

Ausência de ferramenta ou capacidade obrigatória é `NOT_RUN`/`BLOCKED`, nunca `PASS`.

## 10. Evidências e exportação

Evidências são arquivos regulares confinados ao checkout, com SHA-256, tipo e origem. Exportações HTML/PDF são derivadas da evidência validada e devem registrar versão, fontes, digest do dossier e horário. Exportar não converte `NOT_RUN`, `STALE` ou `ENVIRONMENT_FAILURE` em sucesso.

## 11. Troubleshooting

| Sintoma | Ação |
|---|---|
| CLI ausente | registrar `command -v` e recomendar instalação |
| socket indisponível | repetir `status --json` pelo runtime autorizado |
| identidade vazia | manter gate bloqueado |
| digest divergente | preservar snapshot e reabrir gate |
| path fora do escopo | parar e corrigir o plano |
| Loop sem progresso | respeitar limite e registrar bloqueio |
| Live indisponível | continuar em Network Local quando permitido |

## 12. Checklist

- [ ] versão, revisão e workspace registrados;
- [ ] permissões e escopo conferidos;
- [ ] aprovação ligada aos bytes corretos;
- [ ] testes focados executados com mais de zero testes;
- [ ] evidências têm digest e referências válidas;
- [ ] nenhum segredo exposto ou recurso alheio removido;
- [ ] revisão e verificação independentes concluídas.
