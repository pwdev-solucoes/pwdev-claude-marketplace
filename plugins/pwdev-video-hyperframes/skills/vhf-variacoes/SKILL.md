---
name: vhf-variacoes
description: >
  Use quando a pessoa quiser várias saídas do mesmo vídeo — 'faz versões com ganchos diferentes',
  'lote de ganchos', 'versão em 4:5 e 1:1', 'uma versão curta de 15 s', 'teste A/B do começo'.
  Cria projetos irmãos a partir do mesmo corte, troca gancho, formato ou duração, renderiza cada
  um com portão e entrega uma planilha de versões. Não use para editar a versão principal
  (vhf-editar).
metadata:
  version: 0.1.0
---

# Versões e lote de ganchos

Regras: `<plugin-root>/references/regras.md`. Formatos: `pwdev-media formatos listar`.

## 1. Combinar o lote

Uma tabela com a pessoa (ou decida e conte): versão, o que muda (gancho, formato, duração), nome.
Máximo recomendado por rodada: 6 versões.

- **Gancho:** frases de abertura diferentes que **já existem na gravação** (várias tomadas de
  gancho) ou o mesmo gancho com outro `titulo` na tela. Nunca invente uma fala.
- **Formato:** o mesmo plano em outro formato (`feed-4x5`, `feed-1x1`, `youtube-16x9`); confira
  a zona segura e o `origem` do zoom.
- **Duração:** versão curta com um subconjunto de frases.

## 2. Um projeto por versão

Gancho ou duração diferentes mudam o corte: use uma pasta edit por versão
(`<VIDEOS>/edit-<versao>`), com `pwdev-media video montar --frases ...` e `cortar`. Formato diferente
reaproveita o corte. Depois:

```bash
python3 '<plugin-root>/templates/projeto-hf/build.py' novo '<VIDEOS>/<nome>-<versao>' --edit '<EDIT da versão>' --formato <id>
```

Copie e adapte `blocos`, `textos` e `cenas` do projeto principal (tempos mudam se o corte mudou:
recalcule pelas palavras).

## 3. Render e planilha

Renderize cada uma (`build.py render`) e só liste as que passaram. Planilha
`<VIDEOS>/versoes.csv`: `versao,gancho,formato,duracao_s,arquivo,portao`. Resuma em uma tabela de
até 6 linhas.
