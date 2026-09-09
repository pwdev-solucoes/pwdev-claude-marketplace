# Task 02 — re-review 1

Data: 2026-09-09
Range revisado: `664e314..649c862`
Escopo: somente os quatro findings Important da revisão inicial.
Modo: somente leitura da implementação; este arquivo é o único artefato produzido nesta rodada.

## Veredictos

- SPEC: FAIL
- QUALITY: FAIL

## Baseline e preservação

- HEAD observado antes das verificações: `649c862`.
- Baseline local: `M tests/test_sdd_composy_hermes.py`; `plugins/sdd-composy/scripts/sdd_status.py` estava limpo. O diretório administrativo `.planning/power/features/sdd-composy-corrections/` já estava não rastreado.
- Nenhum arquivo de implementação ou teste foi alterado. Todas as reproduções usaram diretórios temporários.

## Reavaliação dos findings

### ADDRESSED — documentos `pt-BR` permaneciam parcialmente em inglês

`sdd_localization.py` agora fornece documentos estáticos completos para os seis destinos e interpola os valores dinâmicos somente depois. A inicialização temporária em `pt-BR` não encontrou nenhum dos trechos em inglês usados na reprodução inicial em `AGENTS.md`, `CLAUDE.md` ou nas quatro regras. Os valores e placeholders de runtime continuam fora do processo de tradução.

### ADDRESSED — `plan` seguia ancestral symlinkado

`_has_symlink_ancestor()` é aplicado antes de qualquer inspeção do destino. Com `.agents/rules` apontando para um diretório externo, o plano retornou `ancestor symlink` para as quatro regras e não classificou o conteúdo externo como arquivo comum. A nova regressão também instrumenta `Path.read_text` para impedir leitura fora do repositório.

### ADDRESSED — estados incompatíveis com `state.schema.json` eram aceitos

A reprodução original com `active_prd: 123`, `updated_at: "not-a-date"` e `trace.source_event_count: -5` agora produz `_valid_state == False`, `verify().state_ok == False` e rejeição da reaplicação antes de nova publicação. A validação adicionada cobre ainda os padrões nullable, summaries, gate, ator, inteiros estritos e datas relevantes ao schema.

### NOT ADDRESSED — falhas posteriores ainda não reportam publicação parcial

A falha na terceira chamada de `os.link`, exatamente como na reprodução inicial, agora retorna corretamente `ok: false`, `created: ["AGENTS.md", "CLAUDE.md"]` e uma lista `pending` ordenada. Porém o tratamento em `apply()` envolve apenas o loop de criação dos documentos. As publicações seguintes — criação de diretórios, symlink `.claude`, persistência de idioma e publicação de estado — permanecem fora do `try`.

Uma falha injetada em `os.symlink` escapou como `OSError` sem resultado estruturado, deixando todos os sete documentos e diretórios já publicados. Portanto o contrato geral de “falha no meio da publicação” e “reportar publicação parcial com precisão” continua violado para etapas reais da mesma transação. O teste novo cobre apenas a terceira criação de arquivo e não as publicações posteriores.

## Verificações executadas

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v`: PASS, 50 testes em 1,729 s.
- `git diff --check 664e314..649c862`: PASS.
- Reprodução de localização dos seis documentos: PASS para o finding original.
- Reprodução de `.agents/rules` como ancestral symlinkado: PASS, quatro conflitos `ancestor symlink`.
- Reprodução de estado inválido pelo schema: PASS, recusado por validação, verify e reaplicação.
- Reprodução de falha na terceira publicação: PASS, `created` e `pending` exatos.
- Reprodução complementar de falha em `os.symlink`: FAIL, exceção não estruturada e publicação parcial sem relatório.
- `git status --short` após as verificações confirmou a preservação do baseline.

## Contagem residual

- Critical: 0
- Important: 1
- Minor: 0
