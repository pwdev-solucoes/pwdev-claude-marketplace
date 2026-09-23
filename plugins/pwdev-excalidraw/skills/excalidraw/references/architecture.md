# Arquitetura

Use esta referência quando o pedido for mapear sistemas, componentes, integrações, dados ou limites de deploy.

## Estrutura mínima

- título e objetivo da visão;
- atores e sistemas externos;
- componentes sob controle do projeto;
- fronteiras de propriedade, confiança ou deploy;
- relações e direção do fluxo;
- legenda para confirmado, proposto e desconhecido.

## Disciplina

Baseie entidades e relações no repositório e no pedido atual. Não invente serviços, filas, bancos, APIs ou responsabilidades. Quando a evidência estiver ausente, marque `desconhecido` ou `premissa`.

Prefira contexto de sistema para visão ampla e componentes somente quando o usuário precisar detalhar uma fronteira. Separe arquitetura atual de arquitetura proposta.

## Verificação

Confirme que cada seta tem origem, destino e significado; que integrações externas estão identificadas; e que fatos e propostas não foram misturados.
