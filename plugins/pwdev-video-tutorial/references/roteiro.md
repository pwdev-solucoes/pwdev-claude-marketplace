# Storytelling e roteiro

## Estrutura de um tutorial (ou explicativo)

| Momento | Duração | O que faz |
|---|---|---|
| **Gancho** | 5–8 s | o resultado que a pessoa vai conseguir ("em 1 minuto você emite a nota do pedido") |
| **Contexto** | 5–10 s | onde fica e quando usar; pré-requisito se houver ("o pedido precisa estar faturado") |
| **Demonstração** | o grosso | um passo por cena, narração dizendo o que fazer e por quê, na ordem da tela |
| **Resultado** | 5–8 s | mostrar o fim do fluxo funcionando (mensagem de sucesso, registro na lista) |
| **Próximo passo** | 3–5 s | o próximo vídeo da série ou onde tirar dúvida |

Explicativo de funcionalidade troca a demonstração por "o que é → como funciona → exemplo".
Novidade: gancho → antes/depois → onde encontrar.

## Regras de narração

- Fala de gente: segunda pessoa ("clique em…", "você vai ver…"), frases curtas, uma ação por frase.
- Nome dos botões e menus **exatamente** como na tela, entre aspas na fala escrita.
- Narração de uma cena cobre as ações dela: se a cena tem 3 ações, a fala descreve as 3 enquanto
  acontecem (uma cena com tela parada > 3 s depois da fala gera aviso no `conferir`).
- 2,5 a 3 palavras por segundo (a voz local fala ~2,8). Uma cena de 5 s tem ~14 palavras.
- Nada que a tela não mostre. Nada de número, preço ou prazo que não esteja no sistema.

## roteiro.json (`pwdev-roteiro-tutorial/1`)

```json
{
  "schema": "pwdev-roteiro-tutorial/1",
  "video_id": "V01",
  "titulo": "Como cadastrar um cliente",
  "resumo": "Cadastro de cliente pessoa física pelo menu Clientes.",
  "url_base": "https://homologacao.exemplo.com.br",
  "viewport": {"largura": 1920, "altura": 1080},
  "mascarar": ["#cpf", "[name=email]"],
  "cenas": [
    {"id": "C01", "capitulo": {"titulo": "Cadastrar cliente", "descricao": "Em menos de um minuto"},
     "narracao": "Neste vídeo você vai cadastrar um cliente novo.",
     "acoes": [{"tipo": "ir", "valor": "/clientes"}]},
    {"id": "C02", "narracao": "Clique em \"Novo cliente\" para abrir o formulário.",
     "acoes": [{"tipo": "clicar", "alvo": "getByRole('button', { name: 'Novo cliente' })", "nota": "Novo cliente"}]},
    {"id": "C03", "narracao": "Preencha o nome e clique em \"Salvar\".",
     "acoes": [{"tipo": "preencher", "alvo": "getByLabel('Nome')", "valor": "Maria Exemplo", "ficticio": true},
               {"tipo": "clicar", "alvo": "getByRole('button', { name: 'Salvar' })"}]}
  ]
}
```

| Ação | Campos | Efeito |
|---|---|---|
| `ir` | `valor` (caminho ou URL) | abre a página e espera a rede assentar |
| `clicar` · `passar` · `destacar` | `alvo`, `nota` opcional | contorno laranja + nota; clica, passa o mouse ou só destaca |
| `preencher` | `alvo`, `valor`, `ficticio` | digita com ritmo humano |
| `selecionar` | `alvo`, `valor` | escolhe opção |
| `pressionar` | `valor` (`Enter`, `Tab`…) | tecla |
| `rolar` | `valor` (px) | rola a página |
| `esperar` | `valor` (ms) | pausa |

Toda ação aceita `pausa` (ms, padrão 700) depois dela. `alvo` é um localizador `getBy…(…)` ou um
seletor CSS; o validador recusa qualquer outra coisa.

**Dado pessoal:** campo de e-mail, CPF, telefone, senha, cartão ou endereço só aceita valor com
`"ficticio": true` ou seletor listado em `mascarar` (que borra o campo na gravação).

```bash
python3 '<plugin-root>/scripts/tutorial.py' validar '<TUT>/<video>/roteiro.json'
```

Junto com o JSON, escreva `roteiro.md` para a pessoa aprovar: tabela cena · fala · o que acontece na
tela · duração estimada.
