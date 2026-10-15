# Explorar o sistema: código + navegação

O vídeo só mostra o que existe e funciona. A exploração cruza duas fontes e anota onde elas
discordam.

## 1. Código (quando a pessoa der acesso ao repositório)

```bash
python3 '<plugin-root>/scripts/tutorial.py' codigo '<raiz-do-codigo>' --saida '<TUT>/codigo.json'
```

Varre, sem executar nada, rotas (Laravel, Next.js app/pages, SvelteKit, React Router, Vue Router,
Django, Rails, Express), links de menu com o texto do link, formulários (campos, rótulos, botões e
campos de dado pessoal) e permissões (`@can`, `can:`, `Gate::define`, `hasRole`…). Ignora
`node_modules`, `vendor`, build e pastas ocultas.

Depois, leia **só o necessário** do código para entender um fluxo: o controller ou a página de uma
rota, as validações do formulário, as mensagens de sucesso e erro, os papéis que enxergam a tela.
Anote o arquivo e a linha de cada afirmação.

## 2. Navegação real com o playwright-cli

Sempre num **ambiente de teste ou homologação** com dados fictícios. Em produção, só leitura e só
com o "sim" da pessoa.

**Login:** a pessoa entra sozinha; a senha nunca passa pela conversa.

```bash
playwright-cli -s=pwdev-tutorial open '<url-de-login>' --persistent   # janela visível
# a pessoa faz o login e avisa; então:
playwright-cli -s=pwdev-tutorial state-save '<TUT>/sessao.json'
```

`sessao.json` tem cookies de acesso: não versione, não compartilhe, apague ao terminar.

**Percurso:** para cada item de menu e cada rota do código que for uma tela:

```bash
playwright-cli -s=pwdev-tutorial goto '<url>'
playwright-cli -s=pwdev-tutorial snapshot --filename='<TUT>/explorar/<tela>.yml'
playwright-cli -s=pwdev-tutorial screenshot --filename='<TUT>/explorar/<tela>.png'
```

Use os refs do snapshot para abrir modais, abas e formulários. Anote o localizador estável de cada
elemento que vai aparecer num vídeo: prefira `getByRole('button', { name: '…' })`,
`getByLabel('…')` e `getByTestId('…')` (gere com `playwright-cli generate-locator e12 --raw`).
**Não envie formulário** na exploração, a não ser em ambiente de teste e com o "sim".

Guarde cada URL visitada (uma por linha) em `<TUT>/visitadas.txt` e compare com o código:

```bash
python3 '<plugin-root>/scripts/tutorial.py' cobertura '<TUT>/codigo.json' --visitadas '<TUT>/visitadas.txt'
```

## 3. Mapa do sistema (`<TUT>/mapa-do-sistema.md`)

| Seção | Conteúdo |
|---|---|
| Visão geral | o que o sistema faz, para quem, em 3 linhas |
| Perfis | papéis e o que cada um enxerga (permissões do código + o que a navegação confirmou) |
| Telas | uma linha por tela: caminho, para que serve, ações principais, captura |
| Fluxos | sequências que geram valor (cadastrar, aprovar, emitir, configurar), com pré-requisitos |
| Campos sensíveis | campos de dado pessoal por tela (vão para `mascarar` nos roteiros) |
| Lacunas | rotas do código não alcançadas na tela; telas sem rota clara; erros e telas quebradas |
| Fontes | arquivo:linha do código e captura de cada afirmação |

Nada no mapa sem fonte. Uma lacuna é uma pergunta para a pessoa, não um palpite.
