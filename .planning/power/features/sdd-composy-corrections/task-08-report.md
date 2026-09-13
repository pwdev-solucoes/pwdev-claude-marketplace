# Task 08 implementation report — offline phase

Status: DONE_WITH_CONCERNS

## Entregue

- CLI offline com matriz dos três runtimes, dois idiomas e seis cenários.
- Orçamento rígido por runtime (máximo 28), timeout padrão de 300 segundos e nenhuma repetição
  automática.
- Fixture Git exclusiva com cópia local do plugin, exclusão de estado operacional/secrets e
  certificados/chaves, recusa de symlinks e cleanup pelo caminho exato criado.
- Sanitização, publicação JSON atômica, statuses fechados e uso indisponível como `null`.
- Cenários comportamentais por fixture: status/sentinelas; init→map→import→next; LOOP de cinco
  estágios; fleet com dois membros e mismatch; handoff durável; evidência negativa/divergência;
  Compose, cmux e merge.
- Registros preservam duração, exit code, result hash, runtime/version, task, worktree, comando e
  recursos mensuráveis; falha de `os.replace` preserva bytes anteriores.
- CLI real expõe `--provider-entry-point production` e `--acknowledge-real-fleet`, mantendo
  `BLOCKED` sem acknowledgement e `NOT_RUN` enquanto o adapter real não for habilitado.
- Fleet real bloqueada sem acknowledgement externo explícito.
- Re-review: handoff offline agora consome artefatos duráveis por adapters Hermes→Codex→Claude→Hermes,
  preservando IDs/gates/evidence e recusando aprovação não sintética ou fora do escopo; mismatch de
  runtime usa diagnóstico canônico.
- Re-review: cópia isolada falha fechada para token/auth, `id_*`, chaves privadas, keystores,
  credenciais e certificados, mantendo somente arquivos explicitamente `.sample`/`.example`.
- Baseline Hermes substituído por registro/discovery comportamental das 17 skills, `Path` nativo
  e falha diagnóstica do bootstrap.
- Referência Hermes alinhada com o vetor nativo e Kanban indisponível.

## TDD e verificação

- RED inicial: ausência de `scripts/sdd_runtime_smoke.py` falhou como esperado.
- Fix round 1 RED: cenário sem recursos/medidas falhou; testes adversariais cobriram symlinks,
  secrets, publicação atômica, preservação de launcher e gate da CLI real.
- GREEN focado: 18/18 testes de harness + Hermes.
- Re-review GREEN focado: 21/21 testes de harness + Hermes; execução offline 36/36 PASS.
- Suíte offline completa: 367/367 testes.
- README/marketplace: 16 plugins e 1/1 teste.
- Shell syntax e `git diff --check`: PASS.

## Correção após re-review offline 2

- `_offline_handoff` agora chama `run()` dos adapters reais em quatro invocações:
  Hermes → Codex → Claude → Hermes. Executáveis fake temporários recebem os vetores
  nativos, leem o artefato durável anterior e emitem JSON Hermes, arquivo final Codex
  ou envelope Claude. Capturas preservam argv/cwd e a origem consumida; os resultados
  validados preservam task/requirement IDs, gate, evidence e aprovação sintética.
- A fixture fleet associa o mesmo member, slug e worktree nas duas execuções.
  Alterar somente o runtime solicitado produz o stderr real
  `sdd-fleet-run: registered fleet member does not match canonical Git worktree registration`.
  O controle com runtime correto passa esse gate e chega ao gate posterior
  `sdd-fleet-run: unsafe phase contract path for task-add`. O runner agrupa identidade
  runtime no gate de registro; não existe mensagem literal `runtime mismatch` nele.
  Nenhum diagnóstico é substituído e nenhum fake provider é invocado nesse teste.
- RED: três regressões novas falharam antes da correção (2 failures, 1 error):
  ausência de capturas, adapter ignorado e stderr fabricado aceito.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke
  tests.test_sdd_composy_runtime_adapters tests.test_sdd_composy_hermes -v`:
  31 testes PASS em 65.771s, incluindo a matriz offline 36/36 e a execução da CLI.
  Os testes detectam a omissão de qualquer uma das quatro chamadas e recusam um
  erro de registro idêntico nos dois lados do controle diferencial.
- Zero inferência real. Task 08 permanece INCOMPLETE; revisão independente e os
  gates humanos aplicáveis não são concedidos por este relatório.

## Entrada real limitada a READ_ONLY

A entrada de produção agora cria uma fixture Git com a cópia local corrigida, inicializa o
idioma pelo helper e solicita ao provider a leitura da skill e execução de status. Usa os
vetores dos adapters locais: Codex troca somente o sandbox para `read-only`; Claude mantém
permissões padrão e carrega `--plugin-dir` local, capturando `stream-json --verbose`;
Hermes exige `--acknowledge-hermes-automation` para seu `-z`, que implicitamente dispensa
aprovações. Diretório temporário não é declarado sandbox.

O resultado compara JSON do helper, hashes dos recursos locais e snapshots antes/depois
incluindo Git, permissões, diretórios e symlinks. PASS também exige testemunho nativo de
execução do helper: evento Codex de comando concluído ou par Claude Bash/tool_result.
Somente resposta final ou hashes narrados não bastam. Hermes `-z` não expõe esse testemunho
no stdout documentado; mesmo uma resposta correta fica `NOT_RUN`/inconclusiva, com a
invocação contabilizada. Falhas preservam stdout/stderr sanitizados e hash no sumário.

Versão usa somente `--version`; autenticação e configuração nativas não são lidas nem
alteradas pelo harness. Uso não disponível permanece null. Outros cenários reais continuam
NOT_RUN e fleet sem acknowledgement continua BLOCKED. Orçamento é consumido imediatamente
antes do processo de inferência; cenário indisponível ou consentimento ausente não gasta chamada.

Comando serial para um idioma (três invocações no máximo, sem retry):

```bash
python3 scripts/sdd_runtime_smoke.py --mode real --runtime all --language pt-BR --scenario read-only --provider-entry-point production --acknowledge-hermes-automation --max-calls-per-runtime 1 --output .planning/power/features/sdd-composy-corrections/runs/real-read-only
```

Nenhuma inferência real foi executada nesta implementação. Autenticação/rede/permissões
continuam dependentes do ambiente de execução. Este incremento não aprova a Task 08 nem
amplia o escopo para lifecycle/fleet.

Verificação local: suíte focada smoke/adapters/Hermes, 36 testes PASS em 73.977s;
após o endurecimento final do parser, três testes focados PASS em 3.000s, incluindo o
novo controle de witness com caminho incorreto/comando falho. `git diff --check`: PASS.
Os executáveis dos testes são fakes locais que de fato executam o helper copiado;
isso é regressão da entrada real, não evidência de inferência remota.
