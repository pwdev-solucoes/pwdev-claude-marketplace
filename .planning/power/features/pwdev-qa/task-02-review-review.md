# Task 02 — re-review do fix round 1

Data: 2026-09-12
Range revisado: `eeccfc2..5ff4f0d`
Escopo: somente os três findings Important da revisão anterior; HEAD não foi movido.

## Verificação fresca

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_tooling tests.test_qa_core`
  — PASS, 16 testes.
- `git diff --check eeccfc2..5ff4f0d` — PASS.
- O pacote corretivo altera somente os três arquivos de implementação/teste autorizados e o
  relatório da tarefa.
- A linha de `playwright-cli` corrigida pelo controller em `spec.md:117`, fora do pacote,
  confirma `npx --no-install playwright --version` para detecção local e `npx playwright cli`
  como entrada, sem tratar a presença isolada de `npx` como prova da ferramenta.

## Finding 1 — disponibilidade derivada de probes e pré-requisitos observados

**ADDRESSED.** O inventário agora exige `state/result/evidence`; ausência de probe produz
`unverified`, apenas probe negativo explícito da própria ferramenta produz `missing`, e
`available` exige todos os probes requeridos positivos. Os cenários cobrem CLI ausente com
probe negativo, inventário ausente sem evidência fabricada, Appium parcial como `unverified` e
Appium completo compatível com Android como `available`.

## Finding 2 — fonte/data ou `unverified` em claims atuais no output

**ADDRESSED.** As regras normalizadas carregam URL oficial e data nos `prerequisites` de cada
claim de compatibilidade, enquanto versão, custo e licença ficam explicitamente `unverified`.
O teste cruza cada claim `verified` do ledger com a linha correspondente e também valida a
presença da proveniência na linha final de sete campos produzida para Appium Android.

## Finding 3 — fallback local de `playwright-cli`

**ADDRESSED.** A skill agora usa `npx --no-install playwright --version` e documenta
`npx playwright cli`, em coerência com a documentação oficial atual e com o ruling incorporado
à spec. O teste rejeita o literal antigo e confirma que o probe usa `--no-install`; nenhuma
instalação ou execução externa foi introduzida.

## REVIEW

APPROVED. Os três findings Important estão endereçados; nenhum finding desta re-review
permanece aberto.
