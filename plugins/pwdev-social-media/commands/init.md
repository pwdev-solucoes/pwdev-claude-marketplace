---
description: Configura o plugin — Figma, brand kit, formatos ativos, geradores e restrições
argument-hint: "[organização] [--brand para só reextrair o brand kit]"
---

# /pwdev-social-media:init — Configurar

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`. Este comando **sempre** pergunta
ou confirma o idioma.

## STEP 1 — Estado
Se `.claude/pwdev-social-context.md` existe: resuma e pergunte o que atualizar.
Nunca sobrescreva sem confirmar.
Se não existe: copie o template.

## STEP 2 — Figma primeiro
Sem os links do design system e do arquivo de campanhas, tudo opera degradado.
Resolva a seção 2 antes de qualquer outra coisa.

Verifique se o MCP do Figma responde. Se não, avise que o plugin entregará
especificação em vez de peça montada.

## STEP 3 — Brand kit
Com Figma disponível, invoque `brand-kit` e extraia — não pergunte de memória.
Sem Figma, peça manual de marca ou peças aprovadas e marque como inferido.

## STEP 4 — Demais seções
Identidade (peça também as referências **rejeitadas**), formatos ativos,
geradores, repositórios, restrições, aprovação.

Setor público: pergunte explicitamente. Muda contraste de AA para AA reforçado
e adiciona exigência de identidade institucional.

## STEP 5 — Chaves
Verifique quais variáveis de ambiente existem. **Não peça chave ao usuário e não
grave chave nenhuma** — registre apenas se está configurada.

## STEP 6 — Gravar
Tabela de preenchimento com pendências e o comando que resolve cada uma.
