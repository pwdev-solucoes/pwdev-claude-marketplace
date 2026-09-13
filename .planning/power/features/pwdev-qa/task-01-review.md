# Task 01 — revisão

Data: 2026-09-12
Range revisado: `5294a06..5b24fc6`
Modo: revisão somente leitura; nenhum subagente; este relatório é o único arquivo produzido.

## SPEC

FAIL

O roteador e os contratos cobrem intenção explícita, rotas indisponíveis, preservação da
governança, autorização, vocabulário de resultados e precedência do parecer. Porém, o contrato
de evidências omite um diagnóstico obrigatório para sanitização pendente, portanto não reproduz
integralmente as Global Constraints exatas do brief.

## QUALITY

FAIL

Verificação fresca:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_core` — PASS, 8 testes.
- `git diff --check 5294a06..5b24fc6` — PASS.
- O pacote altera exatamente os cinco arquivos declarados; HEAD permaneceu em `5b24fc6`.
- A linha inicialmente recebida com `NOT_NOT_USED` era uma transcrição incorreta. A correção
  posterior e o brief integral confirmam `PASS, FAIL, BLOCKED, NOT_RUN, NOT_APPLICABLE` para
  caso/critério e `PASS, FAIL, BLOCKED` para o parecer global; implementação e teste usam os
  literais corretos.

## FINDINGS

### Important — sanitização pendente não exige o diagnóstico obrigatório

Em `plugins/pwdev-qa/references/artifacts.md:23-24`, sanitização `pending` impede cópia e `PASS`,
mas não manda produzir diagnóstico. A regra de diagnóstico em `artifacts.md:57-58` cobre apenas
evidência ausente ou alterada. O brief exige literalmente diagnóstico também quando a
sanitização está pendente. Sem essa instrução, uma implementação posterior pode bloquear o
parecer e omitir a causa observável. Inclua `pending` na obrigação de diagnóstico e adicione uma
asserção específica.

### Important — testes não exercitam os cenários comportamentais do brief

`tests/test_qa_core.py:21-44` não fornece pedidos de review/roteamento nem cria alvo ausente,
diretório ou symlink: apenas procura palavras e linhas da tabela. Do mesmo modo,
`tests/test_qa_core.py:46-58` não demonstra que review/status deixam estado intacto ou que
critérios ausentes/zero aplicáveis resultam em `BLOCKED`; só aplica regex ao Markdown. Assim, os
testes permanecem verdes se todo o comportamento alegado estiver ausente, desde que as frases
esperadas continuem no arquivo. Isso não satisfaz o passo de “teste de comportamento” nem o
Behavior da tarefa. Adicione fixtures/avaliações que exercitem intenção explícita, recusa de
referência inexistente e invariância somente leitura; mantenha o smoke completo de runtimes e
inventário para F05, como planejado.

### Critical

Nenhum.

### Minor

Nenhum.

## REVIEW

CHANGES_REQUESTED

Corrigir os dois findings Important antes de F01-02: tornar obrigatório o diagnóstico para
sanitização pendente e substituir/complementar as asserções textuais por cenários que comprovem
o contrato do roteador e os limites somente leitura. Depois, repetir a suíte focada e o
`diff --check` com evidência fresca.
