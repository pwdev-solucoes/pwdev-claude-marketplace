# Idioma

Conversa, relatórios e mensagens seguem o idioma da pessoa: pt-BR por padrão, inglês se ela
escrever em inglês. Para decidir:

1. `.planning/config.json` → campo `lang` (compartilhado com os outros plugins pwdev), se existir.
2. Senão, o idioma do pedido.
3. Ambíguo: pt-BR.

A saída da CLI `pwdev-media` é em pt-BR; traduza o resumo quando a conversa for em inglês.
**Nunca traduza** id de item do catálogo, nome de modelo, slug, comando, campo JSON nem
mensagem de erro de API: cite como veio.
