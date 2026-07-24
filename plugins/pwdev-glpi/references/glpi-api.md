# GLPI — API REST (diagnóstico) e conceitos ITIL

O plugin opera pelo servidor MCP; a API REST direta só é usada para
**diagnóstico de conexão** (dentro do `check-setup.sh`). Alvo: GLPI **10.x**
com API REST habilitada (Setup → General → API).

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
