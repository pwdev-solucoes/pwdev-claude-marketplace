# Re-revisão focada — Task 14, rodada 3

## SPEC

PASS

O sucesso agora exige que a raiz atualmente nomeada mantenha a identidade validada e que o
arquivo no `destination` nominal seja exatamente o PDF publicado. Trocas de raiz ou do arquivo
final falham explicitamente e preservam conteúdo alheio. A imagem verificada e sua legenda
continuam presentes; a evidência bloqueada continua excluída.

## QUALITY

PASS

A correção combina abertura sem symlink, operações descriptor-relative, snapshot de
dispositivo/inode/tamanho/SHA-256, dupla reabertura do path nominal e remoção condicionada à
identidade do inode publicado. Os testes exercitam os dois swaps e a inspeção fresca não
encontrou regressão funcional, visual ou de atomicidade.

## FINDINGS

### Important original — ADDRESSED

- Raiz symlink é recusada antes da reabertura da evidência.
- Troca da raiz durante a exportação produz erro, preserva o sentinel na raiz substituta e
  remove o PDF somente do inode originalmente retido.
- Troca do arquivo após publicação produz erro e preserva o arquivo atacante porque sua
  identidade não coincide com a do PDF publicado.
- No caminho positivo, `render_pdf` retorna apenas com o PDF exato no `destination` nominal.
- Revalidação de regular file, tamanho, SHA-256, MIME e decodificação completa permanece ativa;
  imagem, legenda e exclusão do anexo bloqueado não regrediram.

O finding Minor da fixture 100×2000 permanece deferred por instrução e não foi reavaliado.

## REVIEW

APPROVED

### Evidência fresca

- HEAD permaneceu em `3185b7b3f93b1ed8d382a1597eadce066c305460`; `git diff --check
  d208b36..3185b7b` passou.
- Python 3.12.14 empacotado com ReportLab 4.4.9, pypdf 6.10.0 e pdfplumber 0.11.9.
- `python3 -m unittest -v tests.test_qa_pdf`: 10 testes, PASS.
- `python3 -m unittest discover -s tests -p 'test_qa_*.py'`: 116 testes, PASS.
- Probes de raiz symlink, troca de raiz e troca pós-publicação do arquivo passaram, com falha
  explícita nos swaps e preservação dos sentinels.
- Probe atômico adicional: SHA-256 divergente preservou o `report.pdf` anterior byte a byte e
  não deixou arquivo temporário.
- PDF positivo temporário: 7 páginas A4, 54.796 bytes, exatamente um `%PDF` e um `%%EOF`, uma
  imagem 480×240 e legenda íntegra em pypdf/pdfplumber; path bloqueado ausente. As sete páginas
  renderizadas por Poppler foram inspecionadas sem clipping, sobreposição ou regressão visual.
- Artefatos temporários e caches gerados pela revisão foram removidos.
