# Plano de ação para quality gates

Este plano orienta adoção incremental e independente de stack. Cada especialização define
suas ferramentas e limiares concretos; este documento define o contrato de evolução.

## Entradas fixadas

Antes da primeira medição, registre em controle de versão tudo que pode mudar o veredito:
versões de runtime e ferramentas, lockfiles, imagens por digest, configurações e conjuntos de
regras, fixtures, seeds e comandos completos. Registre também escopo, riscos, tempo máximo de
feedback, donos e fonte da baseline.

Um gate é determinístico quando o mesmo commit, com essas entradas, produz a mesma classe de
resultado. Sinal remoto flutuante pode informar o relatório, mas não bloquear a promoção.

## Fase 0 — Inventário e contrato

**Responsável:** liderança técnica com donos das stacks e do CI.

**Entradas:** arquitetura observada, riscos, comandos existentes, restrições de tempo e
ambientes suportados.

**Ações:** listar cada candidato a gate; definir dono, comando, entradas fixadas, saída
esperada, condição de falha e custo; separar falha do produto de falha da infraestrutura.

**Saídas:** inventário versionado, política de bloqueio proposta e plano de medição.

**Critério de promoção:** todos os gates candidatos têm contrato reproduzível, dono e forma
de diagnóstico; lacunas estão explicitamente registradas.

## Fase 1 — Observação e baseline

**Responsável:** donos das stacks analisam sinais; plataforma CI mede execução.

**Entradas:** inventário aprovado e configurações fixadas da Fase 0.

**Ações:** executar sem bloquear; medir duração, instabilidade, falsos positivos e problemas
existentes; revisar achados e produzir uma baseline versionada.

**Saídas:** relatório de calibração, baseline revisada e classificação dos gates aptos.

**Critério de promoção:** resultados são repetíveis, acionáveis e cabem no orçamento de
feedback acordado; falsos positivos possuem correção ou exclusão justificada.

## Fase 2 — Bloqueio de regressões

**Responsável:** donos das stacks corrigem regressões; plataforma CI mantém a execução.

**Entradas:** gates calibrados e baseline versionada da Fase 1.

**Ações:** bloquear problemas introduzidos ou agravados pela mudança; manter a dívida
anterior visível; impedir aumento da baseline. O CI pode comparar ou reduzir a baseline, mas
nunca incluir nela novos problemas automaticamente.

**Saídas:** política de zero regressão ativa, evidência por execução e processo de exceção.

**Critério de promoção:** o bloqueio é estável, falhas apontam correção concreta e exceções
não viraram caminho normal de entrega.

## Fase 3 — Ratchet e consolidação

**Responsável:** liderança técnica aprova metas; donos das stacks executam a redução.

**Entradas:** histórico da Fase 2, capacidade do time e riscos priorizados.

**Ações:** aprovar reduções graduais da baseline, versionar cada novo patamar e remover
exceções vencidas. Mudanças de patamar passam por revisão humana e nunca são inferidas pelo CI.

**Saídas:** baseline decrescente, metas rastreáveis e conjunto mínimo de gates consolidado.

**Critério de promoção:** redução sustentada sem aumento relevante de instabilidade, tempo
de feedback ou exceções. A partir daqui, novas metas entram por revisão periódica.

## Responsáveis

| Papel | Responsabilidade |
|---|---|
| Liderança técnica | Aprovar risco, política, baseline, ratchet e exceções relevantes |
| Dono da stack | Selecionar e manter verificadores, regras, fixtures e diagnósticos |
| Plataforma CI | Garantir ambiente reproduzível, evidência, tempo limite e disponibilidade |
| Autor da mudança | Corrigir regressão ou solicitar exceção fundamentada |

Uma pessoa pode acumular papéis, mas cada responsabilidade deve ter um nome ou equipe.

## Exceções

Toda exceção registra gate, escopo mínimo, justificativa, risco aceito, aprovador, dono da
correção, data de expiração e evidência associada. Exceção expirada volta a bloquear. Não
edite a baseline para ocultar uma exceção e não desligue o gate globalmente para liberar uma
mudança isolada.

## SonarQube opcional

SonarQube pode agregar sinais e histórico. Para participar do caminho bloqueante, fixe e
controle a versão do servidor, a versão do scanner, o Quality Profile, o Quality Gate e todos
os parâmetros de scanner que alterem o resultado. Se qualquer item for remoto e flutuante,
mantenha o resultado informativo e preserve verificadores locais determinísticos como fonte
do bloqueio.

## Métricas de eficácia

Acompanhe por gate e por fase:

- regressões detectadas antes do merge e escapes após o merge;
- taxa de falsos positivos e execuções instáveis;
- tempo de feedback e impacto no tempo total do pipeline;
- idade, quantidade e frequência de exceções;
- tamanho e velocidade de redução da baseline;
- tempo entre falha e correção.

Revise tendências em cadência acordada. Uma métrica isolada não autoriza afrouxar o gate:
mudança de regra exige diagnóstico, responsável, revisão e registro da decisão.

## Autorização e mudança

Este plano descreve alterações; não autoriza instalar dependências, editar pipelines ou
executar mutações externas. Antes de qualquer uma dessas ações, apresente o comando ou diff,
efeito, ambiente, alvo, reversão e blast radius, e obtenha autorização explícita.
