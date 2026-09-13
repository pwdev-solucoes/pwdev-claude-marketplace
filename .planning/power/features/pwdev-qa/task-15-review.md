# Revisão independente — Task 15

## SPEC

FAIL

Run ID, colisão, componentes symlink, cópia revalidada, allowlist pública, comandos inertes,
partial exclusivo e integração real funcionam no caminho exercitado. A publicação final,
porém, não mantém o vínculo com o path nominal nem revalida o conteúdo do pacote depois do
rename, e o teste de validade do PDF aceita bytes estruturalmente inválidos.

## QUALITY

FAIL

O uso de descritores, `O_NOFOLLOW`, cópias exclusivas e rename no-replace é consistente, mas a
fronteira final de sucesso está subtestada: os testes cobrem colisão antes do rename, não troca
da raiz ou dos artefatos após ele, e usam deliberadamente um falso PDF que não é parseável.

## FINDINGS

### Important — Troca da raiz ou do PDF após o rename ainda pode resultar em `complete`

Em `plugins/pwdev-qa/scripts/qa_report.py:426-436`, `_verify_published_identity` reabre apenas o
diretório pelo `reports_fd` retido e compara seu inode. Em `:504-512`, o resultado reconstrói
`output_dir` pelo path nominal sem verificar que esse path ainda aponta para a mesma raiz nem
que os arquivos publicados ainda correspondem ao staging validado.

Dois probes frescos comprovaram o impacto:

- ao renomear a raiz `reports` imediatamente antes do rename e criar uma raiz substituta com
  um diretório-sentinel para o run ID, `generate_report` retornou `verdict=PASS` e
  `export_status=complete`; o `output_dir` continha apenas `sentinel`, enquanto o pacote real
  ficou na raiz renomeada;
- ao substituir `report.pdf` por `ATTACKER-PDF` imediatamente após o rename, a função também
  retornou `PASS/complete` e preservou o arquivo atacante como relatório publicado.

Mantenha e verifique a identidade nominal da raiz de relatórios e faça snapshot/reabertura do
inventário e conteúdo publicado, preservando sentinels e falhando explicitamente em qualquer
troca, como já feito no contrato de publicação do renderizador PDF.

### Important — O estágio aceita um arquivo não parseável como PDF completo

Em `plugins/pwdev-qa/scripts/qa_report.py:206-208`, a validação exige somente prefixo `%PDF-` e
um `%%EOF` nos últimos 1.024 bytes. O `fake_pdf` usado pelos testes escreve exatamente
`%PDF-1.4\n%%EOF\n`; `_validate_stage` publica esse arquivo como pacote completo, enquanto
pypdf 6.10.0 em modo estrito o rejeita com `PdfReadError: startxref not found`. Assim, uma
falha/corrupção do renderizador que preserve os dois marcadores viola CA-021 e ainda recebe
exit code 0. Adicione validação estrutural suficiente antes do rename (sem transformar pypdf em
dependência de exportação se o contrato não permitir) e um caso negativo com PDF malformado.

## REVIEW

CHANGES_REQUESTED

### Evidência fresca

- HEAD permaneceu em `fb4905bdc1bacdb5d5e3fc223f4794df831d0b9a`; `git diff --check
  3185b7b..fb4905b` passou.
- Python 3.9.6: `python3 -m unittest -v tests.test_qa_report_cli` — 8 testes, PASS.
- Python 3.12.14 empacotado: `tests.test_qa_report_cli tests.test_qa_pdf` — 18 testes,
  PASS; discovery `test_qa*.py` — 124 testes, PASS.
- Integração real com ReportLab: pacote de 6 páginas publicado, reaberto em pypdf estrito,
  attachment idêntico, campo privado ausente, HTML offline e comando não executado.
- Probes adversariais demonstraram os dois falsos sucessos de troca pós-validação descritos
  acima e a aceitação do PDF sem `startxref`.
- Fixtures temporárias foram autocontidas e removidas; caches gerados pela revisão foram
  removidos.
