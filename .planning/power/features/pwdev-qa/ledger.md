# Power ledger — plan: .planning/power/features/pwdev-qa/plan.md

Created: 2026-09-12T09:34:19Z

## Progress

Task F01-01: complete (commits 5294a06..6f9fe9a, review clean after fix round 1)
Task F01-02: complete (commits 6f9fe9a..5ff4f0d, review clean after fix round 1)

Baseline 2026-09-12: `python3 -m unittest discover -s tests` executou 670 testes em 404.209s; 7 falhas preexistentes antes de qualquer código PWDEV QA.
- 2 falhas `test_flow_claude_compat`: READMEs raiz não contêm `claude -p`.
- 4 falhas `test_marketplace_readmes`: suíte espera formato antigo de seções/inventário.
- 1 falha `test_pwdev_power`: symlink de `power-roadmap-status` ausente no checkout.
Critério de baseline: testes `test_qa_*` devem ficar verdes; regressões novas são bloqueantes; as 7 falhas acima permanecem classificadas separadamente.

### Pre-flight scan

| Par/tarefa | Arquivo ou interface compartilhada | Compatibilidade |
|---|---|---|
| F01-01 -> F01-02/F01-03/F02/F04 | contrato de skill, workflow, safety e artifacts | Consumos nomeiam saídas de F01-01; limitação/autorização preservadas |
| F01-02 -> F04-01/F05-02/F05-03 | `qa-tooling` e contrato de recomendação | campos de disponibilidade e evidência são usados sem instalação automática |
| F01-03 -> F05-01/F05-03 | mappings de runtime | registro e smoke usam os mesmos nomes de runtime |
| F02-01..06 -> F04 | `qa-specialist-*` | prefixo evita colisão com workflows `qa-*` |
| F03-01 -> F03-02..07 | `validate_manifest(data: dict) -> dict` | consumidor recebe manifesto normalizado e preserva extras |
| F03-02 -> F03-03/F03-06 | `inspect_evidence(root, manifest) -> list[dict]` | lista sanitizada; rejeitados não entram em exportação |
| F03-03 -> F03-04/F03-05/F03-06 | `build_report(manifest, evidence) -> dict` | renderizadores não recalculam parecer |
| F03-04/F03-05 -> F03-06/F03-07 | HTML/PDF do mesmo modelo | paridade validada contra a fonte, não apenas entre formatos |
| F03-06 -> F04-05/F05-03 | `generate_report` e CLI | workflow report não executa comandos armazenados |
| F04-01..05 -> F05-01/F05-03 | 10 skills e 10 wrappers | empacotamento conta e descobre nomes exatos |
| F05-01 -> F05-02/F05-03 | 29 skills/manifests | catálogo e smoke verificam o inventário produzido |
| Todas F01-01..F05-03 | texto interno vs Files/Consumes/Produces/Steps | 24 tarefas têm 2-5 arquivos, comando específico, ciclo RED/GREEN e dependências coerentes |

Ruling: o baseline completo já está vermelho por 7 falhas fora do PWDEV QA; conclusão exigirá ausência de novas falhas e registro separado dessas 7. Se estiver errado, uma regressão preexistente poderá permanecer fora do escopo da branch.
Ruling: planos por feature usam IDs locais; briefs e ledger sempre qualificam `Fxx-NN`. Se estiver errado, um status sem prefixo pode ser associado à tarefa incorreta.
Ruling: para `playwright-cli`, a documentação primária consultada em 2026-09-12 substitui o fallback desatualizado da skill local: detectar a instalação local com `npx --no-install playwright --version` e invocar via `npx playwright cli`. Se estiver errado, instalações antigas que expõem outro binário precisarão permanecer `unverified` e usar a alternativa global.
Ruling: sanitização `pending` deve gerar diagnóstico explícito além de impedir cópia e PASS, porque a Global Constraint lista as três consequências. Se estiver errado, o relatório poderá ser mais estrito que o desejado, mas continuará seguro.
Ruling: nesta tarefa de skills Markdown, testes determinísticos devem interpretar a tabela de rotas em fixtures temporárias e comprovar resolução/recusa e ausência de mutação; avaliação do comportamento do modelo permanece no smoke real F05. Se estiver errado, F01 poderá oferecer confiança estrutural insuficiente antes do smoke final.

## Rulings
