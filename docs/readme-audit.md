# Auditoria dos READMEs dos plugins

Auditoria executada em 2026-09-09 contra os 16 manifests do marketplace.

## Resultado

Todos os plugins possuem `README.md` e `README.pt-BR.md`. O catálogo principal e as versões
estão validados automaticamente por `scripts/validate_readme_plugins.py`.

## Padronização pendente

Os READMEs individuais ainda não usam uma estrutura uniforme para as seções de instalação,
primeiro uso e segurança. Alguns plugins documentam esses assuntos em prosa ou em português,
sem títulos equivalentes; outros focam apenas na referência técnica.

## Próxima melhoria recomendada

Adicionar a cada README, nessa ordem:

1. Instalação;
2. Primeiro uso;
3. Comandos principais;
4. Permissões, integrações e segurança;
5. Compatibilidade de runtime;
6. Link para a versão em `pt-BR` ou inglês.

Essa melhoria não altera plugins nem comandos; apenas uniformiza a experiência de descoberta.

## Avisos atuais

O validador aceita títulos equivalentes, mas registra avisos quando a documentação não possui
um título explícito de segurança ou setup. Esses avisos não bloqueiam a publicação porque alguns
plugins concentram essas orientações em `references/`, contratos de runtime ou seções de operação.
