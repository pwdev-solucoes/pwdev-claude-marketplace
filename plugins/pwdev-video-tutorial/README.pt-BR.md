# PWDEV Video Tutorial

Vídeos explicativos, tutoriais, onboarding e novidades de **sistemas** feitos a partir do sistema
real. A IA lê o código e navega no sistema com o `playwright-cli`, entende telas, fluxos e
permissões, planeja a série de vídeos, escreve os roteiros com storytelling, narra, grava a tela e
monta o vídeo final com legenda e zoom no clique, além de um tutorial em texto com capturas.
Funciona no Claude Code, no Codex e no Hermes Agent.

## Fluxo

```
código + navegação ─▶ mapa do sistema ─▶ roadmap de vídeos ─▶ roteiro ─▶ narração ─▶ gravação
                    ─▶ montagem (legenda, zoom) ─▶ revisão + render ─▶ vídeo + tutorial.md
```

| Comando (Claude Code) | Codex / Hermes | O que faz |
|---|---|---|
| `/pwdev-video-tutorial:init` · `:status` | `$vtut-setup` | prepara playwright-cli, voz local e montagem |
| `:explorar` | `$vtut-explorar` | lê o código e navega no sistema; escreve o mapa |
| `:roadmap` | `$vtut-roadmap` | planeja a série: objetivo, público, ordem, prioridade |
| `:roteiro` | `$vtut-roteiro` | roteiro com storytelling e ações verificadas na tela |
| `:narrar` | `$vtut-narrar` | narração por cena: voz local grátis, sua voz ou ElevenLabs |
| `:gravar` | `$vtut-gravar` | grava a tela executando o roteiro no sistema |
| `:montar` | `$vtut-montar` | vídeo final com legenda e zoom no clique + tutorial em texto |
| `:revisar` | `$vtut-revisar` | confere, renderiza com o portão e entrega |

## Instalação

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace
claude plugin install pwdev-video-tutorial@pwdev-claude-marketplace
```

Numa conversa nova: `/pwdev-video-tutorial:init` (Codex: `$vtut-setup`). Ele instala, sem sudo:
- o `playwright-cli`;
- a voz local em português (Kokoro, num ambiente Python isolado em `~/.pwdev/venvs/tts`);
- o resto que faltar (núcleo `pwdev-media`, ffmpeg).

## Manual de uso

1. **Explorar:** "explora o sistema https://homologacao.minhaempresa.com.br usando o código em
   ~/projetos/erp". Se houver login, uma janela abre e **você** entra. A IA nunca vê a senha.
2. **Roadmap:** "monta um roadmap de vídeos para o atendimento". Você recebe uma tabela por série,
   com ordem de produção e prioridade. Aprove ou ajuste.
3. **Roteiro:** "escreve o roteiro do V02". Você aprova a tabela de cenas: fala, o que aparece e
   segundos.
4. **Narrar, gravar, montar e revisar:** "grava e monta o V02". O vídeo sai em
   `<pasta>/V02/projeto-hf/renders/` e o tutorial em texto em `<pasta>/V02/tutorial.md`.

Cada vídeo mostra **só o que o sistema faz de verdade**: os passos foram executados ao vivo e os
localizadores conferidos.

## Segurança e privacidade

- **Senha:** você faz o login numa janela visível. A sessão fica em `sessao.json` (não versione;
  apague ao terminar a série).
- **Dados pessoais:**
  - campos de e-mail, CPF, telefone, senha, cartão e endereço só aceitam dado fictício ou seletor
    em `mascarar`, que borra o campo na gravação inteira;
  - o validador e a revisão recusam o resto;
  - borrar depois não é aceito.
- **Ambiente:** a gravação deve rodar em homologação. Em produção, só com o seu "sim" e sem enviar
  formulários.
- **Nada sai do computador**, a não ser que você escolha a voz paga (ElevenLabs, com estimativa
  e "sim").

## Para quem desenvolve

```bash
python3 -m unittest tests.test_pwdev_video_tutorial
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_tutorial   # + gravação real com playwright-cli
claude plugin validate plugins/pwdev-video-tutorial
hermes plugins doctor --ci plugins/pwdev-video-tutorial
```

Formatos dos arquivos: [`references/roadmap.md`](./references/roadmap.md) e
[`references/roteiro.md`](./references/roteiro.md); exemplos em `templates/`.

## Licença

Apache-2.0.
