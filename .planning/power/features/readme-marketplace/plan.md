# README Marketplace — Plan
Status: DRAFT
Spec: .planning/power/features/readme-marketplace/spec.md
Updated: 2026-09-09

## Goal

Reestruturar a documentação pública do marketplace para usuários que instalam e usam os plugins.

## File Structure

- `README.md`
- `README.pt-BR.md`
- `scripts/validate_readme_plugins.py`
- `tests/test_readme_marketplace.py`

## Task 01 — Inventário e validador

Complexity: medium
Files: `scripts/validate_readme_plugins.py`, `tests/test_readme_marketplace.py`
Steps:
- [ ] Escrever teste que detecta todos os manifests e exige cada plugin na tabela.
- [ ] Executar o teste e observar a falha inicial.
- [ ] Implementar parser de manifests, versões, links e paridade estrutural.
- [ ] Executar os testes do validador.
- [ ] Commitar.

## Task 02 — README principal em inglês

Complexity: medium
Files: `README.md`
Steps:
- [ ] Escrever instalação, seleção por objetivo e primeiro uso.
- [ ] Reorganizar tabela e guias por categoria.
- [ ] Remover changelog da entrada principal ou mover para seção secundária.
- [ ] Executar o validador.
- [ ] Commitar.

## Task 03 — README pt-BR equivalente

Complexity: medium
Files: `README.pt-BR.md`
Steps:
- [ ] Replicar a estrutura pública em português.
- [ ] Preservar nomes de plugins, comandos, IDs e versões.
- [ ] Executar o validador de paridade.
- [ ] Commitar.

## Task 04 — Revisão final

Complexity: low
Files: `README.md`, `README.pt-BR.md`, `scripts/validate_readme_plugins.py`, `tests/test_readme_marketplace.py`
Steps:
- [ ] Executar a suíte específica e o validador.
- [ ] Verificar links relativos e diff.
- [ ] Registrar evidências e limitações.
- [ ] Commitar.
