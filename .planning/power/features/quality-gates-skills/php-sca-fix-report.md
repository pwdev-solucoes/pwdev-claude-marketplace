# Relatório da correção — SCA PHP determinístico

Data: 2026-09-12
Commit: `1cbae09`
Escopo commitado: `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md`

## Correção

O gate SCA bloqueante de PHP agora usa SBOM CycloneDX reproduzível gerada a partir de
`composer.lock`, Composer e gerador fixados, e Trivy fixado por digest. A execução está vinculada
explicitamente ao modo offline com `--offline-scan`, `--skip-db-update` e
`TRIVY_DB_CACHE_DIR`. O artefato imutável da DB deve ser verificado contra
`TRIVY_DB_ARTIFACT_SHA256`; variável, DB ou SBOM ausente e digest divergente são falha de
infraestrutura. `composer audit`, por consultar o registry, permanece apenas informativo.

## Evidência focada

- RED: `python3 /tmp/assert_php_sca_contract.py` falhou porque o contrato anterior não continha
  SBOM CycloneDX, binding de cache/digest nem flags offline.
- GREEN: a mesma asserção passou após a edição.
- Validador oficial: `PYTHONPATH=/tmp/quality-gates-pyyaml python3
  /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/quick_validate.py
  plugins/pwdev-devops/skills/quality-gates-php` — PASS (`Skill is valid!`).
- README focado: `python3 -m unittest tests.test_readme_marketplace` — PASS (1 teste).
- Higiene do diff: `git diff --check` — PASS.
- Commit contém somente a skill PHP: `1cbae09` (`14 insertions`, `1 deletion`).

## Observação fora do escopo

`python3 -m unittest tests.test_marketplace_readmes` também foi tentado por engano e apresentou
quatro falhas preexistentes de inventário nos READMEs para 16 plugins. Esse módulo não é o teste
focado registrado para a feature, não toca o contrato SCA PHP e não foi tratado como sucesso.
