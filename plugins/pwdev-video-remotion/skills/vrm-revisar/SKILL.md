---
name: vrm-revisar
description: >
  Use quando for fechar e entregar a edição ou consertar um trecho — 'renderiza', 'pode exportar',
  'confere antes de entregar', 'o texto entrou atrasado', 'a legenda errou o nome', 'ficou
  estranho em 00:12', 'gera o vídeo final'. Monta o vídeo inteiro, confere com som e em quadros,
  renderiza na versão fixa do Remotion e só entrega com o portão PASSOU. Não use para
  planejar o que aparece (vrm-plano) nem para refazer o corte (vrm-corte).
metadata:
  version: 0.2.0
---

# Revisar, renderizar e entregar

Regras: `<plugin-root>/references/regras.md`. Estúdio: `<plugin-root>/references/estudio.md`.

## 1. Vídeo inteiro

```bash
python3 '<PROJ>/build.py' completo
pwdev-media video projeto '<PROJ>/projeto.json'
python3 '<PROJ>/build.py' checar
```

Corrija todo erro do `check` antes de seguir; avisos, avalie.

## 2. Conferir você primeiro

Toque inteiro no estúdio com som, ou gere quadros (`quadro <segundo>`). Perguntas de
`<plugin-root>/references/modelos.md`. Consertos pontuais:

| Problema | Onde mexer |
|---|---|
| texto entra cedo/tarde | `inicio` no `projeto.json` = tempo da palavra no `cut_timeline.json` |
| nome errado na legenda | `correcoes` no `projeto.json` |
| cobre o rosto | `posicao` do texto ou `origem`/`zoom` do bloco |
| corte com palavra comida | volte ao `vrm-corte` |

## 3. Render (diga quanto leva: ~1 a 3× a duração do vídeo)

```bash
python3 '<PROJ>/build.py' render --qualidade alta
```

Sai `<PROJ>/renders/<nome>.mp4` e o portão roda sozinho. **REPROVOU:** leia os problemas, conserte e
renderize de novo. Nunca entregue reprovado.

## 4. Entrega

Até 5 linhas: onde ficou o arquivo, duração, o que foi feito, suposições e qualquer troca. Lembre
que conteúdo gerado por IA (se houver) deve ser marcado ao publicar. Pare o estúdio
(`build.py estudio --parar`) e atualize `<EDIT>/estado.md`.
