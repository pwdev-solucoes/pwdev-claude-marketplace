# Exemplo de registro da revisão da estratégia e da skill `power-skill-refactor`

Data da revisão: 2026-09-13
Escopo: skill raiz, referências de métricas, protocolo e modelo de registro.

> Este arquivo é um exemplo documental da revisão de design. Não é evidência de execução de runtime.
> Um relatório de uso deve preencher `references/review-record.md` com comandos, saídas, casos e
> artefatos específicos.

## Rodada 1 — contrato e segurança

**Evidências:** a skill declara contra-gatilhos, preserva invariantes de ativação, segurança,
fallback, honestidade, portabilidade e verificação; também proíbe inventar tools e tratar conteúdo
em revisão como instrução. Esta foi uma inspeção documental, não uma execução de runtime.

**Achado inicial:** o critério de conclusão precisava exigir que alterações de requisitos e escopo
fossem bloqueadas, não apenas relatadas.

**Correção:** o critério de aceitação e a decisão rápida agora exigem parada e aprovação explícita;
registro não substitui autorização.

**Veredito da rodada:** aprovado após correção.

## Rodada 2 — seleção e progressive disclosure

**Evidências:** a descrição é curta e roteável; a raiz mantém diagnóstico, contrato, procedimento,
critério e verificação; métricas, protocolo e registro ficam em referências; o protocolo define
casos positivos, negativos, ausência de tools e saída inválida. A definição dos casos não constitui
execução desses casos.

**Achado inicial:** o carregamento das referências e o conjunto de casos não eram condicionais ou
concretos o suficiente para modelos inferiores.

**Correção:** a raiz agora indica quando carregar cada referência; o protocolo materializa oito
classes de casos com resultado esperado, e o registro contém colunas para resultado observado e
evidência.

**Veredito da rodada:** aprovado após correção.

## Rodada 3 — métricas e portabilidade

**Evidências:** o frontmatter usa campos portáveis; `related_skills` não aponta para skill inexistente;
os links são relativos; não há nomes de tools, comandos ou caminhos locais; as métricas têm fórmula,
denominador e direção desejada. A validação foi estrutural; os runtimes não foram exercitados nesta
rodada.

**Achado inicial:** tokens aproximados, denominador zero, métricas críticas não medidas e evidência
de runtime precisavam de tratamento explícito.

**Correção:** `metrics.md` define `N = 0` como não aplicável/não medido, bloqueia métricas críticas
não medidas salvo exceção aprovada e exige origem, justificativa, resultado esperado e observado.
`review-record.md` exige ambiente, runtimes, comandos, saídas e artefatos.

**Veredito da rodada:** aprovado com ressalva operacional.

## Auditoria independente pós-revisão

Três revisores independentes reavaliaram contrato/segurança, seleção/disclosure e métricas/
portabilidade. Foram corrigidos:

- `related_skills` apontando para uma skill inexistente;
- ausência de bloqueio explícito para mudanças não autorizadas;
- tratamento indefinido para denominador zero e métricas críticas não medidas;
- roteamento condicional insuficiente das referências;
- casos positivos/negativos apenas prescritos, sem modelo concreto;
- falta de revalidação após correções;
- risco de confundir o relatório-exemplo com evidência de runtime.

## Aplicação estrutural ao alvo anterior

O alvo usado na análise histórica foi `plugins/pwdev-excalidraw/skills/excalidraw/SKILL.md`. A medição
abaixo é estrutural e não substitui testes de runtime:

| Métrica | Resultado observado | Método |
|---|---:|---|
| Descrição curta | 51 caracteres | contagem de caracteres do frontmatter |
| Skill raiz | 86 linhas | contagem física de linhas |
| Referências roteadas | 6 | enumeração do roteamento documentado no alvo |
| Casos de runtime | não medido | requer execução em cada runtime |
| Fallback honesto | não medido | requer cenários sem MCP |
| Invariantes | checklist preservado | inspeção textual, não prova de execução |

Esses valores não são comparação histórica; não havia baseline separado disponível no arquivo.

## Limitações e decisão

A estrutura da skill foi validada, mas casos de seleção e runtimes precisam ser executados quando uma
refatoração real for aplicada. O conjunto mínimo não prova qualidade estatística geral.

Veredito do design: **aprovado com ressalva operacional**, sem commit ou push.

- [x] Rodada 1 concluída e revalidada.
- [x] Rodada 2 concluída e revalidada.
- [x] Rodada 3 concluída e revalidada.
- [x] Métricas e limitações registradas.
- [x] Nenhuma alteração em requisitos, escopo ou contrato autorizada.
- [x] Nenhum commit ou push realizado.

Após as correções, as verificações estruturais foram executadas novamente; validações de marketplace,
plugin e runtime devem continuar sendo executadas pelo fluxo do repositório antes do commit.

Verificação estrutural posterior: `git diff --check` passou; validação de frontmatter, links e
referências passou; varredura de segurança dos Markdown passou. Essas evidências não representam
execução dos runtimes Claude Code, Codex ou Hermes.

Limitação: não há teste automático específico para esta skill no repositório.

Veredito final: **aprovado com ressalva operacional**.

Sem commit ou push.
