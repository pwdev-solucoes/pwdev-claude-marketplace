# Task F05-24 — Quality Review Round 2

## SPEC

PASS

A correção atende aos três findings da revisão anterior. Os READMEs permanecem integrados sem alteração do layout histórico, os cenários possuem cobertura estrutural e semântica para exatamente 10 workflows e 17 especialistas, o fixture HTML/PDF continua real e os três runtimes permanecem honestamente `UNVERIFIED`. A impossibilidade ambiental de completar CA-003 está registrada como `BLOCKED`, conforme o brief.

## QUALITY

PASS

Os oráculos agora vinculam identidade, campos e evidências por linha. As mutações exatas da rodada anterior e a reintrodução de estado composto foram rejeitadas em probes independentes. As suítes focada e completa, o validador dos READMEs e o diff-check passaram.

## FINDINGS

### Blocker

Nenhum.

### Major

1. **ADDRESSED — promoção fabricada de runtime e remoção de evidência detalhada.** `tests/test_qa_scenarios.py:320`

   O resumo agora exige uma linha única por runtime, versão exata, status atual `UNVERIFIED`, campos separados de descoberta, invocação/missing-tool, relatório e limitações, além do agregado `BLOCKED — 0 of 3`. Cada runtime também exige uma seção detalhada com os probes e resultados próprios. A promoção isolada de Codex para `VERIFIED` e a remoção integral da seção Claude foram ambas rejeitadas. O ledger continua coerente: nenhum runtime concluiu descoberta + invocação + relatório na mesma sessão.

2. **ADDRESSED — cenários vinculados semanticamente por workflow e especialista.** `tests/test_qa_scenarios.py:147`

   As tabelas são parseadas com schema fixo, exatamente uma linha por cada um dos 10 workflows e 17 especialistas, sem extras ou duplicatas. Cada linha exige precondições, ações, oracle, segurança/limitação, caminho de evidência existente e tokens semânticos específicos. As destruições de `qa-init` e `qa-specialist-security` que antes sobreviviam foram rejeitadas.

3. **ADDRESSED — resultados de aceite restritos ao enum normativo.** `tests/test_qa_scenarios.py:251`

   O ledger separa `result` de `limitations`, aceita somente `PASS`, `FAIL` ou `BLOCKED` nesta tabela e registra CA-023 como `PASS` com limitação em coluna própria. O relatório foi igualmente corrigido. A mutação que reintroduziu `PASS_WITH_LIMITATION` foi rejeitada.

### Minor

Nenhum.

### Evidência fresca

- Python 3.12, `python -m unittest -v tests.test_qa_scenarios tests.test_readme_marketplace`: 11 testes aprovados.
- Python 3.12, `python -m unittest discover -s tests -p 'test_qa_*.py' -q`: 201 testes aprovados.
- `scripts/validate_readme_plugins.py`: 17 plugins validados nos dois READMEs.
- `git diff --check 513fdf7..9357b0d`: aprovado.
- Mutation probes independentes: promoção falsa de Codex, remoção da evidência Claude, destruição semântica de `qa-init`, destruição semântica de security e estado composto CA-023 — 5/5 rejeitados.
- O teste completo voltou a executar o exporter real e validar HTML/PDF no ambiente Python 3.12 declarado.
- Nenhuma nova alegação de runtime verificado foi introduzida; Claude, Codex e Hermes continuam `UNVERIFIED` por limitações reproduzíveis.

## REVIEW

APPROVED

## ACCEPTANCE

BLOCKED

- CA-001: PASS.
- CA-002: PASS.
- CA-003: BLOCKED — 0/3 runtimes completaram descoberta, invocação e relatório na mesma sessão; nenhuma limitação foi tratada como sucesso.
- CA-004: PASS.
- CA-018: PASS.
- CA-022: PASS.
- CA-023: PASS, com a limitação de invocação dos runtimes registrada separadamente.
- Parecer consolidado: `BLOCKED`, exclusivamente pela pendência ambiental vigente de CA-003; não há falha comprovada aberta nesta rodada.
