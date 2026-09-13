# GLPI — API REST (diagnóstico) e conceitos ITIL

O plugin opera pelo servidor MCP; a API REST direta só é usada para
**diagnóstico de conexão** (dentro do `check-setup.sh`). O contrato suportado
é GLPI **10.x e 11.x** pela API REST Legacy V1, com a API habilitada em
Setup → General → API e a URL base terminada por `/apirest.php`.

A High-Level API V2 do GLPI 11 (`/api.php`) não é usada nem suportada por
este plugin nesta versão. OAuth2, password grant e authorization-code grant
também estão fora do escopo; o backend comum às duas gerações continua sendo
a Legacy V1.

## Handshake de diagnóstico

```sh
# autentica com o PAT (API token do usuário)
curl -sS -H "Authorization: user_token <PAT>" \
  ${GLPI_APP_TOKEN:+-H "App-Token: $GLPI_APP_TOKEN"} \
  "$GLPI_BASE_URL/initSession"
# → {"session_token":"..."} = ok

# encerra a sessão criada no teste (higiene)
curl -sS -H "Session-Token: <session_token>" "$GLPI_BASE_URL/killSession"
```

O servidor MCP autentica por **PAT direto** em toda chamada
(`Authorization: user_token`), sem manter sessão.

## Diagnóstico de geração

Depois do `initSession`, o diagnóstico consulta `getGlpiConfig` uma vez e
classifica somente uma versão reconhecível:

- major 10: geração `10`, suportada pela Legacy V1;
- major 11: geração `11`, suportada pela Legacy V1;
- outro major numérico: geração `unsupported`, com aviso e continuidade;
- falha HTTP, permissão negada, payload desconhecido ou campo de versão
  ausente: geração `unknown`, sem bloquear as tools.

`unsupported` e `unknown` não são equivalentes: o primeiro indica que um
major numérico foi identificado fora de 10/11; o segundo indica que a geração
não pôde ser determinada. Em ambos os casos, o diagnóstico preserva o acesso
às tools para que a compatibilidade real da Legacy V1 seja avaliada durante o
uso. O payload bruto de `getGlpiConfig` não deve ser exibido nem registrado.

## Erros comuns da API

| Resposta | Causa | Ação |
|---|---|---|
| `ERROR_GLPI_LOGIN` / 401 | PAT inválido ou não regenerado | Preferências → Chaves de acesso remoto → API token → regenerar |
| `ERROR_APP_TOKEN_PARAMETERS_MISSING` | Instância exige App-Token (API client registrado) | `export GLPI_APP_TOKEN=...` |
| HTML em vez de JSON | URL sem `/apirest.php` ou API desabilitada | Corrigir URL; habilitar em Setup → General → API |
| `ERROR_RIGHT_MISSING` | Perfil do usuário sem permissão no recurso | Ajustar perfil no GLPI |

## Conceitos ITIL do GLPI (para não errar nas mutações)

- **urgency** (1–5): quão rápido o *solicitante* precisa da resolução.
- **impact** (1–5): abrangência do problema (uma pessoa ↔ organização toda).
- **priority**: **calculada pelo GLPI** pela matriz urgency×impact — por isso
  nunca se define priority diretamente; proponha urgency e impact.
- **Ciclo de status**: `new → assigned → planned → waiting → solved → closed`.
  `solved` = solução registrada aguardando aprovação do solicitante;
  `closed` = encerrado (transição feita pelo GLPI, não por update direto).
- **Followup vs Solution**: followup é acompanhamento/comunicação (não muda
  status); solution é a resposta definitiva (ITILSolution → status SOLVED).
- **Entidade**: escopo organizacional; tickets, usuários e ativos pertencem a
  entidades — em instâncias multi-entidade, sempre confirme a entidade alvo.
- **Categoria ITIL** (`itilcategories_id`): classifica o chamado; base da
  triagem e do roteamento para grupos de atendimento.
