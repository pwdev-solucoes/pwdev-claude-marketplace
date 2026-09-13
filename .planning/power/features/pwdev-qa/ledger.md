# Power ledger — plan: .planning/power/features/pwdev-qa/plan.md

Created: 2026-09-12T09:34:19Z

## Progress

Task F01-01: complete (commits 5294a06..6f9fe9a, review clean after fix round 1)
Task F01-02: complete (commits 6f9fe9a..5ff4f0d, review clean after fix round 1)
Task F01-03: complete (commits e4e111c..cc9429a, review clean)
Task F02-04: complete (commits 135985c..99fcc6b, review clean)
Task F02-05: fix round 1 — finding Important confirmado; cenários mobile `READY` omitem pré-requisitos obrigatórios de host, build/signing e ADB/conectividade.
Task F02-05: complete (commits 3846a91..8db1e6b, review clean after fix round 1)
Task F02-06: fix round 1 — dois findings Important confirmados; cenários `READY` de dados e performance registram observações que exigem autorização sem carregar o escopo autorizativo completo.
Task F02-06: complete (commits 8db1e6b..ec76425, review clean after fix round 1)
Task F02-07: fix round 1 — finding Important confirmado; pentest `READY` omite owner, rate limit, stop conditions e cleanup.
Task F02-07: minor (deferred): cenário de quarentena flaky registra owner e investigação, mas não explicita rationale e expiração delimitada.
Task F02-07: complete (commits a0407c1..67872a7, review clean after fix round 1; 1 Minor deferred)
Task F02-08: fix round 1 — quatro findings Important confirmados sobre rastreabilidade de regressão, precedência do parecer após reteste, fronteira de produção e prevenção determinística.
Task F02-08: complete (commits 67872a7..323a985, review clean after fix round 1)
Task F02-09: fix round 1 — dois findings Important confirmados; métrica positiva sem proveniência/IDs/evidências e decisão humana de prontidão sem actor/authority/scope/rationale/timestamp.
Task F02-09: complete (commits 323a985..e69099b, review clean after fix round 1)
Task F03-10: complete (commits a67f9a2..8a5185e, review clean)
Task F03-11: fix round 1 — 1 Critical e 2 Important confirmados: TOCTOU em diretório pai, imagem truncada aceita e credencial JSON escapada não detectada.
Task F03-11: fix round 2 — Critical e revalidação ADDRESSED; permanecem variantes Important de paleta PNG incompatível com bit depth e chave JSON duplicada pós-decode.
Task F03-11: complete (commits 8a5185e..b0412ba, review clean after fix rounds 1-2)
Task F03-12: fix round 1 — três findings Important confirmados: N/A válido tratado como pendência, PASS de reteste supersedido encerra defeito e marcadores de escopo contraditórios excluem falha.
Task F03-12: complete (commits 80286c2..f6fb6a4, review clean after fix round 1)
Task F03-13: complete (commits f6fb6a4..4f6c179, review clean)
Task F03-14: fix round 1 — finding Important confirmado para incorporar imagem verificada com legenda e revalidação segura; 1 Minor de integralidade da fixture deferred.
Task F03-14: minor (deferred): teste 100×2000 não compara o fragmento final que completa os 2.000 caracteres.
Task F03-14: fix round 2 — incorporação ADDRESSED, mas raiz de confinamento segue symlink e publicação re-resolve pathname.
Task F03-14: fix round 3 — raiz symlink/redirecionamento ADDRESSED, mas troca de nome publica no inode preservado e retorna sucesso sem arquivo no destino nominal.
Task F03-14: complete (commits 4f6c179..3185b7b, review clean after fix rounds 1-3; 1 Minor deferred)
Task F03-15: fix round 1 — dois findings Important confirmados: troca pós-rename permite falso `complete` e PDF não parseável passa por checagem superficial de marcadores.
Task F03-15: fix round 2 — PDF semântico permanece aberto; finding de troca pós-último snapshot exige definir ponto de linearização porque nenhum número finito de releituras torna pathname imutável.
Task F03-15: fix round 3 — semântica pós-commit ADDRESSED; atestação ainda é pré-rename e parser não valida recursivamente filhos/ciclos de `/Pages`.
Task F03-15: fix round 4 — atestação pré-commit e árvore recursiva avançaram; restaram semântica pós-syscall e dicionários `/Page` lexicalmente malformados.
Task F03-15: fix round 5 — semântica de commit ADDRESSED; corrigindo os valores elementares inválidos restantes do parser PDF.
Task F03-15: complete (commits 3185b7b..dcd096e, review clean after fix rounds 1-5)
Task F03-16: fix round 1 — finding Important confirmado no oráculo E2E: cardinalidade/truncamento/expected-observed não eram comprovados integralmente.
Task F03-16: complete (commits dcd096e..b8b5ab6, review clean after fix round 1; Python 3.9 sem dependências dev classificado como limitação de ambiente)
Task F04-17: fix round 1 — finding Major confirmado: os templates podiam descartar objetivo/intenção e autorização; teste de portabilidade Hermes também não protegia quatro tokens exclusivos do wrapper Claude.
Task F04-17: complete (commits eee8386..7017f18, review clean after fix round 1)
Task F04-18: fix round 1 — dois findings Major confirmados: Procedures não consumiam especialistas F02 e o oráculo aceitava perda dessa integração, reordenação do output e contradição da regra anti-PASS em exploração.
Task F04-18: complete (commits ac9f1e0..bc9b23d, review clean after fix round 1)
Task F04-19: fix round 1 — finding Major confirmado: o oráculo não protegia a cadeia completa de impacto, o reteste no mesmo caso/alvo/ramo, a independência entre severidade e prioridade e a ausência de pendências para PASS.
Task F04-19: complete (commits 6060a73..f8ddbcd, review clean after fix round 1)
Task F04-20: fix round 1 — dois findings Major confirmados: o oráculo não protegia todas as superfícies somente leitura nem os cinco campos auditáveis e todas as pendências que impedem PASS.
Task F04-20: fix round 2 — contradições adversativas `may mutate` e `Never record` ainda passavam por regexes baseadas apenas em vocabulário.
Task F04-20: complete (commits 16c5c78..b070d5f, review clean after fix rounds 1-2)
Task F04-21: fix round 1 — dois findings Major confirmados: oráculos aceitavam execução armazenada, segundo export, bypass de evidência e mutações/descartes no status.
Task F04-21: fix round 2 — variantes flexionadas e passivas de skip/discard ainda escapavam do scanner de contradições.
Task F04-21: complete (commits 75f7335..98046b8, review clean after fix rounds 1-2)

Baseline 2026-09-12: `python3 -m unittest discover -s tests` executou 670 testes em 404.209s; 7 falhas preexistentes antes de qualquer código PWDEV QA.
- 2 falhas `test_flow_claude_compat`: READMEs raiz não contêm `claude -p`.
- 4 falhas `test_marketplace_readmes`: suíte espera formato antigo de seções/inventário.
- 1 falha `test_pwdev_power`: symlink de `power-roadmap-status` ausente no checkout.
Critério de baseline: testes `test_qa_*` devem ficar verdes; regressões novas são bloqueantes; as 7 falhas acima permanecem classificadas separadamente.

### Pre-flight scan

| Par/tarefa | Arquivo ou interface compartilhada | Compatibilidade |
|---|---|---|
| F01-01 -> F01-02/F01-03/F02/F04 | contrato de skill, workflow, safety e artifacts | Consumos nomeiam saídas de F01-01; limitação/autorização preservadas |
| F01-02 -> F04-17/F05-23/F05-24 | `qa-tooling` e contrato de recomendação | campos de disponibilidade e evidência são usados sem instalação automática |
| F01-03 -> F05-22/F05-24 | mappings de runtime | registro e smoke usam os mesmos nomes de runtime |
| F02-04..09 -> F04 | `qa-specialist-*` | prefixo evita colisão com workflows `qa-*` |
| F03-10 -> F03-11..16 | `validate_manifest(data: dict) -> dict` | consumidor recebe manifesto normalizado e preserva extras |
| F03-11 -> F03-12/F03-15 | `inspect_evidence(root, manifest) -> list[dict]` | lista sanitizada; rejeitados não entram em exportação |
| F03-12 -> F03-13/F03-14/F03-15 | `build_report(manifest, evidence) -> dict` | renderizadores não recalculam parecer |
| F03-13/F03-14 -> F03-15/F03-16 | HTML/PDF do mesmo modelo | paridade validada contra a fonte, não apenas entre formatos |
| F03-15 -> F04-21/F05-24 | `generate_report` e CLI | workflow report não executa comandos armazenados |
| F04-17..21 -> F05-22/F05-24 | 10 skills e 10 wrappers | empacotamento conta e descobre nomes exatos |
| F05-22 -> F05-23/F05-24 | 29 skills/manifests | catálogo e smoke verificam o inventário produzido |
| Todas F01-01..F05-24 | texto interno vs Files/Consumes/Produces/Steps | 24 tarefas têm 2-5 arquivos, comando específico, ciclo RED/GREEN e dependências coerentes |

Ruling: o baseline completo já está vermelho por 7 falhas fora do PWDEV QA; conclusão exigirá ausência de novas falhas e registro separado dessas 7. Se estiver errado, uma regressão preexistente poderá permanecer fora do escopo da branch.
Ruling: planos por feature usam IDs locais; briefs e ledger sempre qualificam `Fxx-NN`. Se estiver errado, um status sem prefixo pode ser associado à tarefa incorreta.
Ruling: para `playwright-cli`, a documentação primária consultada em 2026-09-12 substitui o fallback desatualizado da skill local: detectar a instalação local com `npx --no-install playwright --version` e invocar via `npx playwright cli`. Se estiver errado, instalações antigas que expõem outro binário precisarão permanecer `unverified` e usar a alternativa global.
Ruling: IDs locais repetidos entre os cinco planos colidem nos nomes `task-NN-{brief,report,review}.md`; renumerar tarefas globalmente de 01 a 24, preservando ordem, conteúdo e rastreabilidade. Se estiver errado, referências externas aos IDs locais F02-01..F05-03 precisarão ser atualizadas para os IDs globais.
Ruling: sanitização `pending` deve gerar diagnóstico explícito além de impedir cópia e PASS, porque a Global Constraint lista as três consequências. Se estiver errado, o relatório poderá ser mais estrito que o desejado, mas continuará seguro.
Ruling: nesta tarefa de skills Markdown, testes determinísticos devem interpretar a tabela de rotas em fixtures temporárias e comprovar resolução/recusa e ausência de mutação; avaliação do comportamento do modelo permanece no smoke real F05. Se estiver errado, F01 poderá oferecer confiança estrutural insuficiente antes do smoke final.
Ruling: prontidão mobile `READY` exige probe positivo separado para todas as dimensões da plataforma — host, SDK/toolchain, ADB/conectividade quando aplicável, driver, build/signing, device e service; ausência ou probe não executado resulta em `BLOCKED` ou `unverified`, nunca `READY`. Se estiver errado, a referência poderá bloquear uma exploração consultiva parcial, mas não alegará capacidade de execução inexistente.
Ruling: cenários de referência que exibem mutação ou carga observada só podem ser `READY` quando a própria linha carrega autorização rastreável e completa; para dados, alvo/dataset/limite de escrita/evidência, e para performance, alvo/limites/ambiente/janela. Se estiver errado, as tabelas ficarão mais verbosas, mas impedirão que autorização genérica seja confundida com permissão de execução.
Ruling: pentest `READY` exige que a própria linha de cenário carregue owner, rate limit, stop conditions e cleanup, além de alvo, métodos, ambiente e janela; cada omissão mantém execução `NOT_RUN` e outcome `BLOCKED`. Se estiver errado, o cenário ficará mais estrito que uma proposta apenas consultiva, mas não confundirá autorização parcial com prontidão operacional.
Ruling: percentual só é publicável quando target/contrato/coleta, IDs incluídos/excluídos e evidências sustentam numerador e denominador; decisão humana só habilita o cenário de readiness quando actor, authority, scope, rationale e timestamp estão explícitos e separados do parecer. Se estiver errado, a coleta exigirá mais metadados, mas evitará métricas e aprovações não auditáveis.
Ruling: inspeção de evidência deve atravessar componentes por descritores confinados com `O_NOFOLLOW`; `copy_allowed` representa apenas elegibilidade daquele snapshot e exige reabertura/revalidação segura no momento da cópia. Imagens precisam de estrutura completa e JSON deve ser sanitizado semanticamente após decode. Se estiver errado, alguns anexos válidos incomuns poderão ser recusados, mas nenhum arquivo inseguro será promovido por pathname, truncamento ou escape textual.
Ruling: `NOT_APPLICABLE` válido e justificado fora dos critérios aplicáveis não é pendência; reteste só encerra defeito se for o terminal válido do mesmo caso; marcadores de escopo contraditórios bloqueiam em vez de excluir o defeito. Se estiver errado, dispensas legítimas poderão exigir validação adicional, mas o parecer não retrocederá a tentativa antiga nem esconderá falha por ambiguidade.
Ruling: publicação `complete` exige identidade nominal estável da raiz e snapshot pós-rename de inventário/conteúdo igual ao staging; o PDF deve ter estrutura xref/trailer/startxref coerente, não apenas marcadores. Se estiver errado, um PDF válido com estrutura não produzida pelo ReportLab poderá ser recusado, mas corrupção e troca de pacote não serão declaradas completas.
Ruling: a paridade E2E precisa validar cardinalidade exata e uma representação integral de cada texto longo, incluindo o token parcial final, contra HTML, pypdf e pdfplumber; expected/observed devem ser confirmados separadamente em cada formato. Se estiver errado, a normalização de extração poderá ser mais rígida que alguns PDFs equivalentes, mas truncamento real não passará despercebido.
Ruling: o rename no-replace é o ponto de commit da publicação; o retorno deve incluir digest do inventário publicado para revalidação por consumidores. Troca anterior ao commit é erro/colisão; mutação posterior é adulteração externa e não pode ser tornada impossível por releituras finitas do pathname. Se estiver errado, a API precisará mudar para devolver um handle durável ou operar em armazenamento imutável, além do contrato aprovado.
Ruling: imagem só é incorporada a partir do staging do pacote, reaberta e revalidada sob a raiz do destino; a própria raiz deve ser diretório real sem symlink, e criação/substituição do PDF deve permanecer relativa ao mesmo descritor. Se estiver errado, destinos acessados por symlink legítimo serão recusados, mas não haverá escape entre validação e publicação.
Ruling: o PDF incorpora somente imagens `VERIFIED` já revalidadas e copiadas para o diretório temporário do pacote; o renderer reabre o caminho relativo sob `destination.parent`, recusa symlink/mismatch de hash/tamanho/MIME e adiciona legenda com ID. Se estiver errado, a API standalone exigirá staging adicional, mas não reabrirá diretamente um anexo original por pathname não confiável.
Ruling: cenários positivos de regressão, defeitos e produção devem materializar as relações verificáveis que sustentam o estado: IDs change→risk/criterion/defect→case e exclusões; `PASS` após reteste somente com todos os critérios aplicáveis PASS e nenhum outro defeito vigente; fronteira de produção completa por dimensão; causa nomeada e check preventivo com IDs/oráculo/ambiente/pré-requisitos. Se estiver errado, os exemplos ficarão extensos, mas não produzirão `READY`/`PASS` a partir de rótulos genéricos.

## Rulings
