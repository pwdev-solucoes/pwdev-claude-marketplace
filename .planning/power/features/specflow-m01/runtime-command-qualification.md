---
type: COMMAND_QUALIFICATION
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-13T00:30:00Z"
lifecycle:
  status: DRAFT
human_approval: PENDING
sources:
  - resource: .planning/power/features/specflow-m01/plan-amendment-01-runtime-recipe.md
    sha256: 9ffe9c2dd11ce940e13c5f2bcdde0217c7f300b8b8c83ce3e783bd9c41d34f7b
  - resource: tasks/prd-specflow/techspec.md
    sha256: a952198143a3f8b9a97e88331a2fd7bc048c7117a00babcf67025c42cccfd88c
verified: []
---

# M01 — qualificação documental dos comandos

Observação read-only feita no checkout
`/Users/paulosoares/Projetos/skills-ia/pwdev-claude-marketplace/.worktrees/pwdev-composyos`.
Ela qualifica descoberta e sintaxe anunciada pela CLI, não comportamento. Nenhum comando
mutável foi executado; nenhum bundle foi validado; daemon, workspace, extension, Loop,
Run, gate, Docker, browser e Live não foram iniciados, criados, alterados ou removidos.

## Observações frescas

Os hashes são SHA-256 dos bytes emitidos, incluindo newline final. No `status`, a saída
é stderr; stdout foi vazio. Horário da observação: `2026-09-13T00:30:00Z`.

| Comando | Esperado | Observado | Exit | SHA-256 da saída | Conclusão |
|---|---|---|---:|---|---|
| `command -v compozy` | Resolver candidato | `/Users/paulosoares/.local/bin/compozy` | 0 | `2563512952b438d725acf2f22eb75e1419d6683e49bafbeed672edfe5b15ac93` | descoberta PASS; comportamento NOT_RUN |
| `/Users/paulosoares/.local/bin/compozy version` | Informar versão | `compozy 0.3.0-beta.16` | 0 | `6c70f7151561d55c94a8c9f4b21310e9f3d0b48aa862afee217db825933962de` | versão observada; garantias NOT_RUN |
| `/Users/paulosoares/.local/bin/compozy --help` | Listar comandos | anunciou daemon, extension, loop, status, whoami e workspace | 0 | `821900de6a455b80a840ca499e7842fc80e4750b7e83315f7dfba4667c0e5288` | superfície anunciada, não binding |
| `/Users/paulosoares/.local/bin/compozy daemon --help` | Mostrar ações | `start`, `stop` | 0 | `e2fb0a1ef7b826bbab63e6b24b715ff0c97915bb3248326880c2786ebf630e9e` | argv anunciado, não executado |
| `/Users/paulosoares/.local/bin/compozy extension validate --help` | Mostrar sintaxe | `extension validate [directory]`; “without running its code” | 0 | `e9e5a270bf0d857b0e1aaa8ff745aaf19434acab52bc57909ce3c165c8d2b92a` | somente help; bundle não validado |
| `/Users/paulosoares/.local/bin/compozy extension dev --help` | Mostrar sintaxe | `[directory]`, `--workspace`, `--confirm-network-requirement` | 0 | `a7dc66ef8351d33c0f2d92474eb6de737c6d34f6c1903f71b8e4a069ac0507a9` | comando mutável NOT_RUN |
| `/Users/paulosoares/.local/bin/compozy loop validate --help` | Mostrar sintaxe | `--file`, `--name`, `--workspace`; “without saving” | 0 | `627b6f8abcd986aec875f570b8a8c6c7b5ee19a50c6a03d16387d8d5d18d6097` | somente help; definição não validada |
| `/Users/paulosoares/.local/bin/compozy loop create --help` | Mostrar sintaxe | `--file`, `--expected-version`, `--workspace` | 0 | `ab1e07132366c7ef5387716f587e4b278b94bba8e133a32864a1582a9bb6fe73` | comando mutável NOT_RUN |
| `/Users/paulosoares/.local/bin/compozy loop run --help` | Mostrar sintaxe | `--dry-run`, `--name`, `--network`, `--workspace` e budgets via config/input | 0 | `19b36d3dd12e35c01d6c41c32d661f83080fff05bc4c05a06ae39f3fd1bcc93d` | argv anunciado; dry-run e run NOT_RUN |
| `/Users/paulosoares/.local/bin/compozy loop approve --help` | Mostrar sintaxe | `--decision`, `--gate-id`, `--run-id`, `--workspace` | 0 | `82809721eb2094eeaadf4f2861218883121330ae8873d88042d246cd116f626a` | IDs e identidade humana não demonstrados |
| `/Users/paulosoares/.local/bin/compozy status --json` | Consultar status sem efeitos | daemon indisponível em `/Users/paulosoares/.compozy/daemon.sock`; `data_freshness: offline` | 69 | stderr `6d5ec073ef4a7ed55a63760b185ad727b9752a9d54d3f6f3a5c428002e44c6c0`; stdout vazio `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | ambiente indisponível; nenhuma autorização |
| `/Users/paulosoares/.local/bin/compozy whoami --json` | Consultar identidade | `{}` | 0 | `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356` | identidade não demonstrada |

## Limites da qualificação

Help/version/status não provam provider, carregamento, gates humanos, digests,
atomicidade, histórico/retomada, confinamento, observação sem efeitos ou exclusão
mútua. `compozy status --json` falhou porque o daemon socket está indisponível e
`whoami` não forneceu ator. Portanto nenhum `ApprovalRef` pode ser criado e nenhum
CORE/OPT pode ser promovido. O executável e os argv abaixo são propostas para gate
futuro, não autorização operacional.

STATUS: NEEDS_CONTEXT — primeiro o gate humano do TASKS revisado.
