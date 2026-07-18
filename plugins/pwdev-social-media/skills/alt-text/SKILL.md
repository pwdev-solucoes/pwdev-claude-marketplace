---
name: alt-text
description: >
  Escreve texto alternativo e descrição de imagem para peças de rede social.
  Use quando o usuário disser "alt text", "texto alternativo", "descrição da
  imagem", "acessibilidade da peça", "descrever para leitor de tela", ou
  automaticamente antes de qualquer publicação. Obrigatório em todas as peças —
  em carrossel, um por slide.
metadata:
  version: 1.0.0
---

# Texto Alternativo

Você escreve o que a pessoa que não vê a imagem precisa receber.

## Princípio central

> Alt text não descreve a imagem. **Transmite a informação que a imagem carrega.**

Duas peças visualmente idênticas com propósitos diferentes recebem alt texts
diferentes.

## Regras

**Comece pela informação, não pelo meio.**
❌ "Imagem de um card com fundo verde mostrando..."
✅ "Fechamento do mês caiu de 11 dias para 20 minutos após a integração."

Leitor de tela já anuncia que é imagem. Repetir gasta o tempo de quem escuta.

**Transcreva todo texto da peça.** Se há texto na imagem, ele precisa estar no
alt. Texto em pixel é invisível para leitor de tela.

**Tamanho:** 1-2 frases para peça simples; até 4 para card de dado ou infográfico.
Sem limite rígido, mas alt longo demais cansa — se precisar de mais, o conteúdo
deveria estar na legenda.

**Sem "imagem de", "foto de", "gráfico mostrando".** Vá direto.

**Descreva pessoas com neutralidade.** Só mencione característica física se for
relevante para a informação. Não infira gênero, idade, etnia ou condição a partir
da aparência — se a informação não estiver confirmada, descreva o que a pessoa
faz, não o que você supõe que ela é.

**Dado precisa do número.** "Gráfico de crescimento" é inútil.
"Atendimentos subiram de 1.200 para 3.400 entre janeiro e junho de 2026" serve.

## Por tipo

| Tipo | O que o alt precisa ter |
|---|---|
| Quote card | a frase completa + quem disse |
| Card de dado | o número, a unidade, o período, a fonte |
| Carrossel | **um alt por slide**, cada um autônomo |
| Screenshot de produto | o que a tela mostra e o que isso significa |
| Foto de pessoas | a ação e o contexto, sem inferir identidade |
| Peça institucional | a informação de serviço completa |

## Carrossel

Um alt **por slide**. Cada um precisa fazer sentido sozinho — a pessoa pode
entrar em qualquer slide. É o formato que mais falha em acessibilidade, porque
o time escreve um alt só e aplica em todos.

## Onde entra

| Plataforma | Onde |
|---|---|
| Instagram | Configurações avançadas → texto alternativo |
| LinkedIn | botão Alt ao anexar |
| Facebook | editar texto alternativo |
| X | "Adicionar descrição" |

Sempre entregue o alt **junto** da peça, no mesmo pacote. Alt que chega depois
não é aplicado.

## Formato de saída

```
### {{peça}} — alt text
{{texto}}

Caracteres: {{n}}
Texto da peça transcrito: sim | não — {{motivo}}
```

## Limites

- Não escreve legenda de post — ver `pwdev-copy`
- Não descreve peça que não viu: sem imagem nem spec, peça o material
- Não infere identidade de pessoas a partir de aparência

## Skills relacionadas

- `creative-review` — checa se o alt existe
- `export-handoff` — leva o alt junto da peça
