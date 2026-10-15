---
name: fumadocs-doctor
description: >
  Use quando um projeto Fumadocs der erro ou comportamento estranho, ou para uma revisão de
  saúde / atualização — 'o build do fumadocs quebrou', 'erro de contexto React no Vite',
  'página não aparece na sidebar', 'estilo do fumadocs sumiu', 'atualizar o fumadocs', 'status
  do fumadocs no projeto'. Diagnostica primeiro em modo somente leitura (scanner determinístico,
  versões, type-check, build, catálogo de armadilhas, documentação oficial) e só aplica a
  correção após aprovação. Não use para instalar do zero (fumadocs-setup), escrever conteúdo
  (fumadocs-content) ou adicionar features (fumadocs-feature).
metadata:
  version: 0.1.0
---

# Diagnóstico do Fumadocs

Somente leitura até o passo 4. Toda hipótese precisa de evidência (saída de comando, linha de
arquivo, página da documentação).

## 1. Levantar o estado

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text
git -C <dir-do-app> status --short
npm view fumadocs-core version; npm view fumadocs-mdx version   # últimas publicadas (só leitura)
```

Pedido de status sem erro → apresente o resumo do scanner, as versões instaladas contra as
publicadas e os achados, e pare.

## 2. Reproduzir

Peça (ou leia) a mensagem de erro completa. Sem ela, reproduza com o comando mais barato que
falha: `<pm> run types:check`, depois `<pm> run build`, por fim o dev server e a URL afetada.
Guarde a saída relevante — não parafraseie o erro.

## 3. Localizar a causa

1. Achados do scanner e `<plugin-root>/references/pitfalls.md` — a maioria dos casos está ali.
2. Mapa do framework em `<plugin-root>/references/frameworks.md` para achar o arquivo envolvido.
3. Documentação oficial (`<plugin-root>/references/docs-access.md`): `search` com a mensagem de
   erro ou o nome da API, depois `get_page` da página correta; FAQs e callouts de aviso primeiro.
4. Versões: API ausente ou tipo divergente costuma ser `fumadocs-core`, `fumadocs-ui` e
   `fumadocs-mdx` fora de sincronia ou código copiado de outra versão — compare com os tipos em
   `node_modules/fumadocs-*/dist`.
5. Ainda sem causa: issues em `https://github.com/fuma-nama/fumadocs/issues` com a mensagem.

## 4. Propor e aplicar

```
CAUSA: {uma frase} — evidência: {saída/arquivo:linha/página}
CORREÇÃO: {arquivos e mudança, ou comando}
RISCO: {o que mais muda}
```

Aplique só após o "sim". Atualização de versão: `fumadocs-core`, `fumadocs-ui` e
`fumadocs-mdx` juntos, lendo antes as notas de versão (`https://github.com/fuma-nama/fumadocs/releases`)
quando o major muda.

## 5. Confirmar

Rode de novo o comando que falhava, depois o scanner e o build. Relate o antes e o depois com
as saídas. Se a correção não resolveu, volte ao passo 3 com a nova evidência — no máximo duas
voltas; depois, apresente o que foi descartado e peça direção ao usuário.

Idioma: responda no idioma do usuário. Caminhos `<plugin-root>/...`, `references/` e
`scripts/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos
dependem do runtime (`<plugin-root>/references/runtime.md`).
