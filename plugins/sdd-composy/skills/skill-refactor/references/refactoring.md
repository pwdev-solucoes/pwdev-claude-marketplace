---
okf_version: "0.2"
type: protocol
title: "Refatoração portátil de skills"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
sources:
  - resource: "docs/skill-refactoring-guide.md"
    sha256: "b044b3d3246dca295fb93c8e7da094a541b200c262fdc57ad4077fde0c7c60c5"
    context: "Caminho no repositório de origem; esta referência é uma adaptação portátil, não uma cópia integral."
  - resource: "https://claude.com/plugins/skill-creator"
  - resource: "https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra"
verified: []
---

# Protocolo de refatoração

## Contrato e preparação

Registre alvos, resultado esperado, perfis consumidores, perfil executor e
verificações conhecidas. Reutilize informações já fornecidas. Mantenha separadas
as mudanças autorizadas e sugestões para outras skills ou regras do ambiente.
Uma revisão não autoriza modificar arquivos; uma refatoração solicitada exige
entregar a alteração, salvo impedimento concreto.

Leia `SKILL.md` e apenas recursos relevantes ao fluxo alterado. Mapeie gatilhos
legítimos, requisitos obrigatórios, formato de saída, permissões, dependências
e condições de conclusão. Identifique duplicação, contradição, leitura
incondicional, descrição ampla demais e procedimentos sem finalidade aparente.

Antes de editar, preserve o estado observado dos arquivos-alvo, incluindo alterações
não commitadas. Use um diretório novo em uma localização de artefatos permitida
pelo projeto ou escolhida pelo usuário. Copie somente arquivos regulares
necessários, sem segredos, links simbólicos ou diretórios de configuração.
Se o alvo estiver instalado em cache, for somente leitura ou for symlink,
prepare uma candidata em local gravável autorizado e informe sua localização;
não altere o original nem atravesse o link sem resolver a autorização.

## Refatoração que preserva o comportamento

1. Torne `description` uma capacidade acompanhada de condições concretas de uso.
   Preserve os casos legítimos, inclusive formulações sem o nome da skill.
2. Mantenha no núcleo objetivo, invariantes e limites necessários antes da ação.
   Uma regra obrigatória não pode depender de uma referência que o agente talvez
   não leia. Explique o motivo de orientações que precisam de julgamento.
3. Extraia detalhes de domínio ou ferramenta para referências com condições claras
   de leitura. Agrupe por fluxo; evite fragmentação que multiplique consultas.
4. Consolide repetições em uma fonte de verdade. Preserve nome, recursos, campos
   desconhecidos, `paths`, integrações e metadados que pertençam ao runtime-alvo.
5. Converta procedimentos repetitivos em recursos reutilizáveis somente se fizerem
   parte do escopo. Scripts novos precisam de verificação adequada; não os crie
   apenas para reduzir a contagem de linhas do Markdown.
6. Compare o antes/depois com os requisitos e execute os comandos pertinentes.
   Corrija links, roteamento e perdas de comportamento antes de entregar.

O limite de contexto é orientativo, não uma meta de redução arbitrária. Não corte
requisitos para atingir um número de linhas. Preserve a linguagem do alvo e evite
reescrever conteúdo não relacionado à melhoria solicitada.

## Apoio por perfil

| Perfil | Núcleo compartilhado | Apoio adicional |
| --- | --- | --- |
| `lean` — Astra/Fable por política inicial | Resultado, invariantes, referências condicionais, verificação e conclusão | Exemplos somente para ambiguidades importantes |
| `guided` — outros/desconhecidos inicialmente | Exatamente os mesmos requisitos e permissões | Sequência curta, exemplo resolvido, erro frequente e checklist |

Para consumidores mistos, acrescente uma referência guiada na própria skill-alvo
quando necessária e inclua no núcleo uma condição explícita para carregá-la.
Modelo desconhecido usa esse apoio; seleção explícita prevalece. Não dependa
da identidade do modelo executor para decidir quais consumidores serão atendidos.
Se o usuário pedir apenas um perfil, não acrescente recursos para modelos fora
desse escopo. O executor deve registrar como resolveu cada seleção.

No perfil executor `guided`, use esta sequência curta:

- Liste o que precisa permanecer verdadeiro após a alteração.
- Relacione cada trecho movido ou removido à regra que o substitui.
- Edite descrição e núcleo; depois ajuste referências.
- Confira os requisitos, links, metadados e exemplos positivos/negativos.
- Entregue o resultado e classifique a evidência realmente obtida.

O perfil executor `lean` usa o contrato e essas mesmas verificações com liberdade
para organizar as etapas. Nenhum perfil ganha autorização extra.

## Verificação e entrega

Valide a entrada de runtime com as regras da plataforma-alvo. Um validador de
outro ecossistema que rejeite um campo legítimo não autoriza removê-lo.
Confira caminhos relativos a partir do arquivo que os referencia, ausência de
dependência em caminhos pessoais e preservação dos arquivos não relacionados.

Se houver verificações prévias, rode as aplicáveis. Para tarefas objetivas,
prepare 2–3 casos realistas e expectativas sobre conteúdo correto; para tarefas
subjetivas, mostre os artefatos ao usuário com critérios claros. Para rodar ou
interpretar comparações, leia [avaliação](evaluation.md).

Preserve candidatas e baseline após falhas. Não execute restauração ampla, nem
declare aprovação humana a partir de silêncio, arquivo existente ou nota de modelo.

Grave um relatório curto fora do núcleo da skill-alvo, no local de artefatos
permitido pelo projeto. Use OKF v0.2 nos documentos narrativos: `type`,
`generated.by`, `generated.at` com fuso, `lifecycle.status`, `sources` como lista
de objetos com `resource`, e eventos `verified` apenas para verificações realizadas.
Inclua caminhos e hashes de evidências regulares confinadas ao workspace.
Use dados reais; não gere eventos de aprovação humana ou horários fictícios.

O relatório contém: alvos e baseline, perfis, mudanças, requisitos preservados,
comandos/resultados, modelos realmente executados, medições disponíveis e próximos
passos necessários. Uma revisão pode estar editada e validada estaticamente sem
ter sido comparada em todos os modelos; declare essa diferença.

## Fronteira entre Agent Skills e OKF

`SKILL.md` usa o frontmatter nativo do runtime. Nesta skill, proveniência fica em
`metadata`, seguindo a convenção das skills existentes. Os documentos de referência
e relatórios usam OKF na raiz. Não declare que `SKILL.md` possui uma exceção no
validador OKF: ele não a implementa. Valide cada tipo com seu validador e reporte
essa fronteira. Nos alvos, preserve o contrato que já estiver em uso.
