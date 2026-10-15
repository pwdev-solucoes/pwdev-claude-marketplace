# Roadmap de vídeos

O roadmap transforma o mapa do sistema numa série planejada: quais vídeos, para quem, em que
ordem. Arquivos: `<TUT>/roadmap.json` (schema `pwdev-roadmap-videos/1`) e `<TUT>/roadmap-videos.md`
(a mesma coisa para a pessoa ler e aprovar).

## Como montar

1. **Séries** pelo jeito como as pessoas aprendem o sistema:
   - `onboarding` — primeiro acesso, navegação, perfil, o mínimo para usar no dia 1;
   - por **perfil** (atendente, gestor, admin) — o que cada papel faz;
   - por **módulo** (clientes, financeiro, relatórios) — referência para consulta;
   - `novidades` — uma funcionalidade nova, curta.
2. **Um vídeo = um objetivo** que a pessoa consegue cumprir ao final ("cadastrar um cliente", não
   "módulo de clientes"). Fluxo longo vira dois vídeos ligados por pré-requisito.
3. **Pré-requisitos** explícitos: "emitir nota" depende de "cadastrar cliente". O validador ordena.
4. **Prioridade**:
   - `P1` — fluxos do dia a dia, de onboarding ou que mais geram dúvida/suporte;
   - `P2` — fluxos frequentes de um perfil específico;
   - `P3` — configurações raras, telas avançadas.
5. **Duração-alvo**: tutorial 60–180 s; explicativo 45–90 s; novidade 20–45 s (9:16 se for para rede).
6. **Lacunas** do mapa viram perguntas no fim do roadmap, não vídeos.

## Campos de cada vídeo

```json
{
  "id": "V03",
  "titulo": "Como emitir uma nota fiscal",
  "serie": "financeiro",
  "tipo": "tutorial",
  "objetivo": "Emitir a nota de um pedido já faturado",
  "publico": "atendente",
  "prerequisitos": ["V01"],
  "rotas": ["/pedidos/{id}", "/notas/nova"],
  "telas": ["pedidos.png", "nova-nota.png"],
  "duracao_alvo_s": 120,
  "formato": "youtube-16x9",
  "prioridade": "P1",
  "status": "planejado",
  "fontes": ["routes/web.php:42", "explorar/nova-nota.yml"]
}
```

`tipo`: `tutorial` · `explicativo` · `onboarding` · `novidade` · `demo`. `status`: `planejado` →
`roteiro` → `gravado` → `publicado`.

```bash
python3 '<plugin-root>/scripts/tutorial.py' validar '<TUT>/roadmap.json'
```

Devolve os erros e a **ordem de produção** (pré-requisitos primeiro, depois prioridade).

## roadmap-videos.md

Uma tabela por série (ordem, id, título, objetivo, público, duração, prioridade, depende de), o
total de vídeos e de minutos, e a lista de lacunas/perguntas. A pessoa aprova o roadmap antes de
qualquer roteiro.
