# PWDEV QA

> [English version](./README.md)

Workflows portáteis de quality assurance para **Claude Code, Codex e Hermes Agent**. O plugin
roteia pedidos de QA, recomenda ferramentas conforme o contexto observado, orienta execução
delimitada, preserva evidência auditável, valida critérios de aceite e exporta relatórios HTML e
PDF offline equivalentes. Inclui 29 skills, 10 comandos e 0 mandatory MCP servers (zero servidores
MCP obrigatórios).

## Instalação manual e portátil

Clone este marketplace e trabalhe a partir da raiz. Os exemplos abaixo carregam o plugin do
checkout e são instruções para o usuário executar deliberadamente. O plugin não instala
automaticamente, não publica nada e não altera configuração pessoal.

### Claude Code

Carregue o diretório local na sessão atual:

```bash
claude --plugin-dir ./plugins/pwdev-qa
```

O Claude expõe os dez wrappers como `/pwdev-qa:<comando>`. A listagem bem-sucedida comprova apenas
descoberta, não o runtime: a Task 24 precisa fazer smoke real que descubra `qa-tooling`, trate um
cenário sem ferramenta e produza um relatório de fixture antes de declarar Claude Code verificado.

### Codex

Abra este checkout como workspace e carregue o pacote local `plugins/pwdev-qa` pelo mecanismo de
plugin local do Codex. O `.codex-plugin/plugin.json` declara `"skills": "./skills/"`; invoque uma
skill descoberta pelo nome, como `$qa-tooling` ou `$qa-strategy`. Não copie para um diretório
pessoal de skills salvo se você escolher explicitamente manter essa instalação separada.

Descobrir o manifest não é smoke. Até uma sessão Codex real comprovar descoberta, tratamento de
ferramenta ausente e geração de relatório, registre o runtime como `unverified`.

### Hermes Agent

Use o plugin local do repositório e inspecione antes de habilitar ou confiar globalmente:

```bash
hermes plugins doctor plugins/pwdev-qa
```

O adaptador registra os mesmos 29 arquivos `SKILL.md` com `pathlib.Path`, sem hook intrusivo. Se
depois você autorizar confiança local no repositório, siga a ajuda da versão instalada do Hermes.
A saída do doctor prova apenas empacotamento; smoke real no Hermes continua obrigatório antes de
declarar o runtime verificado. Executável, autenticação, descoberta ou invocação ausente permanece
`unverified` e deve ser registrado como limitação, nunca simulado.

Nenhum runtime exige servidor MCP. Capacidades distintas podem produzir limitações distintas, e
cada diferença deve continuar explícita.

## Inventário exato

As 29 skills são um roteador, um recomendador de ferramentas, dez workflows e dezessete
especialistas.

| Tipo | Skills |
|---|---|
| Roteador | `qa` |
| Recomendador | `qa-tooling` |
| Workflows | `qa-init`, `qa-strategy`, `qa-test`, `qa-explore`, `qa-bug`, `qa-regression`, `qa-review`, `qa-release`, `qa-report`, `qa-status` |
| Especialistas | `qa-specialist-accessibility`, `qa-specialist-api`, `qa-specialist-automation`, `qa-specialist-cicd`, `qa-specialist-data`, `qa-specialist-defects`, `qa-specialist-functional`, `qa-specialist-metrics`, `qa-specialist-mobile`, `qa-specialist-performance`, `qa-specialist-production`, `qa-specialist-readiness`, `qa-specialist-regression`, `qa-specialist-requirements`, `qa-specialist-security`, `qa-specialist-strategy`, `qa-specialist-web` |

O Claude Code fornece estes 10 comandos:

| Comando | Finalidade |
|---|---|
| `/pwdev-qa:init` | Inspeciona o contexto e estabelece um workspace de QA delimitado. |
| `/pwdev-qa:strategy` | Define escopo, riscos, cobertura de aceite e abordagem. |
| `/pwdev-qa:test` | Executa um contrato autorizado e preserva resultados. |
| `/pwdev-qa:explore` | Conduz teste exploratório delimitado. |
| `/pwdev-qa:bug` | Reproduz e documenta defeito; correção do produto exige pedido separado. |
| `/pwdev-qa:regression` | Seleciona e executa regressão baseada em risco. |
| `/pwdev-qa:review` | Revisa evidência e prontidão sem inventar execução. |
| `/pwdev-qa:release` | Avalia prontidão de release contra gates explícitos. |
| `/pwdev-qa:report` | Exporta a execução normalizada já registrada. |
| `/pwdev-qa:status` | Resume o estado registrado sem descartar nem alterar dados. |

## Recomendação de ferramentas

`qa-tooling` é uma skill de recomendação, não um instalador. A partir de stack, superfície,
runtime/OS, ferramentas instaladas, CI, orçamento, licença e restrições de dados observados, ela
informa finalidade, disponibilidade (`available`, `missing` ou `unverified`), evidence (evidência)
da detecção, pré-requisitos, custo/licença verificados, uma alternative (alternativa) e o motivo.
Ferramenta ausente nunca vira execução fictícia nem provoca auto-install. Comandos,
compatibilidade, licença e custo atuais exigem fontes oficiais datadas.

Para Web/UI exploratório, `playwright-cli` é opção explícita. A resolução local oficial é:

```bash
npx --no-install playwright --version
npx playwright cli
```

O primeiro comando detecta Playwright local sem baixar; a presença do `npx` isoladamente não é
evidência. A alternativa global já instalada é `playwright-cli` (por exemplo,
`playwright-cli --version`). Use sessão de QA isolada, refs observadas e screenshots revisadas;
não reutilize perfis pessoais nem exporte cookies/storage. Para suites repetíveis/CI, prefira
Playwright Test. Traces e vídeos não fazem parte da allowlist de anexos v1.

## Execução e exportação são distintas

Execution (execução) roda somente um contrato de teste explicitamente autorizado e registra os
resultados. Export acontece depois e consome o manifesto normalizado; reporting não executa
comandos armazenados nem corrige o produto. O exit code da exportação representa publicação,
enquanto a automação lê o parecer QA no modelo JSON.

Resultados de caso e critério são `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN` ou `NOT_APPLICABLE`; o
parecer global é `PASS`, `FAIL` ou `BLOCKED`. Falha vigente comprovada e dentro do escopo implica
`FAIL`. Pendência — ou zero critérios aplicáveis — implica `BLOCKED`. `PASS` exige todos os
critérios aplicáveis aprovados e nenhum defeito vigente dentro do escopo.

Ambos os formatos derivam do mesmo manifesto normalizado e contêm os mesmos IDs e textos de
critério, esperado/observado, referências de evidência, defeitos e parecer:

- HTML é estático offline em UTF-8, sem JavaScript nem recursos remotos.
- PDF é A4, com margens de 18 mm, paginação e rótulos textuais de status.
- A saída fica em `.planning/pwdev-qa/reports/<run-id>/`; diretório de execução existente nunca é
  sobrescrito.

O runtime exige Python >=3.9. A exportação PDF exige `reportlab==4.4.9`. Desenvolvimento e
verificação do PDF usam Python 3.12 com `pypdf==6.10.0` e `pdfplumber==0.11.9`; esses dois pacotes
são dependências de verificação, não da exportação em runtime. Instale dependências somente numa
etapa de gestão de ambiente explicitamente aprovada.

## Limites de evidência, sanitização e autorização

Anexos precisam ser arquivos regulares locais (`regular local files`), com caminhos relativos
confinados à raiz da execução, nunca symlinks. Cada anexo vincula SHA-256, alvo, media type,
tamanho e revisão de sanitização. A v1 aceita texto simples, JSON tratado como texto inerte, PNG e
JPEG. Evidência pending, ausente, alterada ou insegura recebe diagnóstico, não é copiada e impede
`PASS`; schema inválido ou evidência insegura recusa exportação.

A sanitization (sanitização) não pode garantir (`cannot guarantee`) detecção universal de segredo
ou dado pessoal. Padrões conhecidos de credencial são rejeitados, mas revisão semântica continua
obrigatória; imagens exigem revisão visual registrada. Estado synthetic ou reviewed registra ator
e timestamp. Nunca anexe perfis pessoais, cookies, storage ou material de produção não sanitizado.

Os limites geram erro explícito, nunca truncamento silencioso: manifesto de 5 MiB, 1000 criteria
(critérios), 1000 evidence (evidências), 10 MiB por evidência, 100 MiB no conjunto e 20 megapixels
por imagem.

Load (carga), pentest, production (produção) e qualquer efeito externo exigem authorization
(autorização) explícita, identificando alvo, ambiente, métodos, limites, janela, condições de
parada e ator responsável quando aplicável. Correção do produto acontece somente quando pedida
separadamente. Sem autoridade, ferramenta ou acesso real ao runtime, mantenha a ação `NOT_RUN` e
o resultado/parecer `BLOCKED` quando o contrato exigir; nunca alegue smoke não executado.
