# Artefatos `.excalidraw` locais

Use quando o usuário pedir um arquivo editável no repositório ou no filesystem.

## Procedimento

- descubra o caminho desejado antes de escrever;
- verifique se o arquivo já existe;
- confirme antes de substituir um arquivo existente;
- produza JSON `.excalidraw` válido e preserve identificadores quando estiver atualizando;
- não inclua segredos, tokens ou dados privados;
- valide o JSON e informe o caminho exato.

Um arquivo local não prova que o MCP remoto foi usado. Informe separadamente se o artefato foi gerado sem MCP.
