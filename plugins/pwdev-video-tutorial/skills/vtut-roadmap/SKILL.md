---
name: vtut-roadmap
description: >
  Use quando a pessoa quiser planejar a série de vídeos de um sistema — 'cria um roadmap de
  vídeos', 'quais tutoriais devemos gravar', 'trilha de onboarding em vídeo', 'série de vídeos por
  perfil', 'em que ordem gravar'. A partir do mapa do sistema (código + navegação), monta séries,
  vídeos com objetivo, público, pré-requisitos, rotas, duração e prioridade, valida a ordem de
  produção e entrega o roadmap para aprovação. Não use para explorar o sistema (vtut-explorar) nem
  para escrever um roteiro (vtut-roteiro).
metadata:
  version: 0.1.0
---

# Roadmap de vídeos

Método e campos: `<plugin-root>/references/roadmap.md`. Pastas: `<plugin-root>/references/runtime.md`.

## 1. Base

Precisa de `<TUT>/mapa-do-sistema.md`. Sem ele, rode `vtut-explorar` primeiro. Pergunte (se não
souber) quem vai assistir e o objetivo da série: onboarding de cliente, treinamento interno,
central de ajuda, divulgação de novidades.

## 2. Montar

- Séries por necessidade: `onboarding`, por perfil, por módulo, `novidades`.
- Um vídeo por objetivo cumprível; fluxo longo vira vídeos encadeados por pré-requisito.
- Prioridade P1/P2/P3 pelo uso no dia a dia e pelo que mais gera dúvida; se a pessoa tiver dados de
  suporte (chamados, FAQ), use-os e cite.
- Cada vídeo aponta as rotas e capturas do mapa que o sustentam (`fontes`). Nada sem fonte.

Grave `<TUT>/roadmap.json` e valide:

```bash
python3 '<plugin-root>/scripts/tutorial.py' validar '<TUT>/roadmap.json'
```

Corrija até `erros` vazio. A `ordem` devolvida é a ordem de produção.

## 3. Apresentar

`<TUT>/roadmap-videos.md`: uma tabela por série (ordem, título, objetivo, público, duração,
prioridade, depende de), total de vídeos e minutos, e as perguntas abertas. Mostre um resumo e
**espere a aprovação** antes de qualquer roteiro. Depois, siga vídeo a vídeo na ordem com
`vtut-roteiro`, atualizando o `status` de cada um no `roadmap.json`.
