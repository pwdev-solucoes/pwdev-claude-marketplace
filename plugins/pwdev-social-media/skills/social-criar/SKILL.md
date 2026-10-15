---
name: social-criar
description: >
  Use quando a pessoa pedir um criativo do começo ao fim — 'cria o criativo da campanha', 'produz as
  peças', 'faz a arte desse post a partir da copy', 'campanha completa', 'criativo end-to-end'.
  Conduz conceito, triagem e confirmação de custo, geração, curadoria, composição opcional no Figma,
  revisão e entrega, despachando os subagentes quando o runtime tem. Não use para um único ativo
  (social-imagem), só carrossel (social-carrossel) ou só revisão (social-revisao).
metadata:
  version: 3.0.0
---

# Produzir criativos de ponta a ponta

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`. Regras: `<plugin-root>/references/anatomia-skill.md`.

## 1. Portões

| Verificar | Se ausente |
|---|---|
| `.claude/pwdev-social-context.md` | parar → `social-contexto` |
| Seção 3 — brand kit | parar → `social-marca` |
| Copy aprovada | parar → plugin `pwdev-copy` |
| `pwdev-media versao` (0.4.0+) | seguir em modo prompt, avisando |
| Chaves (`pwdev-media chaves listar`) | seguir em modo prompt, avisando |
| Figma (seção 2) | opcional — sem ele, composição vira especificação |

Nunca produza arte sobre copy não aprovada.

## 2. Conceito

Subagente `art-director` (ou, sem subagentes, `social-conceito` aqui mesmo). Ele entrega a **triagem
de ativos** e o **prompt de cada ativo a gerar**. Apresente e **espere aprovação** antes de gastar
qualquer crédito.

## 3. Custo

Triagem e estimativa de `social-custo` (`pwdev-media gerar <item> ... --estimar` por ativo):

```
Ativos no conceito:    {{n}}
Eliminados na triagem: {{n}}   ← composição, acervo ou design system
A gerar:               {{n}}
Chamadas previstas:    {{n}} (2 variações por ativo, primeira rodada)
Estimativa:            US$ {{total}} (preços do catálogo de {{data}})
Vídeo:                 {{n}} clipes ← confirmar separado
```

**Espere confirmação explícita.** Sem ela, não avance.

## 4. Gerar

Subagente `asset-generator` (ou `social-imagem` / `social-video` aqui mesmo), com
`pwdev-media gerar ... --confirmar` e a pasta `.pwdev-social/gerados/<AAAA-MM-DD>-<campanha>`. Regra
das 2 variações na primeira rodada.

## 5. Curar

`social-curadoria`. Grade de comparação para aprovação. **Registre a seed da selecionada.**

## 6. Compor

Com Figma conectado: subagente `figma-builder` (ou `social-figma` aqui mesmo). Sem Figma: `social-figma`
entrega especificação de composição em camadas. Vários formatos da mesma peça: `social-formatos`.

## 7. Revisar

Subagente `creative-reviewer` (ou `social-revisao` + `social-alt-text`). REPROVADO volta ao passo 5 ou
6 — não avance.

## 8. Entregar

`social-entrega`. Ofereça `social-vault` para arquivar prompts e seeds. **Nunca publique.**
