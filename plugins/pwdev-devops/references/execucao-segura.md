# Execução Segura — contrato do plugin

**O arquivo mais importante deste plugin.** Toda skill obedece a este contrato.
Um plugin de copy que erra escreve texto ruim. Um plugin de DevOps que erra
derruba produção.

---

## Postura

```
LEITURA      livre, sem confirmação
MUTAÇÃO      confirmação explícita, com o comando exato à vista
DESTRUTIVO   confirmação + o usuário digita o alvo
```

---

## Classificação

Antes de executar qualquer comando, classifique. Na dúvida, **trate como
mutação** — errar para o lado seguro é gratuito, o contrário não.

### Leitura — pode rodar
```
kubectl get|describe|logs|top|explain
aws  ... describe-*|list-*|get-*
docker ps|images|inspect|logs
psql  SELECT, EXPLAIN, \d, pg_stat_*
systemctl status · journalctl · ss · df · top
terraform plan|show|validate · nginx -t
git log|diff|status
```

### Mutação — exige confirmação
```
kubectl apply|scale|rollout|patch|label|cordon|drain
aws  ... create-*|update-*|put-*|modify-*|attach-*
docker run|build|push|stop|restart
psql  INSERT, UPDATE, CREATE, ALTER, REINDEX, VACUUM FULL
systemctl start|stop|restart|enable · nginx -s reload
terraform apply · ansible-playbook
```

### Destrutivo — confirmação reforçada
```
kubectl delete · aws ... delete-*|terminate-*
docker rm|rmi|system prune
psql  DROP, TRUNCATE, DELETE sem WHERE
terraform destroy · rm -rf · mkfs · dd
DROP INDEX em produção · ALTER TABLE em tabela grande
```

---

## Protocolo de confirmação

### Mutação
Apresente **antes** de executar:

```
⚠ MUTAÇÃO

Comando:   {{comando exato, copiável}}
Ambiente:  {{prod | staging | dev}}  ← se não souber, diga que não sabe
Alvo:      {{cluster / conta / host / banco}}
Efeito:    {{o que muda}}
Reversível: sim — {{como}} | não
Blast radius: {{o que mais é afetado}}

Confirma?
```

Só execute após "sim" explícito. **"Pode seguir" dito três mensagens antes não
vale para este comando.** Confirmação é por comando, não por sessão.

### Destrutivo
Além do acima, peça que o usuário **digite o nome do alvo**:

```
🛑 DESTRUTIVO — IRREVERSÍVEL

{{comando}}
Vai remover: {{lista explícita do que some}}
Backup existe? {{sim, de {{data}} | NÃO VERIFICADO | não}}

Para confirmar, digite o nome do alvo: ____
```

Se o backup não foi verificado, **diga isso e ofereça verificar antes**.

---

## Ambiente

Detectar ambiente é a parte que mais causa acidente. Nunca infira por palpite.

| Fonte | Confiança |
|---|---|
| Seção 2 do contexto (mapeamento explícito) | alta |
| `kubectl config current-context` batendo com o mapa | alta |
| `aws sts get-caller-identity` batendo com o mapa | alta |
| Nome contendo "prod" / "prd" | **média — não basta sozinho** |
| Palpite pelo nome do recurso | **nenhuma — não use** |

**Se não conseguir determinar o ambiente com confiança alta, trate como
produção.** Diga que não conseguiu determinar e peça confirmação.

---

## Proibido sempre

Estes não são executados nem com confirmação. Entregue o comando e o
procedimento; quem roda é o humano.

- Rotação ou revogação de credencial em produção
- `terraform destroy` em ambiente de produção
- `DROP DATABASE`, `DROP SCHEMA`, `TRUNCATE` em produção
- Alteração de regra de segurança que amplie exposição (Security Group 0.0.0.0/0,
  NetworkPolicy permissiva, IAM com `*`)
- Desabilitar backup, log de auditoria, GuardDuty ou alarme
- `kubectl delete` de namespace, PVC ou StatefulSet em produção
- Operação em recurso que outro time é dono, sem aval registrado
- Qualquer comando durante incidente ativo sem o coordenador aprovar

---

## Guard script

`${CLAUDE_PLUGIN_ROOT}/scripts/guard.sh` é a segunda barreira, independente da
instrução da skill:

```bash
guard.sh --check "kubectl delete pod x"     # classifica e bloqueia
guard.sh --check "kubectl get pods"          # libera
guard.sh --check "terraform apply" --confirm # exige --confirm explícito
```

A barreira que importa é a conversa antes. O script existe porque instrução
falha e trava não.

---

## Ordem de diagnóstico

Durante incidente, a pressa é o que causa o segundo incidente.

```
1. OBSERVAR    métricas, logs, eventos — só leitura
2. HIPÓTESE    o que explica todos os sintomas?
3. VALIDAR     leitura que confirma ou derruba a hipótese
4. PROPOR      comando exato + efeito + reversão
5. CONFIRMAR   humano aprova
6. EXECUTAR    um comando por vez
7. VERIFICAR   o sintoma sumiu? o que mais mudou?
```

**Nunca pule do sintoma para o comando.** "Reinicia o pod" sem hipótese resolve
por acidente e apaga a evidência da causa.

---

## Segredos

- **Nunca** imprimir valor de segredo, token, senha ou chave
- `kubectl get secret -o yaml` **expõe base64** — use `describe`, ou decodifique
  só o campo pedido e não ecoe
- Não gravar credencial em arquivo do projeto, log, runbook ou documentação
- Ao documentar, referenciar o **local** do segredo, nunca o valor
- Ao colar saída de comando, revisar se há credencial embutida antes
