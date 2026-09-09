# README Marketplace — Design
Status: APPROVED
Source: revisão aprovada do README e inventário dos plugins
Updated: 2026-09-09

## Problem

O README atual mistura apresentação, changelog e detalhes internos, dificultando que usuários
encontrem o plugin correto, instalem-no e executem o primeiro comando. Há risco de divergência
entre versões/capacidades documentadas e os manifests reais.

## Approach

Reorganizar a documentação para descoberta e uso, mantendo inglês e pt-BR estruturalmente
equivalentes. A tabela de plugins será validada contra `.claude-plugin/plugin.json` e cada plugin
será classificado por objetivo principal.

## Decisions

### DEC-001 — Usuário como público primário

- Options: contribuidores; usuários; ambos com entrada orientada a usuários.
- Choice: usuários como público primário e contribuição como seção secundária.
- Why: reduz o tempo até instalação e primeiro uso.
- Trade-off: detalhes históricos saem da página inicial.
- Reversible: sim, em seção de histórico separada.

### DEC-002 — Dois READMEs equivalentes

- Options: somente inglês; somente pt-BR; inglês e pt-BR com mesma estrutura.
- Choice: inglês e pt-BR equivalentes.
- Why: preserva acessibilidade sem duplicar decisões de navegação.
- Trade-off: alterações devem ser sincronizadas.
- Reversible: sim.

### DEC-003 — Manifesto como fonte de versão

- Options: tabela manual; manifesto Claude; manifesto Codex.
- Choice: manifesto Claude com validação cruzada do Codex.
- Why: elimina versões inventadas e expõe compatibilidade real.
- Trade-off: descrições precisam ser curadas para linguagem de usuário.
- Reversible: sim.

## Interfaces

- `README.md` e `README.pt-BR.md`: índice público do marketplace.
- `plugins/*/.claude-plugin/plugin.json`: nome, descrição e versão canônicos.
- `plugins/*/.codex-plugin/plugin.json`: compatibilidade Codex.
- `scripts/validate_readme_plugins.py`: verificação de cobertura e versões.

## Constraints

- Não remover plugins existentes.
- Não alterar manifestos neste trabalho.
- Manter links relativos válidos para cada diretório de plugin.
- Manter licença Apache-2.0.
- Preservar comandos reais publicados por cada plugin.

## Out of scope

- Alterar código ou skills dos plugins.
- Criar novos plugins.
- Publicar release ou alterar versão.

## Acceptance criteria

- Usuário encontra instalação e primeiro uso nos primeiros blocos do README.
- Todos os plugins presentes no marketplace aparecem uma vez na tabela.
- Nome, versão e link de cada linha correspondem aos manifests.
- README inglês e pt-BR possuem as mesmas seções principais.
- Validador automatizado falha quando plugin, versão ou link divergir.
